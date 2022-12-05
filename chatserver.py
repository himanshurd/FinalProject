import json
import sys
import socket
import select

def join_packet(client_name):
    join = {
    "type": "join",
    "nick": client_name
    }
    return json.dumps(join)

def chat_packet(message, client_name):
    chat = {
    "type": "chat",
    "nick": client_name,
    "message": message
    }
    return json.dumps(chat)

def leave_packet(client_name):
    leave = {
    "type": "leave",
    "nick": client_name
    }
    return json.dumps(leave)

def run_server(port):
    server_socket = socket.socket()
    server_socket.bind(('', port))
    server_socket.listen()
    socket_set = {server_socket}
    name_dict = {}

    while True:
        ready_to_read, _, _ = select.select(socket_set, {}, {})
        for s in ready_to_read:
            if s is server_socket: 
                new_socket, _ = server_socket.accept()
                socket_set.add(new_socket)
            else:
                message = s.recv(4096) 
                if not message:
                  socket_set.remove(s)
                  client_name = name_dict.pop(s)
                  print(leave_packet(client_name))
                  
                  for user_s in name_dict:
                      user_s.send(leave_packet(client_name).encode())
                  print(f"*** {client_name} has left the chat")
                else:
                    if json.loads(message)["type"] == "hello":
                        print(f"*** {json.loads(message)['nick']} has joined the chat")
                        name_dict[s] = json.loads(message)["nick"]
                        print(join_packet(json.loads(message)["nick"]))

                        for user_s in name_dict:
                            user_s.send(join_packet(json.loads(message)["nick"]).encode())
                    elif json.loads(message)["type"] == "chat":
                        print(f"{name_dict[s]}: {json.loads(message)['message']}")
                        print(chat_packet(json.loads(message)["message"], name_dict[s]))

                        for user_s in name_dict:
                            user_s.send(chat_packet(json.loads(message)["message"], name_dict[s]).encode())


def usage():
    print("usage: chatserver.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))