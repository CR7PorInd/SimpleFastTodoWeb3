def restart():
    import sqlite3
    db = sqlite3.connect('./users.db', check_same_thread=False)
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Accounts;")
    cursor.execute('CREATE TABLE Accounts(usr VARCHAR(50), eml VARCHAR(50), pwd VARCHAR(50));')
    from . import inc
    inc.adduser()


if __name__ == '__main__':
    restart()
