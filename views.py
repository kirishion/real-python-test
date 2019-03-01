from flask import Flask, redirect, render_template, g, request, url_for, session, flash
# import sqlite3 removed by sqlalchemy
from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm

from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask('__name__')
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User


#def db_connect(): removed by sqlalchemy
    #return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap



@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('Goodbye')
    return redirect(url_for('login'))



@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome')
                return redirect(url_for('tasks'))
            else:
                error = "Invalid Username or password"
        else:
            error = "Both fields are required"

    return render_template('login.html', form=form, error=error)


@app.route('/tasks/')
@login_required
def tasks():
    """g.db = db_connect()
    cursor = g.db.execute(
        'SELECT name, due_date, priority, task_id from tasks where status = 1 ORDER BY priority')

    open_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2],
             task_id=row[3]) for row in cursor.fetchall()]"""

    open_tasks = db.session.query(Task) \
        .filter_by(status=1).order_by(Task.due_date.asc())

    """cursor = g.db.execute(
        'SELECT name, due_date, priority, task_id from tasks where status = 0')

    closed_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2],
             task_id=row[3]) for row in cursor.fetchall()]"""

    closed_tasks = db.session.query(Task) \
        .filter_by(status=0).order_by(Task.due_date.asc())

    #g.db.close()

    return render_template(
        'tasks.html', form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks)

@app.route('/add/', methods=['GET', 'POST'])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                datetime.datetime.utcnow(),
                form.priority.data,
                '1',
                session['user_id']
            )

            db.session.add(new_task)
            db.session.commit()
            flash('New entry has been posted')

    return redirect(url_for('tasks'))

"""    if not name or not date or not priority:
        flash('All fields are requeired')
        return redirect(url_for('tasks'))
    else:
        g.db.execute('INSERT INTO tasks (name, due_date, priority, status) \
                     VALUES (?,?,?,?)', [
            request.form['name'],
            request.form['due_date'],
            request.form['priority'],
            1
        ]
                     )
        g.db.commit()
        g.db.close()"""



@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    """g.db = db_connect()
    g.db.execute(
        'UPDATE tasks set status = 0 WHERE task_id='+str(task_id))
    g.db.commit()
    g.db.close()"""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({'status': '0'})
    db.session.commit()
    flash("Task has been updated")
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete(task_id):
    """g.db = db_connect()
    g.db.execute(
        'DELETE FROM tasks where task_id='+str(task_id)
    )
    g.db.commit()
    g.db.close()"""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash("Task has been deleted")
    return redirect(url_for('tasks'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User has been added")
            return redirect(url_for('login'))
    return render_template('register.html', form=form, error=error)

