# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 23:36:31 2017

@author: rohit
"""

from socket import *
import threading
import tkinter
from tkinter import *
from functools import partial
from AES_Security import *

clientSocket = None
clientChatTextDictionary = {}
clientInputTextDictionary = {}
clientSendButtonDictionary = {}
private_key ="CyberBullying"

top = tkinter.Tk()
scrollBar = Scrollbar(top, orient="vertical")
scrollBar.pack(side="right",fill="y")

new_user_frame = Frame(top)
new_user_frame.pack()

user_name_label = Label(new_user_frame, text="Currently Logged in User Name:", relief=RAISED)
user_name_label.pack()

logged_in_user_name = tkinter.StringVar()
logged_in_user_name_label = Label(new_user_frame, textvariable=logged_in_user_name, relief=RAISED)
logged_in_user_name_label.pack()

user_name_text = Text(new_user_frame, height=1)
user_name_text.pack()


def new_chat_window():

    user_name = user_name_text.get("1.0","end-1c")
    user_name_text.delete("1.0", "end-1c")
    print("Opening chat window for user: ",user_name)
    new_chat_frame = Frame(top)
    new_chat_frame.pack()

    user_chat_label = Label(new_chat_frame, text=user_name, relief=RAISED)
    user_chat_label.pack()

    user_chat_text = Text(new_chat_frame, height=5)
    user_chat_text.pack()
    clientChatTextDictionary.update({user_name: user_chat_text})

    user_input_text = Text(new_chat_frame, height=1)
    user_input_text.pack()
    clientInputTextDictionary.update({user_name: user_input_text})

    def send_msg(toWhom, user_input_text, user_chat_text):
        towhom = toWhom
        msg = user_input_text.get("1.0", "end-1c")
        user_input_text.delete("1.0","end-1c")
        concatinatedMsg = towhom + "~~" + msg
        
        #Encrypt data before sending
        aes_algo =  AESAlgorithm(private_key)
        encrypted_msg = aes_algo.encrypt(concatinatedMsg)
        
        clientSocket.send(encrypted_msg)
        user_chat_str = user_chat_text.get("1.0", "end-1c")
        user_chat_text.delete("1.0", "end-1c")
        user_chat_text.insert("end", user_chat_str + "\nYou:" + msg)
        user_chat_text.see(tkinter.END)
        user_chat_text.update()

    #send_button = tkinter.Button(new_chat_frame, text="Send", command=lambda :send_msg(user_name,user_input_text.get("1.0","end-1c")))
    send_button = tkinter.Button(new_chat_frame, text="Send", command=lambda: send_msg(user_name, user_input_text,user_chat_text))
    send_button.pack()
    clientSendButtonDictionary.update({user_name: send_button})


new_chat_button = tkinter.Button(new_user_frame, text="Chat", command=new_chat_window)
new_chat_button.pack()



class ServerListener(threading.Thread):
    def __init__(self, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket

    def run(self):
        while True:
            encrypted_msg = self.clientSocket.recv(5000)
            #Decrypt data before sending
            aes_algo =  AESAlgorithm(private_key)
            response = aes_algo.decrypt(encrypted_msg)

            #if response is None:
                #time.sleep(10)
            #    continue
            #else:
            print("Original msg received on client side:",response)
            fromUser = response.split("~~")[0]
            responseMsg = response.split("~~")[1]
            print("\nFrom :", fromUser)
            print("\nMsg :", responseMsg)
            user_chat_text = clientChatTextDictionary.get(fromUser)
            user_chat_str = user_chat_text.get("1.0", "end-1c")
            user_chat_text.delete("1.0", "end-1c")
            user_chat_text.insert("end", user_chat_str + "\n" +fromUser+":" +responseMsg)
            user_chat_text.see(tkinter.END)
            user_chat_text.update()


serverName = "149.162.174.254"
serverPort = 12000
#serverName = sys.argv[1]
#serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
username = input ("Enter Username:")
logged_in_user_name.set(username)
#TODO add user and password to handle login
clientSocket.send(username.encode())
thread = ServerListener(clientSocket)
thread.start()
top.mainloop()

clientSocket.close()
