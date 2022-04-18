import os
import werkzeug
from multiprocessing import Process
from flask import Flask, redirect, render_template, request, session, url_for, jsonify, send_from_directory
from threading import Thread
from chatbot_v1 import chatbot

SERVER = False
EVEshutdown = False
EVEserver_status = False
EVE_cmd = True


IP = '0.0.0.0'
PORT = 4000
Password = ""
app = Flask(__name__, static_url_path='/static')
server = Process(target=app.run)

tools = []
previous_message = []
version = [
    {
        'version': 'Version 1'
    }
]
messages = [
    {
        'message': 'Works.'
    }
]


def start_server():
    try:
        app.secret_key = os.urandom(12)
        app.run(host=IP, port=PORT)
        session.permanent = False
    except:
        print("Server is ON.")


def tool_handler(tool):
    if tool in tools:
        return tool + " out of " + str(tools)


@app.route('/', methods=["GET"])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if session.get('logged_in'):
        if request.method == 'GET':
            return render_template('home.html', version=version)  # secure page
        if request.method == 'POST':
            #   *       *       *
            """# chatbot 1:
            client_msg = request.get_json()
            if not previous_message:
                previous_message.append("")
            previous_message.append(client_msg)
            print("Client said : " + str(client_msg))
            try:
                return jsonify(tool_handler(client_msg))
            except():
                print("no tools called.")
                
            try:
                return jsonify(chat.chat(client_msg, previous_message[-2]))
            except():
                print("bot failed!")"""
            #   *       *       *
            """# print("Client said : " + str(client_msg) + " " + str(chat_test(client_msg)))
            if client_msg == "":
                pass
            if client_msg == "TEST":
                return jsonify("TEST CONNECTION WORKS!")
            print("Client said : " + str(client_msg)+ " " + str(chat_test(client_msg)))
            if chat_test(client_msg) == True:
                return jsonify(chat(client_msg))
            elif chat_test(client_msg) == False:
                #dont know how to make  continued response work, that is EVE_cmd chat_new() based on chat
                if response_unknown == "":
                    response_unknown = client_msg
                    print(response_unknown)
                    return jsonify("Bot: I haven't seen that statement before, how should I respond? ")
                elif response_unknown != "":
                    return jsonify(chat_new(response_unknown, client_msg))
            else:
                return jsonify("Error")
            """
            # chatbot 2:
            return jsonify(chatbot(request.get_json(), SERVER))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == Password:
            session['logged_in'] = True
            # --- Tool Test ---
            tools.clear(), tools.append("A"), tools.append("B"), tools.append("C")
            # ---           ---
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('login.html', version=version)  # login page


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route("/kill_server")
def kill_server():
    if session.get('logged_in'):
        os._exit(0)
    else:
        return redirect(url_for('home'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def page_not_found():
    return redirect(url_for('home'))


@app.errorhandler(400)
@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request():
    return redirect(url_for('home'))


if __name__ == "__main__":
    while EVE_cmd:
        user = input()
        if user:
            if '@EVE' in user:
                if 'server_status' in user.lower():
                    print('SERVER: ', str(SERVER), '\n', str(server), '\n')
                    if SERVER:
                        EVEserver_status = input("Terminate Server? y")
                        if EVEserver_status == 'y' or EVEserver_status == '':
                            SERVER = False
                            print('Server terminated.\n')
                        else:
                            print('Aborted.')
                    else:
                        EVEserver_status = input("Launch Server? y")
                        if EVEserver_status == 'y' or EVEserver_status == '':
                            SERVER = True
                            print('Server launched.\n')
                        else:
                            print('Aborted.')
                if 'help' in user.lower():
                    print('COMMANDS:\nshutdown, start_server, quit_server, server_status\n')
                if 'shutdown' in user.lower():
                    print('Confirm shutdown? y/n')
                    EVEshutdown = True
                    while EVEshutdown:
                        user = input()
                        if user:
                            if user.lower() == 'y':
                                print('Terminated.\n')
                                EVE_cmd = False
                                EVEshutdown = False
                                break
                            elif user.lower() == 'n':
                                print('Aborted.\n')
                                EVEshutdown = False
                                break
                            else:
                                print('Confirm shutdown? y/n')
                elif 'start_server' in user.lower():
                    if SERVER:
                        print('Server is on.\n')
                    else:
                        SERVER = True
                        print('Server launched.\n')
                elif 'quit_server' in user.lower():
                    if SERVER:
                        SERVER = False
                        print('Server terminated.\n')
                    else:
                        print('Server is off.')
                else:
                    print('Command not recognized.')
            else:
                chatbot(user, SERVER)
            if SERVER:
                thread = Thread(target=start_server, daemon=True)
                if thread.is_alive() is False:
                    thread.start()
