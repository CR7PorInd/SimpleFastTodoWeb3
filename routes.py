from flask import Flask, render_template, request
from flask import session, redirect, url_for, g
from backend import UsersDB, adduser
from sqlite3 import connect
import os.path as pt


if not pt.exists('./users.db'):
    import backend.restart as restart
    restart.restart()

todo_list = {}
app: Flask = Flask('todo_list_web_SF_3_0_1')


@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        if session['username'] == 'IndCR7Com':
            return redirect(url_for('manager'))
        todo_list.clear()
        g.user = session['username']
        data = 'todos/' + session['username'] + '.db'
        db = connect(data)
        cursor = db.cursor()
        res = cursor.execute('SELECT tid, title, status from Todos').fetchall()
        for item in res:
            res[res.index(item)] = list(item)
        for i in res:
            todo_list[i[1]] = [i[0], i[1], i[2]]
            todo_list[i[1]][2].capitalize()
        print(todo_list)
        db.commit()

        return render_template('user/home.html', todo_list=todo_list, message='', len=len)
    return render_template('web/start.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('user/signup.html')
    else:
        usr = request.form['usr']
        if usr == 'IndCR7Com':
            return render_template('user/signup.html', message='This User is an Admin.')
        eml = request.form['eml']
        pwd = request.form['pwd']
        message, status = UsersDB.signup(usr, eml, pwd, connect('users.db', check_same_thread=False))
        if status == 0:
            adduser()
            return redirect(url_for('home'))
        elif status == 2:
            session['username'] = usr
            session['password'] = pwd
            return redirect(url_for('home'))
        return render_template('user/signup.html', message=message)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        print('/login POST Request.')
        print(request, request.form)
        usr = request.form['usr']
        if usr == 'IndCR7Com':
            correct = 'Pranav@Pranav61209'
            pwd = request.form['pwd']
            if pwd == correct:
                session['username'] = 'IndCR7Com'
                session['password'] = correct
                return redirect(url_for('manager'))
            else:
                return render_template('manager/login.html', message='Password is Wrong!')
        pwd = request.form['pwd']
        message, status = UsersDB.login(usr, pwd, connect('users.db', check_same_thread=False))
        print(message, status)
        if status == 0:
            session['username'] = usr
            session['password'] = pwd
            return redirect(url_for('home'))
        return render_template('user/login.html', message=message)


@app.route('/logout/')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/about/', methods=['GET'])
def about():
    if 'username' in session and session['username'] != 'IndCR7Com':
        return render_template('user/about.html',)


@app.route('/add/', methods=['POST'])
def add():
    if 'username' not in session or session['username'] == 'IndCR7Com':
        return redirect(url_for('home'))
    if request.method == 'GET':
        return redirect(url_for('home'))
    title = request.form['title']
    status = request.form['status']
    res = UsersDB.exec(connect('todos/'+session['username']+'.db'), "SELECT title from Todos;").fetchall()
    titles = []
    if res:
        for i in res:
            for j in i:
                titles.append(j)

    if title not in titles:
        if 'completed' not in status.lower() and 'progress' not in status.lower():
            return render_template('user/home.html', title=title, message='Invalid Status. '
                                                                          'Should be "Not Completed", "Completed", '
                                                                          '"In Progress""')
        if 'completed' in status.lower():
            if 'not' in status.lower():
                status = 'Not Completed'
            else:
                status = 'Completed'
        elif 'progress' in status.lower():
            status = 'In Progress'
        UsersDB.exec(connect('todos/' + session['username'] + '.db'),
                     f"INSERT INTO Todos(title, status) VALUES('{title}', '{status}')")
    return redirect(url_for('home'))


@app.route('/delete/<int:tid>/', methods=['GET'])
def delete(tid: int):
    if 'username' not in session or session['username'] == 'IndCR7Com':
        return redirect(url_for('home'))
    todo_list.clear()
    data = 'todos/' + session['username'] + '.db'
    db = connect(data)
    cursor = db.cursor()
    res = cursor.execute('SELECT tid, title, status from Todos').fetchall()
    for item in res:
        res[res.index(item)] = list(item)
    for i in res:
        todo_list[i[1]] = [i[0], i[1], i[2]]
        todo_list[i[1]][2].capitalize()
    db.commit()

    UsersDB.exec(connect('todos/'+session['username']+'.db', check_same_thread=False),
                 f"DELETE FROM Todos WHERE tid='{tid}'")
    return redirect(url_for('home'))


@app.route('/update/<int:tid>/', methods=['GET', 'POST'])
def update(tid: int):
    if 'username' not in session or session['username'] == 'IndCR7Com':
        return redirect(url_for('home'))
    if request.method == 'GET':
        title = UsersDB.exec(connect('todos/'+session['username']+'.db'),
                             f"SELECT title FROM Todos WHERE tid='{tid}'").fetchone()[0]

        return render_template('user/update.html', title=title, message='', tid=tid)
    else:
        title = request.form['title']
        status = request.form['status']
        if 'completed' not in status.lower() and 'progress' not in status.lower():
            title = UsersDB.exec(connect('todos/' + session['username'] + '.db'),
                                 f"SELECT title FROM Todos WHERE tid='{tid}'").fetchone()[0]
            return render_template('user/update.html', title=title, message='Invalid Status. '
                                                                            'Should be '
                                                                            '"Not Completed", "Completed", '
                                                                            '"In Progress""', tid=tid)
        if 'completed' in status.lower():
            if 'not' in status.lower():
                status = 'Not Completed'
            else:
                status = 'Completed'
        elif 'progress' in status.lower():
            status = 'In Progress'
        UsersDB.exec(connect(f'todos/{session["username"]}.db'),
                     f"UPDATE Todos SET status='{status}' WHERE tid='{tid}'")
        UsersDB.exec(connect(f'todos/{session["username"]}.db'),
                     f"UPDATE Todos SET title='{title}' WHERE tid='{tid}'")
        return redirect(url_for('home'))


@app.route('/manager/', methods=['GET'])
def manager():
    if 'username' in session:
        if session['username'] == 'IndCR7Com':
            cursor = UsersDB.exec(connect('users.db'), f"SELECT usr, eml, pwd FROM Accounts").fetchall()
            i = 0
            for item in cursor:
                cursor[i] = list(item)
                i = i + 1
            i = 0
            for item in cursor:
                for thing in item:
                    if i == 2:
                        item[2] = u'\u2022' * len(thing)
                        item = item + [thing]
                    i = i + 1
                i = 0
            return render_template('manager/manage.html', users=cursor, len=len)
        else:
            return redirect(url_for('home'))
    else:
        return redirect('/manager/login/')


@app.route('/manager/login/', methods=['GET', 'POST'])
def manager_login():
    if 'username' in session:
        if session['username'] != 'IndCR7Com':
            return redirect(url_for('home'))
        else:
            return redirect(url_for('manager'))
    if request.method == 'GET':
        return render_template('manager/login.html', message='')
    else:
        print(request, request.form, request.form)
        correct = 'Pranav@Pranav61209'
        pwd = request.form['pwd']
        if pwd == correct:
            session['username'] = 'IndCR7Com'
            session['password'] = pwd
            return redirect(url_for('manager'))
        else:
            return render_template('manager/login.html', message='Wrong Password!')


@app.route('/manager/logout/', methods=['GET'])
def manager_logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/')


@app.route('/manager/delete/<string:name>', methods=['GET'])
def manager_delete(name):
    if 'username' not in session or session['username'] != 'IndCR7Com':
        return redirect(url_for('home'))
    UsersDB.exec(connect('users.db', check_same_thread=False), f"DELETE FROM Accounts WHERE usr='{name}'")
    import os
    if os.path.exists(f'todos/{name}.db'):
        os.remove(f'todos/{name}.db')
    return redirect(url_for('manager'))


@app.route('/manager/view/<string:user>', methods=['GET'])
def manager_view(user):
    if 'username' not in session or session['username'] != 'IndCR7Com':
        return redirect(url_for('home'))
    todo = {}
    data = 'todos/' + user + '.db'
    db = connect(data)
    cursor = db.cursor()
    res = cursor.execute('SELECT tid, title, status from Todos').fetchall()
    for item in res:
        res[res.index(item)] = list(item)
    for i in res:
        todo[i[1]] = [i[0], i[1], i[2].capitalize()]
    db.commit()
    return render_template('manager/view.html', todo_list=todo, user=user)


@app.errorhandler(404)
def fnf(*args):
    type(args)
    return render_template('web/Todo_404.html')


@app.before_request
def before_request():
    g.username = None
    if 'username' in session:
        g.username = session['username']


@app.route('/session')
def web_session():
    if 'username' in session:
        return session['username']
    return redirect(url_for('login'))

app.secret_key = '%^^*$*((^&(^$*#$^^$#&&$&((&%%(%^*$^&$&%$^(((^$^**%^#&' \
                     '*()%%&&#&&%^^$$:"{:"}{_+_)(&^^&@*@)@**(|}{:`~,' \
                 '<>/:"\\( '
