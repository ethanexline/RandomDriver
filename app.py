from flask import Flask, current_app, jsonify, make_response, request, abort, Response, redirect, session
from flask_login import LoginManager, logout_user, UserMixin, login_required, login_user
import pyodbc
import json
import hashlib
import string
import random
from datetime import datetime
from emailing import emailing
import re
from gevent.pywsgi import WSGIServer
from RandomDriverSubstance import RandomTest


#Create a flask app. DUH
app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = {REDACTED}
)

# flask-login manager. 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

##!!-- Start of Data structures/class objects.
#The test class object. Returns all test in this class object
class test:
    def __init__(self, date_, company_, test_type_, supportnet_number_, driver_code_, terminal_, name_, hire_date_, return_date_, id_, result_):
        self.date = date_
        self.company = company_
        self.supportnet_number = supportnet_number_
        self.test_type = test_type_
        self.driver_code = driver_code_
        self.terminal = terminal_
        self.name = name_
        self.hire_date = hire_date_
        self.return_date = return_date_
        self.id = id_
        self.result = result_

        #prettify the result.
        if self.result == 'P':
            self.result = 'PASS'
        elif self.result == 'F':
            self.result = 'FAIL'
        elif self.result == 'C':
            self.result = 'CANCEL'

#User object for Flask Login. I have noooo idea why it HAS to be like this.
class User_Login_Stat(UserMixin):
    def __init__(self, id_):
            self.id = id_

#User model for the thing.
class User(UserMixin):
    def __init__(self, id_, username, password, salt, last_login, role, account_status):
        self.id = id_
        self.username = username
        self.password = password
        self.salt = salt
        self.last_login = last_login
        self.role = role
        self.account_status = account_status

class excludedDriver():
     def __init__(self, driver_code_, id_):
        self.driver_code = driver_code_
        self.id = id_
        
##!!--End of data structures--!!##


##!!--Start of helper functions --!!##
##combine password and salt
def combine_password_salt(entered_password, salt):
    return hashlib.sha256((salt + entered_password).encode()).hexdigest()

