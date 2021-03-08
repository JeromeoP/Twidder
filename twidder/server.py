from flask import Flask, jsonify, request, send_from_directory
import uuid
import database_helper
import re
import json
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError



app = Flask(__name__)
app.debug=True

signed_in_users = {}

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()


@app.route('/')
def index():
    return app.send_static_file('client.html')


@app.route('/twidder/sign-in', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if (database_helper.valid_user(email, password)):

        token = str(uuid.uuid4())

        database_helper.put_logged_in_user(email, token)
        return jsonify(
            {"success": True, "message": "Successfully signed in.", "data": token})
    else:
        return jsonify(
        {"success": False, "message": "Wrong username or password"}
        )

@app.route('/sign-up', methods=['POST'])
def sign_up():

        data = request.get_json()
        firstname = data['firstname']
        familyname = data['lastname']
        gender = data['gender']
        city = data['city']
        country = data['country']
        email = data['email']
        password = data['password']
        if (firstname and familyname and gender and city and country and email and password):
            if (len(password) >= 6):
                if(database_helper.taken_user(email)):
                    database_helper.new_user(email, password, firstname, familyname, gender, city, country)


                    return jsonify({"success": True, "message": "Successfully created a new user."})

                else:
                    return jsonify({"success": False, "message": "User already exists."})
            else:
                return jsonify({"success": False, "message": "Password is too short."})

        else:
            return jsonify({"success": False, "message": "You need to fill in all the fields."})

@app.route('/sign-out', methods=['POST'])
def sign_out():
    data = request.get_json()
    token = request.headers.get("token") #headers
    #token = data["token"]
    email = data["email"]
    is_signed_in = database_helper.check_logged_in_users(email, token)


    if (is_signed_in):
        database_helper.delete_logged_in_user(token)
        return jsonify({"success": True, "message": "Successfully signed out."})
    else:
        return jsonify({"success": False, "message": "You are not signed in."})

@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    #token = data["token"]
    token = request.headers.get("token") #headers

    email = ''.join(database_helper.get_email_by_token(token))

    is_signed_in = database_helper.check_logged_in_users(email, token)

    oldPassword = data['oldPassword']
    newPassword = data['newPassword']
    if (is_signed_in):
        help = database_helper.valid_user(email, oldPassword)

        if (help):
            database_helper.changePassword(newPassword, email)
            return jsonify({"success": True, "message": "Password changed."})
        else:
            return jsonify({"success": False, "message": "Wrong password."})

    else:
        return jsonify({"success": False, "message": "You are not logged in."})







@app.route('/get-user-data-by-email/<toEmail>', methods=['GET'])
def get_user_data_by_email(toEmail):
        #data = request.get_json()

        token = request.headers.get("token") #headers
        #token = data["token"]
        email = ''.join(database_helper.get_email_by_token(token))
        is_signed_in = database_helper.check_logged_in_users(email, token)

        if (is_signed_in):
            match = database_helper.get_user_data_by_email(toEmail)
            if (match):
                return jsonify({"success": True, "message": "User data retrieved.", "data": match})
            else:
                return jsonify({"success": False, "message": "No such user."})
        else:
            return jsonify({"success": False, "message": "You are not signed in."})

@app.route('/get-user-data-by-token/', methods=['GET'])
def get_user_data_by_token():
    token = request.headers.get("token") #headers

    email = ''.join(database_helper.get_email_by_token(token))
    is_signed_in = database_helper.check_logged_in_users(email, token)
    if (is_signed_in):
        return get_user_data_by_email(email)
    else:
        return False







@app.route('/get-user-messages-by-token', methods=['GET'])
def get_user_messages_by_token():
    token = request.headers.get("token") #headers

    email = ''.join(database_helper.get_email_by_token(token))
    is_signed_in = database_helper.check_logged_in_users(email, token)
    if (is_signed_in):
        return get_user_messages_by_email(email)
    else:
        return False


@app.route('/get-user-messages-by-email/<toEmail>', methods=['GET'])
def get_user_messages_by_email(toEmail):
    token = request.headers.get("token") #headers
    email = ''.join(database_helper.get_email_by_token(token))

    is_signed_in = database_helper.check_logged_in_users(email, token)

    valid_user = database_helper.taken_user(toEmail)
    if (is_signed_in):
        if not (valid_user):
            messages = database_helper.get_messages(toEmail)
            return jsonify({"success": True, "message": "User messages retrieved.", "data": messages})
        else:
            return jsonify({"success": False, "message": "No such user."})
    else:
        return jsonify({"success": False, "message": "You are not signed in."})

@app.route('/post-message', methods=['POST'])
def post_message():
    data = request.get_json()
    #token = data['token']
    token = request.headers.get("token") #headers

    message = data['message']
    toEmail = data['toEmail']
    fromEmail = ''.join(database_helper.get_email_by_token(token))
    is_signed_in = database_helper.check_logged_in_users(fromEmail, token)

    if (is_signed_in):
        existingUser = database_helper.taken_user(toEmail)
        if not (existingUser):


            database_helper.post_messages(message, fromEmail, toEmail)
            return jsonify({"success": True, "message": "Message posted"})
        else:
            return jsonify({"success": False, "message": "No such user."})
    else:
        return jsonify({"success": False, "message": "You are not signed in."})

'''
@app.route('/socket')
def api():
    if request.environ.get('wsgi.websocket'):

        ws = request.environ['wsgi.websocket']

        token = ws.receive()
        email = ''.join(database_helper.get_email_by_token(token))
        is_signed_in = database_helper.check_logged_in_users(email, token)
        #guess this is ur authentication function, can also just check
        #if db_helper.get_email_by_token() returns anythin

        if (is_signed_in):
            if email in signed_in_users:
                old_socket = signed_in_users[email]
                try:
                    old_socket.send(json.dumps("logout"))
                    print("Active Websocket deleted")

                except:
                    print("Active Websocket deleted (due to reload)")
                del signed_in_users[email]

            #outside the condition
            signed_in_users[email] = ws
            print("New Active Websocket added")
        #no need to be an else
            signed_in_users[email] = ws
            print("New Active Websocket added")
            while True:
                try:
                    message=ws.receive()
                except:
                    #print(socket died or w/e)
                    return "w/e"

'''






if __name__ == "__main__":
    print("sever started")
    http_server = WSGIServer(('', 5000), app, handler_class = WebSocketHandler)

    http_server.serve_forever()
    #app.run()
