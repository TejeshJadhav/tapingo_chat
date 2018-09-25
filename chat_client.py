# !/usr/bin/env python3
import tkinter as T
from tkinter import simpledialog

from threading import Thread
import queue

import time

import atexit

import client_socket
import colors


def connect():
    is_connected = False
    while not is_connected:
        try:
            HOST = input('Enter host: ')
            PORT = input('Enter port (default 33000): ')
            if not PORT:
                PORT = 33000
            else:
                PORT = int(PORT)
            if not HOST:
                raise Exception('Host must be filled')
            address = (HOST, PORT)
            chat_socket = client_socket.create_socket(address)
            is_connected = True
        except Exception as e:
            print('error in connection to the server: ', e)
            print('lets try again, the IP must be valid, default port is 33000')
    return chat_socket


def register():
    name = None
    while name is None:
        name = simpledialog.askstring("Input", "What is your nick name?",
                                      parent=window)
    return name


def render_incoming_msg(recieve_que):
    while True:
        try:
            msg = recieve_que.get()
            render_new_message(msg)
        except OSError as e:  # Possibly client has left the chat.
            print('err: ', e)
            print('end rendering thread')
            break


def render_new_message(msg):
    chat_body.config(state='normal')
    msg_prefix = "%s %s: " % (msg['time'], msg['user_name'])
    chat_body.insert('end', msg_prefix, msg['user_color'])
    chat_body.insert('end', msg['text'], 'body')
    chat_body.config(state='disabled')
    chat_body.see('end')


def create_json_msg(user_name, text):
    sending_time = time.strftime("%H:%M", time.localtime())
    msg = {
        'user_name': user_name,
        'text': text,
        'time': sending_time,
    }
    return msg


def send_hello(chat_socket, nickName):
    hello_msg = create_json_msg(user_name=nickName, text='Hello')
    client_socket.send_new_msg(hello_msg, chat_socket)


def send_msg():
    new_msg_text = text_input.get(1.0, 'end')
    if nickName is not None and new_msg_text is not None:
        new_msg = create_json_msg(user_name=nickName, text=new_msg_text)
        if new_msg_text != '{quit}\n':
            client_socket.send_new_msg(new_msg, chat_socket)
            text_input.delete(1.0, 'end')
        else:
            exit()


def handle_exit():
    quit_msg = create_json_msg(user_name=nickName, text='{quit}\n')
    client_socket.send_new_msg(quit_msg, chat_socket)
    try:
        window.destroy()
    except Exception:
        # window allready has been closed
        pass


### GUI Initializing ###
window = T.Tk()
window.title('Uriel Chat')
window.geometry('800x450')
upper_frame = T.Frame(window)
upper_frame.pack(side='top')

chat_frame = T.Frame(window)
chat_frame.pack()
new_msg_frame = T.Frame(window, pady=20)
new_msg_frame.pack()

# Upper frame
logo_img = T.PhotoImage(file='Tapingo_logo.gif')
logo_img = logo_img.subsample(4, 4)
logo_container = T.Label(upper_frame, image=logo_img)
logo_container.pack(fill='both')

# Chat body frame
chat_body = T.Text(chat_frame)
chat_body.insert('insert', 'hello\n')
chat_body.config(state='disabled')
chat_body.pack(side='top')
chat_body.config(width=100, height=15, bd=4, bg='gray95')
for c in colors.colors_list:
    chat_body.tag_config(c, foreground=c)

# Send Message Frame
text_input = T.Text(new_msg_frame)
text_input.pack(side='left')
text_input.config(
    width=60,
    height=4,
    highlightcolor="black",
    highlightthickness=1,
    bd=3,
    padx=3, )
send_btn = T.Button(new_msg_frame, text='SEND', command=send_msg)
send_btn.config(width=6, height=4, padx=10)
send_btn.pack(padx=20)


### start() ###
chat_socket = connect()
nickName = register()
window.title(nickName)
send_hello(chat_socket, nickName)
text_input.focus_set()

receive_que = queue.Queue()

socket_receive_thread = Thread(
    target=client_socket.receive, daemon=True, args=(
        chat_socket, receive_que,), name='socket_receive_thread')
socket_receive_thread.start()

render_incoming_msg_thread = Thread(
    target=render_incoming_msg,
    daemon=True,
    args=(
        receive_que,
    ))
render_incoming_msg_thread.start()

atexit.register(handle_exit)

window.mainloop()
