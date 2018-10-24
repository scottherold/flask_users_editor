from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import datetime
import re
app = Flask(__name__)
app.secret_key = 'shhhDontTell'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def boot_up():
    return redirect('/users')

@app.route('/users', methods=['GET'])
def index():
    mysql = connectToMySQL("rest_users_db")
    all_users = mysql.query_db("SELECT user_id, first_name, last_name, email, DATE_FORMAT(created_at, '%m/%d/%Y %h:%i %p') AS created_at, DATE_FORMAT(updated_at, '%m/%d/%Y %h:%i %p') AS updated_at FROM users;")
    return render_template('index.html', all_users=all_users)

@app.route('/users/new', methods=['GET'])
def new():
    return render_template('new_user.html')

@app.route('/users/<id>/edit', methods=['GET'])
def edit_user(id):
    user_id = id
    mysql = connectToMySQL("rest_users_db")
    query = "SELECT user_id, first_name, last_name, email FROM users WHERE user_id=%(userid)s;"
    data = {
        'userid': user_id
    }
    user_info = mysql.query_db(query, data)
    return render_template('edit_user.html', user_info=user_info)

@app.route('/users/<id>/edit', methods=['POST'])
def post_edit(id):
    user_id = id
    mysql = connectToMySQL("rest_users_db")
    query = "SELECT email FROM users WHERE user_id<>%(userid)s;"
    data = {
        'userid': request.form['user_id']
    }
    duplicate_validation = mysql.query_db(query, data)
    count = 0
    duplicate = ""
    for email in duplicate_validation:
        if request.form['email'] == email['email']:
            duplicate = email['email']
    if len(request.form['email']) < 1:
        flash(u'Email is required!', 'email')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash(u'Invalid email!', 'email')
    elif request.form['email'] == duplicate:
        flash(u'The email ' + request.form['email'] + ' is already registered!', 'email')
    else:
        count += 1
        session['email'] = request.form['email']
    # Check first name#
    if len(request.form['first_name']) < 1:
        flash(u'First Name is required!', 'first_name')
    elif str.isalpha(request.form['first_name']) == False:
        flash(u'First Name must contain only alphanumeric characters!', 'first_name')
    else:
        count += 1
        session['first_name'] = request.form['first_name']
    # Check last name #
    if len(request.form['last_name']) < 1:
        flash(u'Last Name is required!', 'last_name')
    elif str.isalpha(request.form['last_name']) == False:
        flash(u'Last Name must contain only alphanumeric characters!', 'last_name')
    else:
        count += 1
    if count == 3:
        mysql = connectToMySQL("rest_users_db")
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, updated_at = NOW() WHERE user_id=%(userid)s;"
        data = {
            'userid': request.form['user_id'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']
        }        
        update_user = mysql.query_db(query, data)
        show_route = "/users/"+user_id
        return redirect(show_route)
    else:
        edit_route = "/users/"+user_id+"/edit"
        return redirect(edit_route)

@app.route('/users/create', methods=['POST'])
def create():
    mysql = connectToMySQL("rest_users_db")
    duplicate_validation = mysql.query_db("SELECT email FROM users")
    count = 0
    duplicate = ""
    for email in duplicate_validation:
        if request.form['email'] == email['email']:
            duplicate = email['email']
            print(duplicate_validation)
            print(duplicate)
    if len(request.form['email']) < 1:
        flash(u'Email is required!', 'email')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash(u'Invalid email!', 'email')
    elif request.form['email'] == duplicate:
        flash(u'The email ' + request.form['email'] + ' is already registered!', 'email')
    else:
        count += 1
        session['email'] = request.form['email']
    # Check first name#
    if len(request.form['first_name']) < 1:
        flash(u'First Name is required!', 'first_name')
    elif str.isalpha(request.form['first_name']) == False:
        flash(u'First Name must contain only alphanumeric characters!', 'first_name')
    else:
        count += 1
        session['first_name'] = request.form['first_name']
    # Check last name #
    if len(request.form['last_name']) < 1:
        flash(u'Last Name is required!', 'last_name')
    elif str.isalpha(request.form['last_name']) == False:
        flash(u'Last Name must contain only alphanumeric characters!', 'last_name')
    else:
        count += 1
    if count == 3:
        session['last_name'] = request.form['last_name']
        session['first_name'] = request.form['first_name']
        session['last_name'] = request.form['last_name']
        session['email'] = request.form['email']
        mysql = connectToMySQL("rest_users_db")
        query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUEs (%(first_name)s, %(last_name)s, %(email)s, NOW(), NOW());"
        data = {
            'first_name': session['first_name'],
            'last_name': session['last_name'],
            'email': session['email']
        }
        new_user = mysql.query_db(query, data)
        mysql = connectToMySQL("rest_users_db")
        query = "SELECT * FROM users WHERE email=%(email)s;"
        data = {
            'email': session['email']
        }
        query_data = mysql.query_db(query, data)
        for user in query_data:
            session['user_id'] = user['user_id']
        show_route = "/users/"+str(session['user_id'])
        return redirect(show_route)
    else:
        return redirect('/users/new')

@app.route('/users/<id>', methods=['GET'])
def show(id):
    user_id = id
    mysql = connectToMySQL("rest_users_db")
    query = "SELECT user_id, first_name, last_name, email, created_at, updated_at AS updated_at FROM users WHERE user_id=%(userid)s;"
    data = {
        'userid': user_id
    }
    user_info = mysql.query_db(query, data)
    return render_template('show_user.html', user_info=user_info)

@app.route('/users/<id>/destroy', methods=['GET'])
def destroy(id):
    user_id = id
    mysql = connectToMySQL("rest_users_db")
    query = "DELETE FROM users WHERE user_id=%(userid)s;"
    data = {
        'userid': user_id
    }
    delete_user_id = mysql.query_db(query, data)
    return redirect('/users')

if __name__=="__main__":
    app.run(debug=True)