##Generate a random salt string!
def salt_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#Create user. 
def create_user(user):

    salt = hashlib.sha256(salt_generator().encode())
    hashed_password = hashlib.sha256((str(salt.hexdigest()) + user.password).encode())

    conn = pyodbc.connect('Driver={SQL Server};'
                        'Server={REDACTED};'
                        'Database={REDACTED};'
                        'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        insert into 
        {REDACTED} 
        values(?,
        ?,
        ?,
        getdate(), 
        1,
        'A')
    
    '''

    cursor.execute(sql, user.username, str(hashed_password.hexdigest()), str(salt.hexdigest()))
    conn.commit()

    if cursor.rowcount == 1:
        return True
    else:
        return False

##Get user information based on entered username. SECURITY!
def get_user(username):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server={REDACTED};'
                      'Database={REDACTED};'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        select top 1 * 
        from {REDACTED}
        where {REDACTED} = ?
    
    '''

    cursor.execute(sql, username)
    users = cursor.fetchall()

    all_users = []
    for user in users:
        newuser = User(user[0],user[1], user[2], user[3], user[4], user[5], user[6])
        all_users.append(newuser)
    return all_users

#validate the password
def validate_password(password):
    if len(password) < 8:
        return False
    elif re.search('[0-9]',password) is None:
        return False
    elif re.search('[A-Z]',password) is None: 
        return False
    else:
        return True

#validate the username 
def validate_username(username):
    print(username)
    if len(username) < 8:
        return False
    else:
        return True

#record a user login        
def record_user_login():
    id_ = session['username_id']
    conn = pyodbc.connect('Driver={SQL Server};'
                    'Server={REDACTED};'
                    'Database={REDACTED};'
                    'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        update {REDACTED} 
        set {REDACTED} = getdate()
        where {REDACTED} = ?
    
    '''

    cursor.execute(sql, id_)
    conn.commit()

# handle login failed. Required by flask-login
@app.errorhandler(401)
def page_not_found(e):
    return redirect('/login?fail=true')
    
# callback to reload the user object. Again, required by flask-login      
@login_manager.user_loader
def load_user(userid):
    return User_Login_Stat(userid)  

##!!--End of helper functions--!!##



##!!-- Start of GUI routes --!!##
#Index Route
@app.route('/')
@login_required
def index_page():
    return current_app.send_static_file('index.html')

    #Login Route.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userDetails = get_user(username)
        if len(userDetails) > 0:
            if combine_password_salt(password, userDetails[0].salt) == userDetails[0].password:
                session['username_id'] = userDetails[0].id
                session['role'] = userDetails[0].role
                record_user_login()
                login_user(userDetails[0])
                return redirect('/')
            else:
                return abort(401)
        else:
            return abort(401)
    else:
        return current_app.send_static_file('login.html')


#Logout Route. Not really a GUI, but still here because this is the wey.
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('username_id', None)
    return redirect('/')

#historical page route
@app.route('/historical')
@login_required
def historical():
    return current_app.send_static_file('historical.html')

#historical page route
@app.route('/admin')
@login_required
def admin():
    if str(session['role']) == '1':
        return current_app.send_static_file('admin.html')
    else:
        return redirect('/?error=User Not Admin')

#historical page route
@app.route('/stats')
@login_required
def stats():
    return current_app.send_static_file('stats.html')

##!!-- END of GUI routes --!!##


##!!-- Start of API Routes --!!##
#Create user 
@app.route("/api/adduser", methods=["POST"])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_username(username) != True:
            return redirect('/admin?stat=false&error=Username does not meet requirements.')
        if validate_password(password) != True:
            return redirect('/admin?stat=false&error=Password does not meet requirements.')

        userDetails = get_user(username)
        if len(userDetails) == 0:
            user = User('',username, password, '','','','')
            stat = create_user(user)
            if stat == True:
                return redirect('/admin?stat=true&error=false')
            elif stat == False:
                return redirect('/admin?stat=false&error=database')
        else:
            return redirect('/admin?stat=false&error=Username already exists')

#Get open random drug/alcohol tests
@app.route('/api/getexcludeddrivers')
@login_required
def get_excluded_drivers():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server={REDACTED};'
                      'Database={REDACTED};'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        select {REDACTED}, {REDACTED}
        from {REDACTED}
        where {REDACTED} = 'A'
    
    '''

    cursor.execute(sql)
    drivers = cursor.fetchall()
    
    all_drivers = []
    for driver in drivers:
        all_drivers.append(excludedDriver(driver[0], driver[1]))
    
    json_string = json.dumps([ob.__dict__ for ob in all_drivers])
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/api/excludedriver", methods=["POST"])
@login_required
def exclude_driver():
    if request.method == 'POST':
        driver_code = request.form['driver_code'].strip()
        if driver_code is not None and driver_code != "":
            conn = pyodbc.connect('Driver={SQL Server};'
                                'Server={REDACTED};'
                                'Database={REDACTED};'
                                'Trusted_Connection=yes;')
            cursor = conn.cursor()

            check_driver_sql = ''' 
                select * from {REDACTED} where {REDACTED} = ?
            '''
            cursor.execute(check_driver_sql, driver_code)
            driver_valid = cursor.fetchall()
            
            if len(driver_valid) > 0:

                sql = ''' 
                    insert into {REDACTED}
                    values(?, cast(getdate() as date), getdate(), 'A')
                
                '''

                cursor.execute(sql, driver_code)
                conn.commit()

                if cursor.rowcount == 1:
                    json_string = '''{"status":"true"}'''
                    response = make_response(json_string)
                    response.headers['Content-Type'] = 'application/json'
                else:
                    json_string = '''{"status":"false"}'''
                    response = make_response(json_string)
                    response.headers['Content-Type'] = 'application/json'
                return response
            else:
                return Response("{'a':'b'}", status=301, mimetype='application/json')
        else:
            return Response("{'a':'b'}", status=301, mimetype='application/json')

    else:
        return abort(401)

#Remove a driver from the excluded driver
@app.route("/api/excludedriverdelete", methods=["POST"])
@login_required
def exclude_driver_driver():
    if request.method == 'POST':
        id = request.form['id']
        conn = pyodbc.connect('Driver={SQL Server};'
                            'Server={REDACTED};'
                            'Database={REDACTED};'
                            'Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql = ''' 
            update {REDACTED}
            set {REDACTED} = 'I'
            where {REDACTED} = ?
        
        '''

        cursor.execute(sql, id)
        conn.commit()

        if cursor.rowcount == 1:
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        else:
            json_string = '''{"status":"false"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return abort(401)

#Adjust percentages      
@app.route("/api/adjusttestperc", methods=["POST"])
#@login_required
def adjust_test_percentages():
    update_successful = False
    if request.method == 'POST':
        new_drug_percent = request.form['adj_drug']
        new_alc_percent = request.form['adj_alcohol']


        conn = pyodbc.connect('Driver={SQL Server};'
                            'Server={REDACTED};'
                            'Database={REDACTED};'
                            'Trusted_Connection=yes;')
        cursor = conn.cursor()

        old_percent_sql = '''
        select [{REDACTED}] 
        from {REDACTED}
        order by {REDACTED} 
        '''

        cursor.execute(old_percent_sql)
        old_percentages = cursor.fetchall()

        new_drug_percent = (float(new_drug_percent) * .01)
        new_alc_percent = (float(new_alc_percent) * .01)
        if new_drug_percent != float(old_percentages[1][0]):

            update_drug_sql = ''' 
            update {REDACTED}
            set [{REDACTED}] = ?
            where {REDACTED} = 'RND'
            '''
            cursor.execute(update_drug_sql, new_drug_percent)
            conn.commit()
            update_successful = True

        if new_alc_percent != float(old_percentages[0][0]):
            update_alc_sql = ''' 
            update {REDACTED}
            set [{REDACTED}] = ?
            where {REDACTED} = 'RNA'
            '''
            cursor.execute(update_alc_sql, new_alc_percent)
            conn.commit()
            update_successful = True

        if update_successful is True:
            return Response("{'a':'b'}", status=200, mimetype='application/json')
        else:
            return Response("{'a':'b'}", status=301, mimetype='application/json')

    else:
        return abort(401)

##Delete a user
@app.route('/api/deleteuser', methods=["POST"])
@login_required
def api_delete_user():
    if request.method == 'POST':
        id_ = request.form['id']
        if str(id_) != str(session['username_id']):

            conn = pyodbc.connect('Driver={SQL Server};'
                            'Server={REDACTED};'
                            'Database={REDACTED};'
                            'Trusted_Connection=yes;')
            cursor = conn.cursor()
            sql = ''' 
                delete from {REDACTED} 
                where {REDACTED} = ?
            
            '''

            cursor.execute(sql, id_)
            conn.commit()

            if cursor.rowcount == 1:
                json_string = '''{"status":"true"}'''
                response = make_response(json_string)
                response.headers['Content-Type'] = 'application/json'
            else:
                json_string = '''{"status":"false"}'''
                response = make_response(json_string)
                response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return Response("{'a':'b'}", status=301, mimetype='application/json')
    else:
        return abort(401)

#Get open random drug/alcohol tests
@app.route('/api/open')
@login_required
def api_open():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server={REDACTED};'
                      'Database={REDACTED};'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        select * 
        from {REDACTED}
        where {REDACTED} is null
        order by {REDACTED}, {REDACTED}
    
    '''

    cursor.execute(sql)
    open_tests = cursor.fetchall()
    
    tests = []
    for open_test in open_tests:
        tests.append(test(open_test[0], open_test[1], open_test[2], open_test[3], open_test[4], open_test[5], open_test[6], open_test[7], open_test[8], open_test[9], open_test[10]))
    
    json_string = json.dumps([ob.__dict__ for ob in tests])
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
    return response

#Gets all the historical drug/alcohol tests
@app.route('/api/historical')
@login_required
def api_historical():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server={REDACTED};'
                      'Database={REDACTED};'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        select * 
        from {REDACTED}
        where {REDACTED} is not null
    
    '''

    cursor.execute(sql)
    open_tests = cursor.fetchall()
    
    tests = []
    for open_test in open_tests:
        tests.append(test(open_test[0], open_test[1], open_test[2], open_test[3], open_test[4], open_test[5], open_test[6], open_test[7], open_test[8], open_test[9],open_test[10]))
    
    json_string = json.dumps([ob.__dict__ for ob in tests])
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
    return response

##Set a test to passed
@app.route('/api/pass', methods=["POST"])
@login_required
def api_set_passed():
    if request.method == 'POST':
        id_ = request.form['id']
        
        conn = pyodbc.connect('Driver={SQL Server};'
                        'Server={REDACTED};'
                        'Database={REDACTED};'
                        'Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql = ''' 
            update {REDACTED}
            set {REDACTED} = cast(getdate() as date),
            {REDACTED} = 'P'
            where {REDACTED} = ?
        
        '''

        cursor.execute(sql, id_)
        conn.commit()

        if cursor.rowcount == 1:
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        else:
            json_string = '''{"status":"false"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return abort(401)

##Set a test to failed
@app.route('/api/fail', methods=["POST"])
@login_required
def api_set_failed():
    if request.method == 'POST':
        id_ = request.form['id']
        
        conn = pyodbc.connect('Driver={SQL Server};'
                        'Server={REDACTED};'
                        'Database={REDACTED};'
                        'Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql = ''' 
            update {REDACTED}
            set {REDACTED} = cast(getdate() as date),
            {REDACTED} = 'F'
            where {REDACTED} = ?
        
        '''

        cursor.execute(sql, id_)
        conn.commit()

        if cursor.rowcount == 1:
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        else:
            json_string = '''{"status":"false"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return abort(401)

#Set a test to canceled status
@app.route('/api/cancel', methods=["POST"])
@login_required
def api_set_cancel():
    if request.method == 'POST':
        id_ = request.form['id']
        
        conn = pyodbc.connect('Driver={SQL Server};'
                        'Server={REDACTED};'
                        'Database={REDACTED};'
                        'Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql = ''' 
            update {REDACTED}
            set {REDACTED} = cast(getdate() as date),
            {REDACTED} = 'C'
            where {REDACTED} = ?
        
        '''

        cursor.execute(sql, id_)
        conn.commit()

        if cursor.rowcount == 1:
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        else:
            json_string = '''{"status":"false"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return abort(401)

##Reopen a previously passed/failed/canceled test
@app.route('/api/reopen', methods=["POST"])
@login_required
def api_set_reopen():
    if request.method == 'POST':
        id_ = request.form['id']
        
        conn = pyodbc.connect('Driver={SQL Server};'
                        'Server={REDACTED};'
                        'Database={REDACTED};'
                        'Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql = ''' 
            update {REDACTED}
            set {REDACTED} = null,
            {REDACTED} = null
            where {REDACTED} = ?
        
        '''

        cursor.execute(sql, id_)
        conn.commit()

        if cursor.rowcount == 1:
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        else:
            json_string = '''{"status":"false"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return abort(401)

##Get a list of users
@app.route('/api/userlist')
@login_required
def api_ousers():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server={REDACTED};'
                      'Database={REDACTED};'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql = ''' 
        select * 
        from {REDACTED}
    
    '''

    cursor.execute(sql)
    users = cursor.fetchall()

    all_users = []
    for user in users:
        newuser = User(user[0],user[1], '', '', user[4], user[5], user[6])
        all_users.append(newuser)
  
    
    json_string = json.dumps([ob.__dict__ for ob in all_users], default=str)
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
    return response

##Run a manual report based on parameters passed.
@app.route('/api/runmanualreport', methods=["POST"])
@login_required
def api_run_manual_report():
    if request.method == 'POST':
        try:
            company = request.form['company']
            email = request.form['email']
            number_drug = request.form['number_drug']
            number_alc = request.form['number_alc']
            
            if company == "" or email == "" or '@fleetmasterexpress.com' not in email:
                return Response("{'a':'b'}", status=301, mimetype='application/json')


            tester = RandomTest()
            #All drivers combined
            if number_drug != '' or number_alc != '':
                print(1)
                drivers = tester.get_drivers(company, number_drug, number_alc)
            else:
                print(2)
                drivers = tester.get_drivers(company)
            #Create summary page
            tester.create_summary(drivers)
            #Create detail page.
            tester.create_driver_letters(drivers)

            #Send the email with multiple attachments. create_email_body() is called here.
            email = emailing(email, "Random Selections for " + datetime.today().strftime('%Y-%m-%d'), tester.create_email_body(drivers), tester.pdf_documents, "report/")
            email.send_mail()
                
            json_string = '''{"status":"true"}'''
            response = make_response(json_string)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        except Exception as e:
            print(e)
            return Response("{'Error':'Error'}", status=301, mimetype='application/json')


    else:
        return abort(401)

## END OF API ROUTES!###

##Main function
if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
