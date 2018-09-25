from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
import threading
import pickle
import colors
import atexit

import time


def log(msg):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(
        '%s:   %s :%s ' %
        (current_time,
         threading.current_thread().getName(),
         msg))


def accept_incoming_connections(clients_list_lock):
    while True:
        try:
            client, client_address = SERVER.accept()
            log("%s:%s has connected." % client_address[:])
            addresses[client] = client_address
            threading.Thread(
                target=handle_client,
                args=(
                    client,
                    clients_list_lock,
                ),
                name='client %s:%s thread' %
                client_address[:]).start()
        except Exception as err:
            log('error in accept_incoming_connections: %s' % err)
            break
    SERVER.close()


def create_server_json_msg(text):
    server_msg = create_json_msg(user_name='Server',
                                 text=text,
                                 user_color='black')
    return server_msg


def create_json_msg(user_name, text, user_color):
    sending_time = time.strftime("%H:%M", time.localtime())
    new_msg = {
        'user_name': user_name,
        'text': text,
        'time': sending_time,
        'user_color': user_color
    }
    return new_msg


def handle_client(client, clients_list_lock):
    log('Start thread for this client')
    incoming_msg = pickle.loads(client.recv(BUFSIZ))
    log('Server receive register message \n %s' % incoming_msg)
    welcome = 'Welcome %s! If you ever want to quit,' \
              ' type {quit} to exit\n' % incoming_msg['user_name']
    welcome_msg = create_server_json_msg(text=welcome)
    client.send(bytes(pickle.dumps(welcome_msg)))
    log('Send to %s \n msg= %s' % (client.getsockname(), welcome_msg))
    has_join = "%s has joined the chat!\n" % incoming_msg['user_name']
    has_join_msg = create_server_json_msg(has_join)
    broadcast(has_join_msg, clients_list_lock)
    with clients_list_lock:
        clients[client] = incoming_msg['user_name']
    client_color = colors.get_color()
    while True:
        try:
            incoming_msg = client.recv(BUFSIZ)
            incoming_msg = pickle.loads(incoming_msg)
        except EOFError:  # Possibly client has left brutality the chat.
            if incoming_msg.decode("utf8") == '':
                incoming_msg = {
                    'text': "{quit}\n"  # Back to safety quit scenario
                }
        if incoming_msg['text'] != "{quit}\n":
            log('Incoming message from %s \n message = %s'
                % (client.getsockname(), incoming_msg))
            incoming_msg['user_color'] = client_color
            log('Broadcasting the message')
            broadcast(incoming_msg, clients_list_lock)
        else:
            log('Client %s:%s has disconnected' % client.getsockname())
            left_client = client.getsockname()
            with clients_list_lock:
                client.close()
                log('client %s:%s deleted' % left_client)
                has_left = "%s has left the chat.\n" % clients[client]
                del clients[client]
            has_left_msg = create_server_json_msg(has_left)
            log('Broadcasting message %s' % has_left[:-2])
            broadcast(has_left_msg, clients_list_lock)
            break
    log('thread is finished')


def broadcast(msg, clients_list_lock):
    log('Start broadcasting \n %s' % msg)
    msg = bytes(pickle.dumps(msg))
    with clients_list_lock:
        for sock in clients:
            sock.send(msg)
            log('sent to %s:%s' % sock.getsockname())
    log('Finish broadcasting')


def close_server(clients_list_lock):
    with clients_list_lock:
        log('Closing the server')
        SERVER.close()
    log('Server is closed')


def get_my_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # I know this is a hack but it is the shortest way.
    my_ip = (s.getsockname()[0])
    s.close()
    return my_ip


def start_listen():
    tries = 0
    while True:
        try:
            SERVER.bind(ADDR)
            break
        except OSError as e:
            # Address in use, if server recovers it happens
            if e.errno == 48:
                print('Address in use try to reconnect in 10 seconds')
                time.sleep(10)
                tries += 1
                if tries > 1:
                    print('Address is in use for more than 30 seconds, exit program')
                    exit(0)
            pass


HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
clients = {}
addresses = {}
start_listen()
local_ip = get_my_ip()
clients_list_lock = threading.Lock()
SERVER.listen(50)  # Listens for 50 connections at max.
atexit.register(close_server, args=(clients_list_lock,))
print("Server is listnening on %s" % local_ip)
ACCEPT_THREAD = threading.Thread(
    target=accept_incoming_connections,
    args=(clients_list_lock,),
    name='accept_connections_thread')
ACCEPT_THREAD.start()  # Starts the infinite loop.
ACCEPT_THREAD.join()
