from flask import flash, redirect, render_template, request, url_for, session,g
from datetime import date, datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':30})
from app import app
from model import *

now=str(date.today())

#login controllers
@app.route('/', methods=['GET','POST'])
def login(): 
    if(request.method=='POST'):
        session.pop('user', None)
        if(request.form['btn']=='login'):
            id=request.form["userid"]
            user= User.query.filter_by(user_id=id).first()
            if user:
                if request.form['pswd']==user.password:
                    session['user'] = id
                    return redirect(url_for("home", name=id))
                else: 
                    flash("Incorrect Password!")
            else:
                flash("UserID not registered!")
        else:
            if(request.form['btn']=='register'):
                id=request.form["userid"]
                pswd=request.form["pswd"]
                email=request.form["email"]
                user= User.query.filter_by(user_id=id).first()
                mail= User.query.filter_by(email=email).first()
                if user:
                    flash("User already exists!")
                if email:
                    flash("Email already registered with a user!")
                if not (user or mail):
                    new=User(user_id=id,password=pswd, email=email)
                    db.session.add(new)
                    db.session.commit()
                    flash("User successfully registered!")  
    return render_template('index.html')

@app.before_request
def before_requests():
    
    g.user = None
    if "user" in session:
        g.user=session['user']

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

#list controllers
@app.route("/board/<name>", methods=['GET','POST'])
def home(name):
    if g.user==name:
        lists=List.query.filter_by(user_id=name).all()
        return render_template("board.html", name=name, lists=lists)
    else:
        return redirect(url_for("login"))

@app.route("/board/<name>/addlist", methods=['GET','POST'])
def addlist(name):
    if (request.method=="POST"):
        new_list=List(list_title=request.form['listname'],desc=request.form['desc'],user_id=name)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("home",name=name))
    return render_template("addlist.html", name=name)

@app.route("/board/<name>/<listid>/editlist", methods=['GET','POST'])
def editlist(name,listid):
    list=List.query.filter_by(list_id=listid).first()
    if (request.method=="POST"):
        list.list_title=request.form['listname']
        list.desc=request.form['desc']
        db.session.commit()
        return redirect(url_for('home',name=name))
    return render_template("editlist.html", name=name, list=list )

@app.route("/board/<name>/<listid>/deletelist")
def deletelist(name,listid):
    list=List.query.filter_by(list_id=listid).first()
    for task in list.tasks:
        db.session.delete(task)
    db.session.delete(list)
    db.session.commit()
    return redirect(url_for('home',name=name))

#task controllers
@app.route("/board/<name>/<listid>/addtask", methods=['GET','POST'])
def addtask(name,listid):
    user= User.query.filter_by(user_id=name).first()
    if (request.method=="POST"):
        task= Task(user_id=name, list_id=request.form['listid'], 
                    task_title=request.form['title'] ,
                    task_desc=request.form['desc'], 
                    deadline=request.form['deadline'], 
                    completed=request.form.get('completed'))
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("home",name=name))
    return render_template("addtask.html", name=name, lists=user.lists, listid=int(listid), now=now)

@app.route("/board/<name>/taskcompleted/<taskid>")
def completed(name,taskid):
    task= Task.query.filter_by(task_id=taskid).first()
    if task.completed:
        task.completed= ""
    else:
        task.completed=now
    db.session.commit()
    return redirect(url_for('home',name=name))

@app.route("/board/<name>/<listid>/<taskid>/edittask", methods=['GET','POST'])
def edittask(name,listid,taskid):
    user= User.query.filter_by(user_id=name).first()
    task= Task.query.filter_by(task_id=taskid).first()
    if (request.method=="POST"):
        task.list_id=request.form['chosenlist']
        task.task_title=request.form['title']
        task.task_desc=request.form['desc']
        task.deadline=request.form['deadline']
        task.completed=request.form.get('completed')
        db.session.commit()
        return redirect(url_for("home",name=name))
    return render_template("edittask.html", name=name, lists=user.lists, listid=int(listid), task=task, now=now)

@app.route("/board/<name>/<taskid>/deletetask")
def deletetask(name,taskid):
    task=Task.query.filter_by(task_id=taskid).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home',name=name))

#summary controller
@app.route("/board/<name>/summary")
def summary(name):
    user= User.query.filter_by(user_id=name).first()
    lists=user.lists

    #for bar graph
    data2= dict()
    completed=[] #for front end checking and not displaying the bar chart where no tasks are completed

    for list in lists:
        if len(list.tasks)>0:
            if list.list_id not in data2.keys():
                data2[list.list_id]={}
            for task in list.tasks:
                completed_date=task.completed
                if completed_date:
                    completed.append(list.list_id)
                    if completed_date not in data2[list.list_id].keys():
                        data2[list.list_id][completed_date]=1
                    else:
                        data2[list.list_id][completed_date]+=1
    
    for i in data2.keys():
        x= data2[i].keys()
        y= data2[i].values()
        plt.bar(x,y, color='green', width=0.6)
        plt.tight_layout()
        plt.savefig(f"static/images/{i}bar.png",
            bbox_inches ="tight",
            pad_inches = 1,
            transparent = True,)
        plt.cla()
        plt.clf()

    #for pie chart
    data= dict()

    for list in lists:
        if len(list.tasks)>0:
            if list.list_id not in data.keys():
                data[list.list_id]={"completed":0, "passed_deadline":0, "due":0}
            for task in list.tasks:
                if task.completed:
                    data[list.list_id]['completed']+=1
                else:
                    diff= datetime.strptime(now, "%Y-%m-%d")-datetime.strptime(task.deadline, "%Y-%m-%d")
                    if diff.days <= 0:
                        data[list.list_id]['due']+=1
                    else:
                        data[list.list_id]['passed_deadline']+=1

    for i in data.keys():
        y1=data[i]['completed']
        y2=data[i]['due']
        y3=data[i]['passed_deadline']
        
        x=["Completed", "Due", "Deadline Passed"]
        y=[y1,y2,y3]
        colors = ['#99ff99', '#ffcc99', '#ff6666']
        explode = (0.06,0.03,0.03)

        fig = plt.figure(figsize =(10, 7))
        # autopct=lambda p: '{:.1f}%'.format(round(p)) if p > 0 else '',
        plt.pie(y, colors=colors, explode=explode , shadow=True, startangle=90, textprops={'fontsize': 40})
        plt.tight_layout()
        plt.savefig(f"static/images/{i}pie.png",
            bbox_inches ="tight",
            pad_inches = 1,
            transparent = True,)            
        plt.cla()
        plt.clf()
        
    return render_template("summary.html", name=name, lists=lists, data=data, completed=completed)
