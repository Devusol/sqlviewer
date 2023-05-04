from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
load_dotenv('.env') 

print(os.environ.get('MYSQL_DATABASE_USER'))

mysql = MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = os.environ.get('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('MYSQL_DATABASE_HOST')
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


@app.route("/")
def index():
    # return "Hello from index route"
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
