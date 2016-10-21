from flask import Flask, request, render_template
#import pyodbc
from datetime import datetime, timedelta
app = Flask(__name__)

# conn = pyodbc.connect(
#     'DRIVER={SQL Server};;SERVER=cti-syspro.local.citytheatrical.com;PORT=51845;DATABASE=SysproCompanyZ;UID=CITY\gmercado;PWD=01189998819991197253')
#
# cursor = conn.cursor()


@app.route('/labor/tracking', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        job = {'number': '00058954', 'status': 'ON', 'time': datetime.now()}
        employees = [{'name': 'Greg', 'time': datetime.now()}]
        return render_template('Workstation.html', job=job, employees=employees)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
