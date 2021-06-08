#!flask/bin/python
from flask import Flask
from flask import request
from flask import redirect as fredirect
import time
import MySQLdb

app = Flask(__name__)

myDB = "172.16.3.231"

@app.route('/objects', methods=['POST'])
def add_object():  # noqa: E501
    return redirect(request, getMonitorIP())


@app.route('/objects/<path:text>', methods=['DELETE'])
def delete_object(text):  # noqa: E501
    return redirect(request, getMonitorIP())


@app.route('/objects/<path:text>', methods=['GET'])
def get_object_by_name(text):  # noqa: E501
    return redirect(request, getMonitorIP())


@app.route('/status', methods=['GET'])
def get_status():  # noqa: E501
    return redirect(request, getMonitorIP())


@app.route('/objects', methods=['GET'])
def retrieve_list():  # noqa: E501
    return redirect(request, getMonitorIP())


def getMonitorIP():
    mydb = MySQLdb.connect(host=myDB, user="root", passwd="password", db="ipaddresses")
    mycursor = mydb.cursor()
    sql = "SELECT address FROM ipaddresses.addresses;"
    mycursor.execute(sql)
    monitor_IPs = mycursor.fetchall()
    mycursor.close()
    timestamp = time.time()
    return monitor_IPs[hash(timestamp) % len(monitor_IPs)][0]


def redirect(request, ip):
    return fredirect('http://{}:8080/{}'.format(ip, request.path), code=307)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


