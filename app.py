import datetime
import smugmug
import threading
import emailer
from flask import Flask, render_template, request, json, redirect, session, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash
import pymysql.cursors


mysql = MySQL()


app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'devusol'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Tulip_-Db'
app.config['MYSQL_DATABASE_DB'] = 'tulip2023'
# '50.62.141.187'  # 'localhost'
app.config['MYSQL_DATABASE_HOST'] = 'mysql.devusol.net'
app.config['MYSQL_USE_POOL'] = {
    # use = 0 no pool else use pool
    "use": 0,
    # size is >=0,  0 is dynamic pool
    "size": 10,
    # pool name
    "name": "local",
}
app.secret_key = 'F-JaNdRgUkXp2r5u8x/A?D(G+KbPeShV'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS ContestEntries ( \
                id INT AUTO_INCREMENT PRIMARY KEY, \
                timestamp DATETIME NULL DEFAULT CURRENT_TIMESTAMP(), \
                firstname VARCHAR(255), \
                lastname VARCHAR(255), \
                email VARCHAR(255), \
                phone VARCHAR(50), \
                address1 VARCHAR(255), \
                address2 VARCHAR(255), \
                city VARCHAR(50), \
                state VARCHAR(50), \
                zip VARCHAR(50), \
                contest VARCHAR(50), \
                files TEXT, \
                agreedTOS BIT \
                )")

cursor.execute("CREATE TABLE IF NOT EXISTS BloomAlerts ( \
                id INT AUTO_INCREMENT PRIMARY KEY, \
                timestamp DATETIME NULL DEFAULT CURRENT_TIMESTAMP(), \
                firstname VARCHAR(255), \
                lastname VARCHAR(255), \
                email VARCHAR(255)\
                )")

cursor.execute("CREATE TABLE IF NOT EXISTS Admins ( \
                id INT AUTO_INCREMENT PRIMARY KEY, \
                username VARCHAR(255), \
                password VARCHAR(255) \
                )")

cursor.close()


@app.route('/emailertest')
def sendNotice():
    bod = "body"
    emailer.sendIt(f"text that goes into the {bod}")
    return json.dumps({'message': 'Message sent!'})


@app.route('/api/bloomalerts', methods=['POST'])
def bloom_alert():

    _redirect = 'https://whitechapelcemetery.com/tulip-bloomthankyou.php'
    conn.ping(reconnect=True)
    cursor = conn.cursor()

    _firstname = request.form['fname']
    _lastname = request.form['lname']
    _email = request.form['email']

    sql = "INSERT INTO BloomAlerts (firstname, lastname, email) VALUES (%s, %s, %s)"
    val = (_firstname, _lastname, _email)
    cursor.execute(sql, val)
    conn.commit()
    # print(cursor.rowcount, "record inserted.")

    data = cursor.fetchall()
    # print(data)
    if len(data) == 0:
        try:
            conn.commit()
            json.dumps({'message': 'User created successfully !'})
            cursor.close()

            emailThread = threading.Thread(daemon=True, target=emailer.sendIt, kwargs={
                'message': request.args.get('message', f"Bloom Alert Subscriber: {_firstname} {_lastname}\nEmail: {_email}")})

            emailThread.start()
            return redirect(_redirect)

        except Exception as e:
            print('Failed to commit to db: ' + e)
            return redirect(_redirect)
    else:
        print('error: ', str(data[0]))
        return redirect(_redirect)


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/signin')
def signin():
    return render_template("signin.html")


@app.route('/api/signup', methods=['POST'])
def signup_post():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    _hashed_password = generate_password_hash(_password)
    # cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
    sql = "INSERT INTO bucketlist (name, email, password) VALUES (%s, %s, %s)"
    val = (_name, _email, _hashed_password)
    cursor.execute(sql, val)
    conn.commit()
    # print(cursor.rowcount, "record inserted.")
    data = cursor.fetchall()
    if len(data) == 0:
        conn.commit()
        return json.dumps({'message': 'User created successfully !'})
    else:
        return json.dumps({'error': str(data[0])})


@app.route('/api/tulip2023', methods=['POST'])
def tulip_post():
    _redirect = 'https://whitechapelcemetery.com/tulip-thankyou.php'
    conn.ping(reconnect=True)
    cursor = conn.cursor()

    _contest = request.form['categorytype']
    _firstname = request.form['fname']
    _lastname = request.form['lname']
    _email = request.form['email']
    _phone = request.form['phone']
    _add1 = request.form['add1']
    _add2 = request.form['add2']
    _city = request.form['city']
    _state = request.form['state']
    _zip = request.form['zip']
    _files = request.files.getlist('uploads')
    _filenames = ""
    _filepaths = []
    _agreed = 1 if request.form['agreed'] else 0

    # print(_agreed)

    for file in _files:
        x = datetime.datetime.now()
        # print(x.strftime("%m_%d_%H_%M"))
        _filepath = f"./uploads/{_contest}/{_firstname}_{_lastname}_{x.strftime('%m_%d_%H_%M')}_{file.filename}"
        _filenames += (f"{file.filename}, ")
        _filepaths.append(_filepath)
        file.save(_filepath)
        # print(_filenames)

    sql = "INSERT INTO ContestEntries (firstname, lastname, email, phone, address1, address2, city, state, zip, contest, files, agreedTOS) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (_firstname, _lastname, _email, _phone,
           _add1, _add2, _city, _state, _zip, _contest, _filenames, _agreed)
    cursor.execute(sql, val)
    conn.commit()
    # print(cursor.rowcount, "record inserted.")

    data = cursor.fetchall()
    # print(data)
    if len(data) == 0:
        try:
            conn.commit()
            json.dumps({'message': 'User created successfully !'})
            cursor.close()

            smugThread = threading.Thread(daemon=True, target=smugmug.upload_image, kwargs={
                'image_paths': request.args.get('image_paths', _filepaths)})
            emailThread = threading.Thread(daemon=True, target=emailer.sendIt, kwargs={
                'message': request.args.get('message', f"Contestant: {_firstname}_{_lastname}\nPhotos submitted: {_filenames}")})

            emailThread.start()
            smugThread.start()

            return redirect(_redirect)

        except Exception as e:
            print('Failed to commit to db: ' + e)
            return redirect(_redirect)
    else:
        print('error: ', str(data[0]))
        return redirect(_redirect)


@app.route("/")
# def index():
#     # return "Hello from index route"
#     return redirect('https://whitechapelcemetery.com/tulip-festival.php')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'uname' in request.form and 'pword' in request.form:
        _username = request.form['uname']
        _password = request.form['pword']
        _selection = request.form['dbselect']

        conn.ping(reconnect=True)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        cursor.execute(
            'SELECT * FROM Admins WHERE username = % s \
            AND password = % s', (_username, _password))

        account = cursor.fetchone()

        print(account)
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']

            if _selection == 'bloom':
                cursor.execute('SELECT `timestamp`,  `firstname`,  `lastname`,  `email` FROM BloomAlerts')
            else:
                cursor.execute('SELECT `timestamp`,  `firstname`,  `lastname`,  `email`,  `phone`,  `address1`,  `address2`,  `city`,  `state`,  `zip`,  `contest` FROM ContestEntries')

            _data = cursor.fetchall()
            print(_data)
            msg = json.loads(json.dumps(_data))
            cursor.close()
            return render_template('viewdb.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'

        cursor.close()
    return render_template('login.html', msg=msg)


@app.route("/display")
def display():
    print("display route")
    if 'loggedin' in session:

        # return render_template("display.html", account=account)
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
