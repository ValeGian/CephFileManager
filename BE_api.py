#!flask/bin/python
from flask import Flask
from flask import request

import BE_server as be

app = Flask(__name__)


@app.route('/objects', methods=['POST'])
def add_object():  # noqa: E501
    file = request.files['file']
    filename = file.filename
    filebody = file.read()
    parameter = {
        "filename": filename,
        "body": filebody
    }
    return be.handle_request("add", parameter)


@app.route('/objects/<path:text>', methods=['DELETE'])
def delete_object(text):  # noqa: E501
    return be.handle_request("delete", text)


@app.route('/objects/<path:text>', methods=['GET'])
def get_object_by_name(text):  # noqa: E501
    return be.handle_request("get", text)


@app.route('/status', methods=['GET'])
def get_status():  # noqa: E501
    return be.handle_request("get_status")


@app.route('/objects', methods=['GET'])
def retrieve_list():  # noqa: E501
    return be.handle_request("get_objects_list")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)