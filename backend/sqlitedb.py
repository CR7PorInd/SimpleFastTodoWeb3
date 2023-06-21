from sqlite3 import Connection, connect, Cursor


class UsersDB:
    @staticmethod
    def connect(database: str) -> Connection:
        conn = connect(database, check_same_thread=False)
        return conn

    @staticmethod
    def exec(conn: Connection, sql: str) -> Cursor:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return cursor

    @staticmethod
    def signup(usr: str, eml: str, pwd: str, conn: Connection) -> str:
        res = UsersDB.exec(conn, """
                    SELECT pwd FROM Accounts WHERE usr='{}';
                """.format(usr)).fetchone()
        if res is not None:
            message, status = UsersDB.login(usr, pwd, conn, status2=True)
            return message, status
        res = UsersDB.exec(conn, """
                    SELECT usr FROM Accounts WHERE eml='{}';
                """.format(usr)).fetchone()
        if res is None:
            UsersDB.exec(conn, f"""
                INSERT INTO Accounts(usr, eml, pwd) VALUES('{usr}', '{eml}', '{pwd}');
            """)
        else:
            return 'There is a user with this email!', 1
        return 'Signed Up Successfully!', 0

    @staticmethod
    def login(usr: str, pwd: str, conn: Connection, status2=False):
        res = UsersDB.exec(conn, "SELECT usr FROM Accounts").fetchall()
        for item in res:
            res[res.index(item)] = list(item)

        users = []
        for item in res:
            for thing in item:
                users.append(thing)

        if usr not in users:
            return 'User not found! Login Failed!', 1

        res = UsersDB.exec(conn, f"SELECT usr FROM Accounts WHERE pwd='{pwd}'").fetchone()
        if res is None:
            return 'Incorrect Password!', 1

        if status2:
            return 'Login Successful.', 2
        return 'Login Successful.', 0
