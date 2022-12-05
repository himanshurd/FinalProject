from chatui import *
import json
import socket
import threading
import sys
import itertools

def usage():
    print("usage: chatclient.py prefix host port", file=sys.stderr)

def main(argv):
    try:
        nick = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))
    s.send(hello_packet(nick))
    init_windows()

    first_thread = [threading.Thread(target=messages_for_user, args=(s, nick))]
    second_thread = [threading.Thread(target=messages_for_server, args=(s,), daemon=True)]
    
    for user,server in itertools.zip_longest(first_thread,second_thread):
        user.start()
        server.start()
    user.join()


def hello_packet(name):
    hello = {
        "type": "hello",
        "nick": name
    }
    return json.dumps(hello).encode()

def chat_packet(conn,message):
    chat = {
    "type": "chat",
    "message": message
    }
    return conn.send(json.dumps(chat).encode())

def messages_for_user(conn, user):
    while True:
        read_input = read_command(user + "> ")
        if read_input == "/q":
            conn.close()
            return
        else:
            chat_packet(conn,read_input)

def messages_for_server(data):
    while True:
        json_conversion = json.loads(data.recv(4096).decode())
        print_message(generate_messages(json_conversion))

def generate_messages(data):
    if data["type"] == "chat":
        return data["nick"] + ": " + data["message"]
    elif data["type"] == "join":
        return "*** " + data["nick"] + " has joined the chat"
    elif data["type"] == "leave":
        return "*** " + data["nick"] + " has left the chat"

if __name__ == "__main__":
    sys.exit(main(sys.argv))