from flask import Flask, render_template, session, request, flash, redirect, url_for
from lib.config import *
from lib import functions as fcn
from functools import wraps


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def main():
	return render_template('index.html')

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('you need to login first.')
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if is_admin():
            return f(*args,**kwargs)
        else:
            return redirect(url_for('permission_error'))
    return wrap
    
def session_initialization(isadmin,username):
    if isadmin == True:                               #if the user is admininstrator
        session['logged_in'] = True
        session['user'] = username
        session['role'] = 'admin'
    else:                                               #if the user is a regular user 
        session['logged_in'] = True           
        session['user'] = username
        session['role'] = 'user'
def session_kill():
    session.pop('logged_in',None)
    session.pop('user',None)
    session.pop('role',None)
    PROJECT_TITLE = None

def is_admin():
    role = session['role']
    if role =='admin':
        return True
    else:
        return False

@app.route('/login', methods = ['POST','GET'])
def login():
    error = None
    session_kill()
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        result = fcn.fetch_username_and_password(username,password)
        if result[0] !=True:
            error = 'incorrect credentials'
        else:
            session_initialization(result[1],username)
    if 'logged_in' in session:
        if is_admin():
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user_panel'))
    else:
        return render_template('login.html', error = error)

@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin.html')

'''logout route '''

@app.route("/logout")
def logout():
    session_kill()
    flash('you are logged out successfully!')
    return redirect(url_for('login'))

'''create a user in system page '''

@app.route('/adduser', methods = ['GET','POST'])
@login_required
@admin_required
def define_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    else:
        fcn.hashing_and_save(request.form.items())
        flash('User added successfuly!')
        return render_template('add_user.html')

@app.route('/user_panel')
@login_required
def user_panel():
	return render_template('user_panel.html')



if __name__ == '__main__':
	app.debug = True
	app.run()

