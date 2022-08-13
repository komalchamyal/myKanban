from werkzeug.exceptions import HTTPException
from flask import make_response
import json



class DateError(HTTPException):
    def __init__(self):
        data = { "error_code" : "T002", "error_message": "Incorrect date format, should be YYYY-MM-DD" }
        self.response = make_response(json.dumps(data), 406)

class UserNotFoundError(HTTPException):
    def __init__(self):
        data = { "error_code" : "L001", "error_message": "User not found" }
        self.response = make_response(json.dumps(data), 404)

class ListNotFoundError(HTTPException):
    def __init__(self):
        data = { "error_code" : "L002", "error_message": "List not found" }
        self.response = make_response(json.dumps(data), 404)

class TaskNotFoundError(HTTPException):
    def __init__(self):
        data = { "error_code" : "T001", "error_message": "Task not found" }
        self.response = make_response(json.dumps(data), 404)
