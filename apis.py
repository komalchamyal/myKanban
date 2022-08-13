from flask import jsonify
from model import *
from app import app
from flask_restful import Api, Resource, marshal_with, fields, reqparse
from validation import *
from datetime import datetime

api= Api(app)

############################################### ListAPI ##########################################################

#ListAPI Parsers
new_list_parser= reqparse.RequestParser()
new_list_parser.add_argument("list_title",None,required=True, help="List Name is required")
new_list_parser.add_argument("desc",None)

update_list_parser= reqparse.RequestParser()
update_list_parser.add_argument("list_id",None,type=int,required=True, help="List ID is required")
update_list_parser.add_argument("desc",None)
update_list_parser.add_argument("list_title",None)

delete_list_parser= reqparse.RequestParser()
delete_list_parser.add_argument("list_id", None, required=True, help="List ID required to delete it")

list_response={
    "list_id": fields.Integer,
    "list_title": fields.String,
    "desc": fields.String
}

#LIST CRUD API
class ListAPI(Resource):
    @marshal_with(list_response)
    def get(self,username):
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            lists=List.query.filter_by(user_id=username).all()
            return lists, 200
        else: 
            raise UserNotFoundError

    def post(self,username):
        args= new_list_parser.parse_args()
        listname= args.get("list_title",None)
        listdesc= args.get("desc",None)
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            newlist= List(user_id=username, list_title=listname,desc=listdesc)
            db.session.add(newlist)
            db.session.commit()
        else:
            raise UserNotFoundError
        return "Added Successfuly", 201
    
    def put(self,username):
        args= update_list_parser.parse_args()
        listid= args.get("list_id",None)
        new_listdesc= args.get("desc",None)
        new_listname=args.get("list_title", None)
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list= List.query.filter_by(list_id=listid).first()
            if valid_list:
                if new_listname: valid_list.list_title=new_listname
                if new_listdesc: valid_list.desc= new_listdesc
                db.session.commit()
            else:
                raise ListNotFoundError
        else:
            raise UserNotFoundError
        return "Updated Successfuly", 202

    def delete(self,username):
        args= delete_list_parser.parse_args()
        listid=args.get("list_id", None)
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list= List.query.filter_by(list_id=listid).first()
            if valid_list:
                #delete all tasks in that list first, if present
                if valid_list.tasks:
                    for task in valid_list.tasks:
                        db.session.delete(task)
                db.session.delete(valid_list)
                db.session.commit()
            else:
                raise ListNotFoundError
        else:
            raise UserNotFoundError
        return "Deleted Successfuly", 200

#ListAPI endpoint
api.add_resource(ListAPI,"/api/list/<string:username>")

############################################### TaskAPI ##########################################################

#TaskAPI Parsers
new_task_parser= reqparse.RequestParser(bundle_errors=True)
new_task_parser.add_argument("task_title",None,required=True, help="Task Name is required")
new_task_parser.add_argument("task_desc",None)
new_task_parser.add_argument("deadline",None, required=True, help="Deadline required (YYYY-MM-DD)")
new_task_parser.add_argument("completed",None, help="Date of Completion")

update_task_parser= reqparse.RequestParser()
update_task_parser.add_argument("task_id", type=int, required=True, help="Task ID is required")
update_task_parser.add_argument("task_title",None, help="Task Name")
update_task_parser.add_argument("task_desc",None, help="Task Description")
update_task_parser.add_argument("deadline",None, help="Deadline format (YYYY-MM-DD)")
update_task_parser.add_argument("completed",None, help="Date of Completion")

delete_task_parser= reqparse.RequestParser()
delete_task_parser.add_argument("task_id", required=True, help="Task ID required to delete it")

task_response={
    "task_id": fields.Integer,
    "task_title": fields.String,
    "task_desc": fields.String,
    "deadline": fields.String,
    "completed": fields.String
}

#function to validate date as per YYYY-MM-DD format
def validateDate(date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            raise DateError

#Task CRUD API
class TaskAPI(Resource):

    @marshal_with(task_response)
    def get(self,username,listid):
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list=List.query.filter_by(list_id=listid).first()
            if valid_list:
                return valid_list.tasks, 200
            else:
                raise ListNotFoundError
        else: 
            raise UserNotFoundError

    def post(self,username,listid):
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list=List.query.filter_by(list_id=listid).first()
            if valid_list:
                args= new_task_parser.parse_args()
                task_title= args.get("task_title", None)
                task_desc= args.get("task_desc", None)
                deadline= args.get("deadline", None)
                completed= args.get("completed", None)
                validateDate(deadline)
                if completed: validateDate(completed)
                newtask= Task(user_id=username, list_id=listid, task_title=task_title, 
                task_desc=task_desc, deadline=deadline, completed=completed)
                db.session.add(newtask)
                db.session.commit()
            else:
                raise ListNotFoundError
        else: 
            raise UserNotFoundError
        return "Added Task Successfully!", 201

    def put(self,username,listid):
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list=List.query.filter_by(list_id=listid).first()
            if valid_list:
                args= update_task_parser.parse_args()
                task_id= args.get("task_id")
                valid_task= Task.query.filter_by(task_id=task_id).first()
                if valid_task:
                    task_title= args.get("task_title", None)
                    task_desc= args.get("task_desc", None)
                    deadline= args.get("deadline", None)
                    completed= args.get("completed", None)
                    if task_title:
                        valid_task.task_title= task_title
                    if task_desc:
                        valid_task.task_desc= task_desc
                    if deadline: 
                        validateDate(deadline)
                        valid_task.deadline= deadline
                    if completed: 
                        validateDate(completed)
                        valid_task.completed=completed
                    db.session.commit()
                else:
                    raise TaskNotFoundError
            else:
                raise ListNotFoundError
        else: 
            raise UserNotFoundError
        return "Updated Task Successfully!", 202

    def delete(self, username, listid):
        valid_user= User.query.filter_by(user_id=username).first()
        if valid_user:
            valid_list=List.query.filter_by(list_id=listid).first()
            if valid_list:
                args= delete_task_parser.parse_args()
                task_id= args.get("task_id")
                task=Task.query.filter_by(task_id=task_id).first()
                if task:
                    db.session.delete(task)
                    db.session.commit()
                else:
                    raise TaskNotFoundError
            else:
                raise ListNotFoundError
        else: 
            raise UserNotFoundError
        return "Deleted Task Successfully"

#TaskAPI endpoint
api.add_resource(TaskAPI, "/api/task/<string:username>/<int:listid>")