from flask import Flask, request, render_template

from top import employees, activeWorkstations, currentJobs, cursor, conn, ipaddrs,SQLQueries
from datetime import datetime
import pyodbc

app = Flask(__name__)


class workStation:
    def __init__(self, name, currentJob, currentemployees):
        self.name = name
        self.currentJob = currentJob
        self.employees = currentemployees


class Job:
    def __init__(self, jobid, start):
        self.id = jobid
        self.start = start

    def finalwritetodb(self):
        if self.id == '':
            return

        cursor.execute("UPDATE TrackLaborJob SET DateFinish=? where Job=? AND Datestart=?",
                       datetime.utcnow(), self.id, self.start)
        conn.commit()

    def beginwritetodb(self, ws):
        if self.id == '':
            return

        cursor = conn.cursor()
        cursor.execute("insert into TrackLaborJob(Job, Datestart, DateFinish, Station) values (?,?,?,?)",
                       self.id,
                       self.start, datetime.utcnow(), ws.name)
        conn.commit()


'''
 Employee object has a name and start time
 Employee.writetodb writes the closing entry for an employee into the database
 Employee.restartclock restarts the clock for an employee when a new job is starte
'''


class Employee:
    def __init__(self, name, start):
        self.name = name
        self.start = start

    def writetodb(self, ws):
        if ws.currentJob.id == '':
            return

        cursor.execute(
            "insert into TrackLaborEmployee(EmployeeName, Job, Datestart, DateFinish, Station) values (?,?,?,?,?)",
            self.name, ws.currentJob.id, self.start, datetime.utcnow(), ws.name)
        conn.commit()

    def restartclock(self):
        self.start = datetime.utcnow()


