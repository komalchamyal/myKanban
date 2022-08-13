from app import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    lists = db.relationship("List", backref="user")

    def __repr__(self):
        return f"User {self.user_id}"

class List(db.Model):
    __tablename__ = 'list'
    list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_title = db.Column(db.String)
    desc = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey("user.user_id"))
    tasks = db.relationship("Task", backref="list")

    def __repr__(self):
        return f"List {self.list_title}: User {self.user_id}"

class Task(db.Model):
    __tablename__ = 'task'
    user_id = db.Column(db.String, db.ForeignKey("user.user_id"), nullable=False)
    list_id = db.Column(db.Integer,  db.ForeignKey("list.list_id"), nullable=False) 
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_title =  db.Column(db.String)
    task_desc = db.Column(db.String)
    deadline = db.Column(db.String)
    completed = db.Column(db.String)

    def __repr__(self):
        return f"Task {self.task_title}: List {self.list_title}"
