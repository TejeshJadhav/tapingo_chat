import pickle
from socket import AF_INET, socket, SOCK_STREAM

BUFSIZ = 1024


def receive(soc, recive_que):
    while True:
        try:
            msg = soc.recv(BUFSIZ)
            msg = pickle.loads(msg)
            recive_que.put(msg)
        except OSError:  # Possibly client has left the chat.
            break
            # finish this thread
        except EOFError:  # Possibly client has left the chat.
            if msg.decode("utf8") == '':
                print('server closed connection')
                soc.close()
                break
                # could be handle by exit(0)
                # or produce a msg(text = lost connection)


def send_new_msg(msg, soc):
    try:
        soc.send(bytes(pickle.dumps(msg)))
        if msg['text'] == "{quit}\n":
            soc.close()
    except BrokenPipeError as e:  # Possibly client has left the chat.
        print('socket is closed')
        # Could be handle by exit(0)
        # or produce a msg to the screen(text = lost connection)


def create_socket(address):
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.settimeout(3)
        client_socket.connect(address)
        client_socket.settimeout(None)
        return client_socket
    except Exception as err:
        raise err