@app.errorhandler(500)
@app.route('/labor/tracking', methods=['GET', 'POST'])
def mainloop():
    message = ''
    if request.access_route[0] not in ipaddrs:
        return "OOPS! Please report this number to the system admin" + request.access_route[0]
    currentWorkStation = workStation(ipaddrs[request.access_route[0]], Job('', ''), [])

    wsnew = True
    for workstation in activeWorkstations:
        if workstation.name == currentWorkStation.name:
            currentWorkStation = workstation
            wsnew = False
            break

    if wsnew:  # todo this is the wrong statement it should check to see if it is in the list
        activeWorkstations.append(currentWorkStation)

    if request.method == 'GET':
        if currentWorkStation.currentJob.id == '' or currentWorkStation.employees == []:
            stat = 'OFF'
        else:
            stat = 'ON'
        job = {'number': currentWorkStation.currentJob.id, 'status': stat, 'time': currentWorkStation.currentJob.start}

        current_employees = []
        for employee in currentWorkStation.employees:
            current_employees.append({'name': employee.name, 'time': employee.start})
        return render_template('Workstation.html', job=job, employees=current_employees, message=message)

    if request.method == 'POST':
        mscan = request.form['scan']

        # if scan is a job
        if mscan[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # if scan job is the current job
            if currentWorkStation.currentJob.id == mscan:
                # sign everyone out and finish job
                for employee in currentWorkStation.employees:
                    employee.writetodb(currentWorkStation)
                    employee.start = ''

                currentWorkStation.currentJob.finalwritetodb()
                currentJobs.remove(currentWorkStation.currentJob)
                currentWorkStation.currentJob = Job('', '')
            # else close old job and start new job
            else:
                for employee in currentWorkStation.employees:
                    employee.writetodb(currentWorkStation)
                    employee.restartclock()
                currentWorkStation.currentJob.finalwritetodb()
                if currentWorkStation.employees == []:
                    currentWorkStation.currentJob = Job(mscan, '')
                else:
                    currentWorkStation.currentJob = Job(mscan, datetime.utcnow())
                    currentWorkStation.currentJob.beginwritetodb(currentWorkStation)

                currentJobs.append(currentWorkStation.currentJob)

        # scan is an employee
        else:
            newemployee = True  # Temporary to see if scan is a new employee to the job

            # check to see if the employee is already on the job and close and remove employee if true
            for employee in currentWorkStation.employees:
                if employee.name == mscan:
                    employee.writetodb(currentWorkStation)
                    currentWorkStation.employees.remove(employee)
                    employees.remove(employee)
                    if currentWorkStation.employees == []:
                        currentWorkStation.currentJob.finalwritetodb()
                        currentWorkStation.currentJob.start = ''
                    newemployee = False
            for employee in employees:
                if employee.name == mscan:
                    message = "Operator Logged in to another station"
                    newemployee = False

            # else add employee to list
            if newemployee:
                newemp = Employee(mscan, datetime.utcnow())
                if currentWorkStation.employees == [] and not (currentWorkStation.currentJob.id == ''):
                    currentWorkStation.currentJob.start = datetime.utcnow()
                    currentWorkStation.currentJob.beginwritetodb(currentWorkStation)
                currentWorkStation.employees.append(newemp)
                employees.append(newemp)
        if currentWorkStation.currentJob.id == '' or currentWorkStation.employees == []:
            stat = 'OFF'
        else:
            stat = 'ON'
        job = {'number': currentWorkStation.currentJob.id, 'status': stat, 'time': currentWorkStation.currentJob.start}

        current_employees = []
        for employee in currentWorkStation.employees:
            current_employees.append({'name': employee.name, 'time': employee.start})
        return render_template('Workstation.html', job=job, employees=current_employees, message=message)


@app.route('/labor/view', methods=['GET', 'POST'])
def main_view():
    return render_template("View.html", workstations=activeWorkstations)


class SubJob:
    def __init__(self, starttime, endtime, totaltime, manhours, stations):
        self.starttime = starttime
        self.endtime = endtime
        self.totaltime = totaltime
        self.manhours = manhours
        self.stations = stations


class Station:
    def __init__(self, starttime, endtime, totaltime, manhours):
        self.starttime = starttime
        self.endtime = endtime
        self.totaltime = totaltime
        self.manhours = manhours


@app.route('/labor/totals', methods=['GET', 'POST'])
def totals_view():
    # todo: get active jobs and run their totals etc
    SQLwhere = " WHERE Complete = 'N' "
    if request.method == 'POST':
        if request.form['filter'] == 'Job':
            SQLwhere = " WHERE WipMaster.Job > " + request.form['From'] + " and WipMaster.Job < " + request.form['To'] + " "
        elif request.form['filter'] == 'Date':
            SQLwhere = " WHERE WipMaster.JobStartDate > " + request.form['From'] + " and WipMaster.JobStartDate < " + request.form['To'] + " "

    masterjobs = {}

    cursor.execute(SQLQueries['masterJob-totaltime'] + SQLwhere + SQLQueries['masterJob-group'])
    masterjobs_total = cursor.fetchall()
    cursor.execute(SQLQueries['masterJob-manhours'] + SQLwhere + SQLQueries['masterJob-group'])
    masterjobs_manhr = cursor.fetchall()
    # print(masterjobs_total)
    for masterjob in masterjobs_total:
        # print(masterjob.MasterJob)
        SQLwhere2 = " and MasterJob like '" + masterjob[0] + "' "
        cursor.execute(SQLQueries['subJob-totaltime'] + SQLwhere + SQLwhere2 + SQLQueries['subJob-group'])
        # print([column[0] for column in cursor.description])
        subjobs_total = cursor.fetchall()
        cursor.execute(SQLQueries['subJob-manhours'] + SQLwhere + SQLwhere2 + SQLQueries['subJob-group'])
        subjobs_manhr = cursor.fetchall()

        subjobs = {}
        mh = 0
        for s in masterjobs_manhr:
            if s[0] == masterjobs_total[0]:
                mh = s[1]
        subjobs[masterjob[0]] = SubJob(masterjob[2], masterjob[3], masterjob[1], mh, {})

        for subjob in subjobs_total:
            SQLwhere3 = " and WipMaster.Job like '" + subjob[0] + "' "
            cursor.execute(SQLQueries['station-totaltime'] + SQLwhere + SQLwhere2 + SQLwhere3 + SQLQueries['station-group'])
            station_total = cursor.fetchall()
            cursor.execute(SQLQueries['station-manhours'] + SQLwhere + SQLwhere2 + SQLwhere3 + SQLQueries['station-group'])
            station_manhr = cursor.fetchall()
            stations = {}
            for station in station_total:
                mh = 0
                for s in station_manhr:
                    if s[0] == station[0]:
                        mh = s[2]
                stations[station[2]] = Station(station[4], station[5], station[3], mh)
            mh = 0
            for s in subjobs_manhr:
                if s[0] == subjob[0]:
                    mh = s[1]
            subjobs[subjob[0]] = SubJob(subjob[2], subjob[3], subjob[1], mh, stations)
        masterjobs[masterjob[0]] = subjobs
    print(masterjobs)
    # masterjobs = {'123456': {'123456': subJob('start time 1', 'end time 1', 'total time 1', 'manhours 1',
    #                                           {'fab1': station('start time 11', 'end time 11', 'total time 11', 'manhours 11')}),
    #                          '123457': subJob('start time 2', 'end time 2', 'total time 2', 'manhours 2',
    #                                           {'fab3': station('start time 22', 'end time 22', 'total time 22', 'manhours 22'),
    #                                            'fab2': station('start time 11', 'end time 11', 'total time 11', 'manhours 11')}),
    #                          '123458': subJob('start time 3', 'end time 3', 'total time 3', 'manhours 3',
    #                                           {'fab4': station('start time 33', 'end time 33', 'total time 33', 'manhours 33')})},
    #               '234567': {'234567': subJob('start time 1', 'end time 1', 'total time 1', 'manhours 1',
    #                                           {'fab1': station('start time 11', 'end time 11', 'total time 11', 'manhours 11'),
    #                                            'fab2': station('start time 11', 'end time 11', 'total time 11', 'manhours 11')}),
    #                          '234568': subJob('start time 2', 'end time 2', 'total time 2', 'manhours 2',
    #                                           {'fab3': station('start time 22', 'end time 22', 'total time 22', 'manhours 22')}),
    #                          '234569': subJob('start time 3', 'end time 3', 'total time 3', 'manhours 3',
    #                                           {'fab4': station('start time 33', 'end time 33', 'total time 33', 'manhours 33')})}}
    return render_template("Totals.html", masterjobs=masterjobs)

if __name__ == '__main__':
    conn = pyodbc.connect(
        'DRIVER={FreeTds};SERVER=cti-syspro.local.citytheatrical.com;PORT=51845;DATABASE=SysproCompanyC;UID=CITY\\gmercado;\
        PWD=01189998819991197253;TDS_Version=8.0')
    cursor = conn.cursor()

    app.run(host='0.0.0.0')
    # app.run()
