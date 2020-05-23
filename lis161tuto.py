from flask import Flask, render_template, request, session, redirect, url_for
# from the framework Flask, datatypes are imported
import sqlite3
# imports the database

app = Flask(__name__)
# creates an instance of the Flask app
app.secret_key = 'lIs161'
# foruse in session, flask uses this to for server sided encryption, so the session can't be tampered with

def connect_db():
    conn = sqlite3.connect('flask.db')
    return conn
# connects to sqlite database


def read_all_classes():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM classes')
    results = cur.fetchall()
    cur.close()

    return results
# connects to database, chooses the classes table, and fetches all items from table


def read_all_details():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM details')
    results = cur.fetchall()
    cur.close()

    return results
# connects to database, chooses the details table, and fetches all items from table


def read_all_students():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM students')
    results = cur.fetchall()
    cur.close()

    return results
# connects to database, chooses the students table, and fetches all items from table
# above are functions which can be used instead of repeating code
# below are functions mapped to URLs

@app.route('/')
@app.route('/home')
def landing():
    return render_template('landing.html', title='TUTO WebApp')
#renders landing page of website, can also be accessed through /home


@app.route('/hub')
def hub():
    if 'username' in session:
# checks if a value has been assigned to username in the session
        username = session["username"]
        return render_template('hub.html', title='My Classes', home_name=username)
# assigns value from /form to username, this value is passed to home_name, so that when hub html is rendered the value of home_name can be used to display form data


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == "GET":
        return render_template('login.html', title='Sign In')
    else:
        var_name = request.form["username"]
        session["username"] = request.form["username"]
# the value for username is taken from the form, and is passed to var_name, and to the session

        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name) VALUES (?)', (var_name,))
        conn.commit()
        cur.close()
# the database is accessed, and the value of var_name is passed to the table users, under name

        if var_name == '':
            return redirect(url_for('unsuccessful'))
# if the form is empty, unsuccessful html will be displayed, with a button to go back to the form
        else:
            return redirect(url_for('hub'))


@app.route('/unsuccessful')
def unsuccessful():
    return render_template('unsuccessful.html', title='TUTO WebApp')
# simple form validation, returns user to form if form is not filled


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))
# uses session.pop to allow user to log out, then goes back to the landing page


@app.route('/classes')
def classes():
    if 'username' in session:
        username = session["username"]
        results = read_all_classes()
# checks if there is a username value in the session, value is passed to home_name, which allows the template to use the {{ home_name }} jinja code to display username
# also uses the predefined code read_all_classes() and passes the values to results
        return render_template('classes.html', results=results, home_name=username)


@app.route('/students')
def students():
    if 'username' in session:
        username = session["username"]
        results = read_all_students()
# checks if there is a username value in the session, value is passed to home_name, which allows the template to use the {{ home_name }} jinja code to display username
# also uses the predefined code read_all_students() and passes the values to results
        return render_template('students.html', results=results, home_name=username)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "GET":
        return render_template('add.html', title='Add Student Data')
# form allows user to add an entry into the student table
    else:
        sname = request.form['sname']
        snum = request.form['snum']
        work = request.form['work']
# assigns the values from the form with the names, sname, snum, and work, to sname, snum, and work, respectively

        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO students (sname, snum, work) VALUES (?,?,?)', (sname, snum, work))
        conn.commit()
        cur.close()
# database is accessed and the values of sname, snum, and work, from the form are added to the database

        if sname == '':
            return redirect(url_for('unsuccessful'))
# simple form validation, if sname has no value, then user will be redirected to the unsuccessful page, with an option to return to the form
        else:
            return redirect(url_for('students'), )
# returns to the students page, with an additional entry


@app.route('/sinfo', methods=['GET', 'POST'])
def sinfo():
    if request.method == 'GET':
        edit_id = request.args.get('edit')
# request.args.get() takes a dictionary type object containing all the values which corresponds to the id, or the {{ result[0] }} code in students html, this value is passedto edit_id
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM students WHERE id = ?', (edit_id,))
        result = cur.fetchone()
        cur.close()
# the value from edit_id, is used to get the list of data from the table students with the same value for its id

        return render_template('sinfo.html', result=result)
    elif request.method == 'POST':
        new_sname = request.form['sname']
        new_snum = request.form['snum']
        new_work = request.form['work']
        edit_id = request.form['id']
# values from the form are passed to new variables

        if request.form['edit'] == "update":
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('UPDATE students SET sname = ?, snum = ?, work = ? WHERE id = ?', (new_sname, new_snum, new_work, edit_id))
            conn.commit()
            cur.close()
# if the value of the form edit is update, the database is accessed and the row where id == edit_id will be given new values
        elif request.form['edit'] == "delete":
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM students WHERE id = ?', (edit_id,))
            conn.commit()
            cur.close()
# if the value of the form is delete, the row where id == edit_id is removed from the database (but the value of id will still be autoincrementing)

        results = read_all_students()
# after changes are made, the new table is displayed

        return render_template('students.html', results=results)


@app.route('/statuscheck', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        student = request.form['student']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT sname, snum, work from students WHERE sname LIKE ? OR snum LIKE ? OR work LIKE ?', (student, student, student))
        conn.commit()
        data = cur.fetchall()
        cur.close()
# simple search form; the value of the form named student is passed to student, the database is accessed, and the records containing the value of student will be retrieved

        if student == '':
            return redirect(url_for('unsuccessful'))
        return render_template('search.html', data=data)
    return render_template('search.html')


@app.route('/searchreqs', methods=['GET', 'POST'])
def searchreqs():
    if request.method == "POST":
        requ = request.form['requ']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT cname, reqs, act, supp from classes WHERE cname LIKE ? OR reqs LIKE ? OR act LIKE ? OR supp LIKE ?', (requ, requ, requ, requ))
        conn.commit()
        data = cur.fetchall()
        cur.close()
# simple search form; the value of the form named requ is passed to student, the database is accessed, and the records containing the value of requ will be retrieved
# results are passed to the variable data

        if requ == '':
            return redirect(url_for('unsuccessful'))

        return render_template('searchreqs.html', data=data)
    return render_template('searchreqs.html')


@app.route('/details')
def details():
    results = read_all_details()

    return render_template('details.html', results=results)
# the predefined code read_all_details() fetches records from the details table and is displayed

@app.route('/thanks')
def thanks():

    return render_template('thanks.html')

if __name__ == '__main__':
    app.run(debug=True)
# not really sure, but the code allows server to run if script is not imported
# debug=True allows the errors to be printed out when there is a problem with the code
#paulrondario lis161
