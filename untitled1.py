from flask import Flask, request, render_template

import socket
from top import employees, activeWorkstations, currentJobs, cursor, conn, ipaddrs
from datetime import datetime, timedelta
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


@app.route('/labor/tracking', methods=['GET', 'POST'])
def mainloop():
    if request.access_route[0] not in ipaddrs:
        return "OOPS! Please report this number to the system admin" + request.access_route[0]
    currentWorkStation = workStation(ipaddrs[request.access_route[0]], Job('', ''), [])

    for workstation in activeWorkstations:
        if workstation.name == currentWorkStation.name:
            currentWorkStation = workstation
            break

    if activeWorkstations == []:
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
        return render_template('Workstation.html', job=job, employees=current_employees)

    if request.method == 'POST':
        mscan = request.form['scan']

        # if scan is a job
        if mscan[0] == '0' or mscan[0] == '1' or mscan[0] == '2' or mscan[0] == '3' or mscan[0] == '4' or mscan[
            0] == '5' \
                or mscan[0] == '6' or mscan[0] == '7' or mscan[0] == '8' or mscan[0] == '9':
            # if scan job is the current job
            if currentWorkStation.currentJob.id == mscan:
                # sign everyone out and finish job
                for employee in currentWorkStation.employees:
                    employee.writetodb(currentWorkStation)
                currentWorkStation.clear()
                currentWorkStation.currentJob.finalwritetodb()
                currentJobs.remove(currentWorkStation.currentJob)
                currentWorkStation.currentJob = Job('', '')
            # else close old job and start new job
            else:
                for employee in currentWorkStation.employees:
                    employee.writetodb(currentWorkStation)
                    employee.restartclock()
                currentWorkStation.currentJob.finalwritetodb()
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
                    newemployee = False
            for employee in employees:
                if employee.name == mscan:
                    message = "Operator Logged in to another station"
                    newemployee = False

            # else add employee to list
            if newemployee:
                newemp = Employee(mscan, datetime.utcnow())
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
        return render_template('Workstation.html', job=job, employees=current_employees)

if __name__ == '__main__':
    conn = pyodbc.connect(
        'DRIVER={FreeTds};SERVER=SHIPPER.local.citytheatrical.com;PORT=50180;DATABASE=LaborTracking;UID=CITY\\gmercado;\
        PWD=01189998819991197253;TDS_Version=8.0')
    cursor = conn.cursor()

    app.run(host='0.0.0.0')
    #app.run()
