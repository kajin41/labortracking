from flask import Flask
import pyodbc
app = Flask(__name__)

conn = pyodbc.connect(
    'DRIVER={SQL Server};;SERVER=cti-syspro.local.citytheatrical.com;PORT=51845;DATABASE=SysproCompanyZ;UID=CITY\gmercado;PWD=01189998819991197253')

cursor = conn.cursor()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
