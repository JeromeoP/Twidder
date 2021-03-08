import sqlite3
from flask import g

DATABASE_URI = "database.db"

def db_hackU(query, args=()):
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    result = []
    for index in range(len(rows)):
        result.append(rows[index])
    return result
#From flask website

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    return db
#From flask website

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
#HÖRRR
def put_logged_in_user(email, token):
    if check_logged_in_users_by_email(email):
        try:
            get_db().execute("UPDATE signedInUsers SET token = ? WHERE email = ?", [token, email])
            get_db().commit()
            return True
        except:
            return False
    else:

        try:
            get_db().execute("INSERT INTO signedInUsers VALUES(?,?);", [email, token])
            get_db().commit()
            return True
        except:
            return False


def check_logged_in_users(email, token):
    logged_in_user = query_db("SELECT email, token FROM signedInUsers WHERE email = ? AND token = ?", [email, token], one=True)
    if (logged_in_user is None):
        return False
    else:
        return True

def check_logged_in_users_by_email(email):
    logged_in_user = query_db("SELECT email FROM signedInUsers WHERE email = ?", [email], one=True)
    if (logged_in_user is None):
        return False
    else:
        return True

def check_logged_in_users_with_token (token):
    logged_in_user = query_db("SELECT email, token FROM signedInUsers WHERE token = ?", [token], one=True)
    if (logged_in_user is None):
        return False
    else:
        return True

def get_email_by_token(token):
    try:


        cursor = get_db().execute("select email from signedInUsers where token like ?", [token])
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for index in range(len(rows)):
            result.append(rows[index][0])
        return result

    except:
        return False




def delete_logged_in_user(token):
    try:
        get_db().execute("DELETE FROM signedInUsers WHERE token = ?;", [token])
        get_db().commit()
        return True
    except:
        return False

def valid_user(email, password):

    valid_user = query_db("SELECT email, password FROM users WHERE email = ? AND password = ?", [email, password], one=True)
    if (valid_user is None):
        return False
    else:
        return True


def taken_user(email):

    is_user_taken = query_db("SELECT email FROM users WHERE email = ?", [email], one=True)
    if (is_user_taken is None):
        return True
    else:
        return False

def new_user(email, password, firstname, familyname, gender, city, country):
    try:
        get_db().execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", [email, password, firstname, familyname, gender, city, country])
        get_db().commit()

        return True
    except:
        return False

def get_user_data_by_email(email):
     user_data = query_db("SELECT email, firstname, familyname, gender, city, country FROM users WHERE email = ?", [email], one = True)
     return user_data



def changePassword(password, email):
    try:
        get_db().execute("UPDATE users SET password = ? WHERE email = ?", [password, email])
        get_db().commit()
    except:
        return False
def get_messages(email):
    user_messages = db_hackU("SELECT * FROM messages WHERE toUser = ?", [email])
    return user_messages

def post_messages(messages, fromUser, toUser):
    try:
        get_db().execute("INSERT INTO messages (message, fromUser, toUser) VALUES(?,?,?);", [messages, fromUser, toUser])
        get_db().commit()

        return True

    except:
        return False
