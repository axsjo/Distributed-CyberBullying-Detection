# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 10:21:04 2017

@author: rohit
"""

from socket import *
from AES_Security import *
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

private_key ="CyberBullying"
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
    
bullyingServerPort = 15000
bullyingServerSocket = socket(AF_INET,SOCK_STREAM)
bullyingServerSocket.bind(('',bullyingServerPort))
bullyingServerSocket.listen(100)

print ('Bullying  server is ready to receive')
bullyingConnectionSocket, addr = bullyingServerSocket.accept()
print ('Communication Server is connected ')
print ('Connection Information :', addr)
print ('Socket Info',bullyingConnectionSocket)

while True:
    encrypted_msg = bullyingConnectionSocket.recv(5000)
    
    #Decrypt data before sending
    aes_algo =  AESAlgorithm(private_key)
    msg = aes_algo.decrypt(encrypted_msg)
    bullying_output = detectBullying(msg)
    print ('Msg:',msg)
    print ('Bullying output:',bullying_output)
    
    #Encrypt data before sending
    encrypted_msg = aes_algo.encrypt(bullying_output)
    bullyingConnectionSocket.send(encrypted_msg)
    
