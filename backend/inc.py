def adduser():
    import sqlite3
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cu = conn.cursor()
    res = cu.execute("SElECT usr from Accounts;").fetchall()
    if res is None:
        return
    users = []
    for i in res:
        res[res.index(i)] = list(i)
    for j in res:
        users.append(j[0])

    for usr in users:
        con = sqlite3.connect('todos/' + usr + '.db')
        cursor = con.cursor()
        cursor.execute("DROP TABLE IF EXISTS Todos;")
        cursor.execute("CREATE TABLE Todos(tid INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, status TEXT);")
        con.commit()
        cursor.close()
        con.close()
    conn.commit()
