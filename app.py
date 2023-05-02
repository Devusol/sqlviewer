import datetime
from flask import Flask, render_template, request, json, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash

mysql = MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'devusol'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Tulip_-Db'
app.config['MYSQL_DATABASE_DB'] = 'tulip2023'
app.config['MYSQL_DATABASE_HOST'] = '50.62.141.187'
# app.config['MYSQL_USE_POOL'] = {
#     # use = 0 no pool else use pool
#     "use": 0,
#     # size is >=0,  0 is dynamic pool
#     "size": 10,
#     # pool name
#     "name": "local",
# },
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS bucketlist (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")


@app.route('/signup')
def signup():
    return render_template("signup.html")


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
    print("tulip route")
    cursor = conn.cursor()

    # _contest = request.form['submissiontype']
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

    for file in _files:
        x = datetime.datetime.now()
        print(x.strftime("%m_%d_%H_%M"))
        _filenames += (f", {file.filename}")
        file.save(f"./uploads/{_firstname}_{_lastname}_{x.strftime('%m_%d_%H_%M')}_{file.filename}")
        print(_filenames)

    sql = "INSERT INTO ContestEntries (firstname, lastname, email, phone, address1, address2, city, state, zip,  files) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (_firstname, _lastname, _email, _phone,
           _add1, _add2, _city, _state, _zip,  _filenames)
    cursor.execute(sql, val)
    conn.commit()
    # print(cursor.rowcount, "record inserted.")

    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        try:
            conn.commit()
            json.dumps({'message': 'User created successfully !'})
            cursor.close()
            return redirect('http://localhost:3000/tulip-contest.php')
        except Exception as e:
            print('Failed to commit to db: ' + e)
    else:
        return json.dumps({'error': str(data[0])})


@app.route("/")
def index():
    # return "Hello from index route"
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
