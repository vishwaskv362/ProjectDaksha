import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from datetime import date
import pandas as pd
import csv
#from twilio.rest import Client
from firebase import firebase
import pyttsx3
import smtplib
server = smtplib.SMTP_SSL('smtp.gmail.com',465)
server.login("attendanceautomated@gmail.com","IrichIFL5877")

engine = pyttsx3.init()


FBConn = firebase.FirebaseApplication('https://daksha-891e3.firebaseio.com/', None)

str_list = []
time_list = []
#client = Client('AC5f29f7010f4cf35e9ebcfdf32f968c9b', 'c12cf7227152e1d2a2786a06e7543c1d')
#from_whatsapp_number = ('whatsapp:+14155238886')
#to_whatsapp_number = ('whatsapp:+919148413281')
print('Bigining Encoding')
path = "/home/pi/DAKSHA/dataset"
images = []
className = []
mylist = os.listdir(path)
myList = os.listdir(path)
filename = "attendance.csv"
f = open(filename, "w+")
f.close()
#print("Total Classes Detected:",len(myList))
for x,cl in enumerate(myList):
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        className.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(img)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('attendance.csv','r+') as f:
        myDataList = f.readlines()
        nameList = []
        
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            today = date.today()
            d4 = today.strftime("%b-%d-%Y")
            dtString = now.strftime('%H:%M:%S')
            dtString2 = now.strftime('%H')
            f.writelines(f'\n{name},{dtString}')
            while True:
                 result = FBConn.post('/PresentList/'+str(d4)+'/'+str(dtString2),name)
                 str_list.append(name)
                 time_list.append(str(dtString))
                 engine.say("Welcome "+name+" Your Attendance has been marked")
                 engine.setProperty('volume',0.5)
                 voices = engine.getProperty('voices')
                 engine.setProperty('voice',voices[3].id)
                 engine.runAndWait()
                 break

encodeListKnown = findEncodings(images)
print('Encodings Complete')
cap = cv2.VideoCapture(0)
 
while True:
    success, img = cap.read()
    #img = captureScreen()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
 
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)
 
        if matches[matchIndex]:
            name = className[matchIndex].upper()
            #print(name)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
 
    cv2.imshow('Webcam',img)
    today = date.today()
    date_str = today.strftime("%b-%d-%Y")
    if cv2.waitKey(20) & 0xFF == ord('q'):
        ret_str=''
        for i in range(len(str_list)):
            ret_str = ret_str + str_list[i] +',' +' '
        #client.messages.create(body='Present List for date '+str(date_str)+' is '+ret_str, from_=from_whatsapp_number, to=to_whatsapp_number)
        server.sendmail("attendanceautomated@gmail.com",["abhishekvasudev03@gmail.com","kvvishwas6@gmail.com"],'Present List for date '+str(date_str)+' is '+ret_str)
        server.quit()
        break
    
ser.close()

