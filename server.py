import base64
import io
import mysql.connector
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
import face_recognition
import os
import coba_subprocess

from multi_recognition import multirecog

#Connect to database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="flask"
)
c = db.cursor(buffered=True)

app = Flask(__name__)

images = []
classNames = []

# Encoding List Image Known
def saveEncodings(images):
    path = 'imageAttendance'
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

saveEncodings(images)
encodeListKnown = findEncodings(images)
print('Encoding Complete')

@app.route("/")
def home():
    return "Hello, World!"

#RECOGNITION
@app.route("/recog", methods=["POST"])
def recognition():
    if request.method == 'POST':
        input_data = request.get_json(force=True)
        # print(input_data)
        imgdata = base64.b64decode(input_data['image_base64'])
        imagedata = Image.open(io.BytesIO(imgdata))
        imgnew = cv2.cvtColor(np.array(imagedata), cv2.COLOR_BGR2RGB)

        output = multirecog(encodeListKnown, classNames, imgnew)

        for i in output:
            print(i)

        respons = {'output' : output}

        return jsonify(respons)

#PresenceIn
@app.route("/recogIn", methods=["POST"])
def presenceIn():
    if request.method == 'POST':
        input_data = request.get_json(force=True)
        # print(input_data)
        imgdata = base64.b64decode(input_data['image_base2'])
        imagedata = Image.open(io.BytesIO(imgdata))
        imgnew = cv2.cvtColor(np.array(imagedata), cv2.COLOR_BGR2RGB)

        name = input_data['name']
        en64 = input_data['image_base2']

        c.execute("INSERT INTO `presence_in` (`name`,`photo`) VALUES (%s,%s)", (name, en64))
        db.commit()

        respons = {
            'status': 'Success',
            'message': 'Data Berhasil Ditambahkan!',
        }

        return jsonify(respons)

#PresenceIn
@app.route("/recogOut", methods=["POST"])
def presenceOut():
    if request.method == 'POST':
        input_data = request.get_json(force=True)
        # print(input_data)
        imgdata = base64.b64decode(input_data['image_base2'])
        imagedata = Image.open(io.BytesIO(imgdata))
        imgnew = cv2.cvtColor(np.array(imagedata), cv2.COLOR_BGR2RGB)

        name = input_data['name']
        en64 = input_data['image_base2']

        c.execute("INSERT INTO `presence_out` (`name`,`photo`) VALUES (%s,%s)", (name, en64))
        db.commit()

        respons = {
            'status': 'Success',
            'message': 'Data Berhasil Ditambahkan!',
        }

        return jsonify(respons)

#REGISTER
@app.route("/regis", methods=["POST"])
def register():
    if request.method == 'POST':
        input_data = request.get_json(force=True)
        name = input_data['name']
        en64 = input_data['image_base64']

        c.execute("INSERT INTO `db_picture` (`name`,`picture`) VALUES (%s,%s)", (name, en64))
        db.commit()

        #imgdata = base64.b64decode(input_data['image_base64'])
        #imagedata = Image.open(io.BytesIO(imgdata))
        #imagedata.save("imageAttendance/{}.jpg".format(name))

        respons = {
            'status': 'Success',
            'message': 'User Berhasil Ditambahkan!',
        }

        # saveEncodings(images)
        # findEncodings(images)
        # print(classNames)
        # print('Encoding Complete')

        return jsonify(respons)

#Record In
@app.route('/recordIn', methods=['POST'])
def recordin():
    if request.method == 'POST':
        # Query untuk mengambil data dari database
        query = "SELECT name, photo, presence_time FROM presence_in"
        c.execute(query)

        # Mengambil semua baris data
        rows = c.fetchall()

        # Membuat list dictionary dari data
        data = []
        for row in rows:
            item = {
                'name': row[0],
                'photo': row[1].decode('utf-8'),
                'presence_time': row[2]
            }
            data.append(item)

        return jsonify(data)

#Record Out
@app.route('/recordOut', methods=['POST'])
def recordOut():
    if request.method == 'POST':
        # Query untuk mengambil data dari database
        query1 = "SELECT name, photo, presence_time FROM presence_out"
        c.execute(query1)

        # Mengambil semua baris data
        rows = c.fetchall()

        # Membuat list dictionary dari data
        data = []
        for row in rows:
            item = {
                'name': row[0],
                'photo': row[1].decode('utf-8'),
                'presence_time': row[2]
            }
            data.append(item)

        return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)