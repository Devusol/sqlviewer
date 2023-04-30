from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash

mysql = MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/api/signup', methods=['POST'])
def signup_post():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    _hashed_password = generate_password_hash(_password)
    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))

    data = cursor.fetchall()
    if len(data) == 0:
        conn.commit()
        return json.dumps({'message':'User created successfully !'})
    else:
        return json.dumps({'error':str(data[0])})


@app.route("/")
def index():
    # return "Hello from index route"
    return render_template('index.html')

if __name__ == "__main__":
    app.run()