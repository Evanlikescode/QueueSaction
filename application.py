from flask import Flask, request, render_template, redirect, request, session, url_for, make_response
from helper.action_method import AuthMethod
from helper.middleware import Middleware
from management import management_app
import os
application = Flask(__name__)
application.secret_key = os.getenv('SECRET_KEY')

action_method = AuthMethod()
middleware = Middleware()

application.register_blueprint(management_app, url_prefix='/management')


@application.route('/', methods=['POST', 'GET'])
def login():
    if middleware.is_login() == False:
        message = True
        if request.method == "POST":
            input_data = {
                "username": request.form['username'],
                "password": request.form['password']
            }
            data = action_method.login(input_data)
            print(data)
            if data != False:
                session['is_login'] = True
                session['id'] = data[0]
                session['username'] =  data[1]
                session['role'] = data[3]
                session['profile_picture'] = data[4]
                return redirect(url_for('management_app.main'))
            message = False
        return render_template('auth/login.html', message = message)
    return redirect(url_for('management_app.main'))


@application.route('/register', methods=['POST', 'GET'])
def register():
    if middleware.is_login() == False:
        message = True
        if request.method == "POST":
                input_data = {
                    "username": request.form['username'],
                    "password": request.form['password'],
                }
                if input_data.get("username") != '' and input_data.get('password') != '':
                    data = action_method.register(input_data)
                    if data != False:
                        session['is_login'] = True
                        session['id'] = data[0]
                        session['username'] =  data[1]
                        session['role'] = data[3]
                        session['profile_picture'] = data[4]
                        return redirect(url_for('management_app.main'))
                    message = False
        return render_template('auth/register.html', message=message)
    return redirect(url_for('management_app.main'))


@application.route('/logout', methods=['POST', 'GET'])
def logout():
    if middleware.is_login() != False:
        if session['is_login'] == True:
            session.pop('is_login', False)
            session.pop('id', None)
            session.pop('username', None)
            session.pop('role', None)
            session.pop('profile_picture', None)
            return redirect(url_for('login'))
        return redirect(url_for('management_app.main'))
    return redirect(url_for('login'))
    


if __name__ == "__main__":
    DEBUG_APP = "on"
    debuging = False
    if DEBUG_APP.lower() == 'on':
        debuging = True
    application.run(debug=debuging, port=8080)