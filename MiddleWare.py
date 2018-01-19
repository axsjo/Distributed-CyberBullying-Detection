# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 23:35:49 2017

@author: rohit
"""

from socket import *
import threading
from AES_Security import *
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords


socketInfoDictionary = {}
private_key ="CyberBullying"
bullyingClientSocket = None

#Backup Bullying capability 
model = joblib.load(r'D:\Fall 17\DC Project\DC project\Project\model.pkl')
X_token = joblib.load(r'D:\Fall 17\DC Project\DC project\Project\x_token.pkl')

vectorizer = CountVectorizer()

X_bagOfWords = vectorizer.fit_transform(X_token)
# importing stop words and using Regex tokenizer to remove punctuations  
stopWords = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

def detectBullying(userInput):
    # ==================================================================================
    #userInput = raw_input('Enter your tweet : ')
    
    userInput.strip()
    
    words = tokenizer.tokenize(userInput.lower())
    
    wordsFiltered = []
    
    for w in words:
        if w not in stopWords:
            wordsFiltered.append(w)
    
    wordsFiltered = ' '.join(wordsFiltered)            
    
    userInputToken = []
    userInputToken.append(wordsFiltered)            
    
    del w
    del wordsFiltered
    del userInput
    del words
    
    userInputVector =  vectorizer.transform(userInputToken)
    
    userPredict = model.predict(userInputVector)
    
    if userPredict == 1:
        return "drop"
#    if "fuck" in msg:
#        return "drop"
    return "forward"


class ClientListener(threading.Thread):
    def __init__(self, userName, clientSocket, addr):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.addr = addr
        self.userName = userName

    def run(self):
        while True:
            encrypted_msg = self.clientSocket.recv(5000)
            #Decrypt data before sending
            aes_algo =  AESAlgorithm(private_key)
            requestMsg = aes_algo.decrypt(encrypted_msg)
          
            
            #if requestMsg is None:
                #time.sleep(10)
            #   continue
            print("Original msg received at server side:",requestMsg)
            towhom = requestMsg.split("~~")[0]
            receivedMsg = requestMsg.split("~~")[1]
            
            #Detect bullying 
            try:
                encrypted_msg_to_bullying_server = aes_algo.encrypt(receivedMsg)
                bullyingClientSocket.send(encrypted_msg_to_bullying_server)
                encrypted_msg_from_bullying_server = bullyingClientSocket.recv(5000)

                bullying_output = aes_algo.decrypt(encrypted_msg_from_bullying_server)
            except Exception as e:
                #print (e)
                #directly call trained model
                print('Bullying server is crashed hence main server is taking over bullying server')
                bullying_output = detectBullying(receivedMsg)

            if "drop" in bullying_output:
                print('Dropping msg')
                continue
            
            #broadcast msg
            if "broadcast" in towhom.lower():
                print('broadcasting msg...')
                responseMsg = "broadcast~~" +self.userName+":"+ receivedMsg
                #Encrypt data before sending
                aes_algo =  AESAlgorithm(private_key)
                encrypted_msg = aes_algo.encrypt(responseMsg)
                for username,userSocket in socketInfoDictionary.items():
                    userSocket.send(encrypted_msg)
                continue
            
            #unicast msg
            socketInfo = socketInfoDictionary.get(towhom)
            if socketInfo is None:
                #time.sleep(10)
                continue
            if not receivedMsg is None:
                responseMsg = self.userName + "~~" + receivedMsg
                #Encrypt data before sending
                aes_algo =  AESAlgorithm(private_key)
                encrypted_msg = aes_algo.encrypt(responseMsg)

                socketInfo.send(encrypted_msg)
                print("ACK of msg sent")
                if receivedMsg == 'exit':
                    print('Exit request')
                    self.clientSocket.close()
                    socketInfoDictionary.__delitem__(self.userName)
                    break

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(100)

print ('The server is ready to receive')
print ('Waiting for bullying server to connect')

#Connect to bullying server
bullyingServerName = "127.0.0.1"
bullyingServerPort = 15000

bullyingClientSocket = socket(AF_INET, SOCK_STREAM)
bullyingClientSocket.connect((bullyingServerName,bullyingServerPort))

print ('Connected to bullying server')

while True:
    connectionSocket, addr = serverSocket.accept()
    print ('Connection Information :', addr)
    print('Socket Infor',connectionSocket)
    username = connectionSocket.recv(5000).decode()
    print ('Client name:',username)
    socketInfoDictionary.update({username: connectionSocket})
    #Insert client information into table
    #DatabaseOperation().InsertClientInformation(username,connectionSocket,addr)
    thread = ClientListener (username, connectionSocket, addr)
    thread.start()
