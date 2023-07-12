import datetime
import io
import sys
import cv2
import face_recognition
import cv2
import os
import numpy as np
import mysql.connector
import base64
import requests
import json
import threading
import subprocess
import time

from PIL import Image
from flask import Flask, request, jsonify
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QVBoxLayout, QMessageBox, QTableWidgetItem, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QTimer, Qt, QDate
from time import ctime

# Fungsi untuk memulai subprocess
def start_subprocess():
    process = subprocess.Popen(['python', 'server.py'], shell=True)
    return process

# Fungsi untuk menghentikan subprocess
def stop_subprocess(process):
    process.terminate()
    process.wait()

# Fungsi untuk me-restart subprocess
def restart_subprocess():
    stop_subprocess(subprocess_instance)
    time.sleep(2)  # Jeda 2 detik sebelum memulai kembali subprocess
    subprocess_instance1 = start_subprocess()
    return subprocess_instance1

# Start the subprocess
subprocess_instance = start_subprocess()

# Tunggu beberapa saat
time.sleep(1)

#Directory of picture
directory = os.getcwd() + '/imageAttendance/'

#MENU WINDOW
class MultiFaceMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Face Recognition System")
        self.resize(525, 426)
        self.menu_win = QLabel("WINDOW MENU", self)
        self.menu_win.move(150, 20)
        self.menu_win.resize(231, 44)
        self.menu_win.setFont(QFont('Times', 18))

        self.btn_regis = QPushButton("Registrasi", self)
        self.btn_regis.move(130, 90)
        self.btn_regis.resize(250, 50)
        self.btn_regis.setFont(QFont('Times', 10))
        self.btn_regis.clicked.connect(self.regis_win)

        self.btn_present = QPushButton("Presensi", self)
        self.btn_present.move(130, 160)
        self.btn_present.resize(250, 50)
        self.btn_present.setFont(QFont('Times', 10))
        self.btn_present.clicked.connect(self.present_win)

        self.btn_record = QPushButton("Record Presensi", self)
        self.btn_record.move(130, 230)
        self.btn_record.resize(250, 50)
        self.btn_record.setFont(QFont('Times', 10))
        self.btn_record.clicked.connect(self.record_win)

        # self.btn_history = QPushButton("History", self)
        # self.btn_history.move(130, 270)
        # self.btn_history.resize(250, 50)
        # self.btn_history.setFont(QFont('Times', 10))

        self.btn_exit = QPushButton("Keluar", self)
        self.btn_exit.move(130, 300)
        self.btn_exit.resize(250, 50)
        self.btn_exit.setFont(QFont('Times', 10))
        self.btn_exit.clicked.connect(self.closeGui)

    def present_win(self):
        self.pre_win = PresentWindow()
        self.pre_win.show()
        self.hide()

    def regis_win(self):
        self.reg_win = RegisWindow()
        self.reg_win.show()
        self.hide()

    def record_win(self):
        self.record_win = RecordWindow()
        self.record_win.show()
        self.hide()

    def closeGui(self):
        exit()

#PRESENCE GUI
class PresentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WINDOW PRESENSI")
        self.resize(1070, 700)
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.presen = QLabel("WINDOW PRESENSI", self)
        self.presen.move(380, 20)
        self.presen.resize(291, 44)
        self.presen.setFont(QFont('Times', 18))

        self.camera1 = QLabel(self)
        self.camera1.setFixedSize(640, 480)
        self.camera1.move(40, 80)

        # Tanggal dan Waktu saat ini
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")

        layout_grid1 = QGridLayout()
        layoutdate1 = QHBoxLayout()
        self.dateText1 = QLabel("Tanggal :", self)
        self.dateText1.move(720, 80)
        self.dateText1.resize(120, 44)
        self.dateText1.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        self.fill_date1 = QLabel("-", self)
        self.fill_date1.move(800, 80)
        self.fill_date1.resize(135, 44)
        self.fill_date1.setFont(QFont('Times', 10))
        self.fill_date1.setText(current_date)
        layoutdate1.addWidget(self.dateText1)
        layoutdate1.addWidget(self.fill_date1)
        # -------------------------------------------------------------
        layouttime1 = QHBoxLayout()
        self.timeText1 = QLabel("Waktu   :", self)
        self.timeText1.move(720, 140)
        self.timeText1.resize(120, 44)
        self.timeText1.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        self.fill_time1 = QLabel("-", self)
        self.fill_time1.move(800, 140)
        self.fill_time1.resize(125, 44)
        self.fill_time1.setFont(QFont('Times', 10))
        self.fill_time1.setText(current_time)
        layouttime1.addWidget(self.timeText1)
        layouttime1.addWidget(self.fill_time1)
        # -------------------------------------------------------------
        layout_grid1.addLayout(layoutdate1, 0, 0)
        layout_grid1.addLayout(layouttime1, 1, 0)

        # Presence in & out
        layout_presence = QHBoxLayout()
        self.presence_in = QPushButton("Presensi Masuk", self)
        self.presence_in.move(40, 590)
        self.presence_in.resize(316, 50)
        self.presence_in.setFont(QFont('Times', 10))
        self.presence_in.clicked.connect(self.doPresenceIn)
        # -------------------------------------------------------------
        self.presence_out = QPushButton("Presensi Keluar", self)
        self.presence_out.move(360, 590)
        self.presence_out.resize(316, 50)
        self.presence_out.setFont(QFont('Times', 10))
        self.presence_out.clicked.connect(self.doPresenceOut)
        # -------------------------------------------------------------
        layout_presence.addWidget(self.presence_in)
        layout_presence.addWidget(self.presence_out)

        # MASIH TAHAP PENGERJAAN
        # INFO BOX
        self.info_box1 = QGroupBox("Informasi", self)
        self.info_box1.move(720, 250)
        self.info_box1.resize(305, 311)
        self.info_box1.setFont(QFont('Times', 10))
        #########################################################
        layout_grid2 = QGridLayout()
        layoutname1 = QVBoxLayout()
        self.nameText1 = QLabel("Nama :", self)
        self.nameText1.move(730, 340)
        self.nameText1.resize(228, 43)
        self.nameText1.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        self.fill_name1 = QLabel("-", self)
        self.fill_name1.move(730, 380)
        self.fill_name1.resize(229, 35)
        self.fill_name1.setFont(QFont('Times', 10))

        layoutname1.addWidget(self.nameText1)
        layoutname1.addWidget(self.fill_name1)
        # -------------------------------------------------------------
        layoutstatus1 = QHBoxLayout()
        self.statusText1 = QLabel("Status :", self)
        self.statusText1.move(730, 430)
        self.statusText1.resize(110, 33)
        self.statusText1.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        self.fill_status1 = QLabel("-", self)
        self.fill_status1.move(810, 430)
        self.fill_status1.resize(120, 33)
        self.fill_status1.setFont(QFont('Times', 10))
        #self.fill_time1.setText(current_time)
        layoutstatus1.addWidget(self.statusText1)
        layoutstatus1.addWidget(self.fill_status1)
        # -------------------------------------------------------------
        layout_grid2.addLayout(layoutdate1, 0, 0)
        layout_grid2.addLayout(layouttime1, 1, 0)

        # Button Menu
        self.btn_menu1 = QPushButton("Menu", self)
        self.btn_menu1.move(777, 590)
        self.btn_menu1.resize(250, 50)
        self.btn_menu1.setFont(QFont('Times', 10))
        self.btn_menu1.clicked.connect(self.menu1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(15)

    def update(self):
        ret, frame = self.video.read()

        if ret:
            imgC = frame.copy()
            # img = captureScreen()
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)

            for (top, right, bot, left) in facesCurFrame:
                top *= 4
                right *= 4
                bot *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bot), (0, 255, 0), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qImg = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.camera1.setPixmap(pixmap)

    def doPresenceIn(self):
        ret, frame = self.video.read()

        if ret:
            imgC = frame.copy()
            # img = captureScreen()
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)

            for (top, right, bot, left) in facesCurFrame:
                top *= 4
                right *= 4
                bot *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bot), (0, 255, 0), 2)
                # cv2.putText(frame, name, (left + 6, top - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qImg = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.camera1.setPixmap(pixmap)

            temp = []

            if facesCurFrame:
                print("Initialize . . .")

                res, img = cv2.imencode('.jpg', imgC)
                data = base64.b64encode(img).decode('utf-8')

                rawJson = {
                    "image_base64": data
                }

                response_recognition = requests.post(url='http://127.0.0.1:5000/recog', data=json.dumps(rawJson))
                result = (response_recognition.json())

                for value in result.values():
                    for value1 in value:
                        bulkname = value1

                        rawJson2 = {
                            "name" : bulkname,
                            "image_base2" : data
                        }

                        response_recognition2 = requests.post(url='http://127.0.0.1:5000/recogIn', data=json.dumps(rawJson2))
                        result2 = response_recognition2.json()

                        #print(bulkname)
                        temp.append(bulkname)

                self.fill_name1.setText(str(temp))
                print(str(temp))

                self.fill_status1.setText('Presensi Masuk')
            else:
                print("No Face Detected")
                self.fill_name1.setText("Wajah tidak terdeteksi")

    def doPresenceOut(self):
        ret, frame = self.video.read()

        if ret:
            imgC = frame.copy()
            # img = captureScreen()
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)

            for (top, right, bot, left) in facesCurFrame:
                top *= 4
                right *= 4
                bot *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bot), (0, 255, 0), 2)
                # cv2.putText(frame, name, (left + 6, top - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qImg = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.camera1.setPixmap(pixmap)

            temp = []

            if facesCurFrame:
                print("Initialize . . .")

                res, img = cv2.imencode('.jpg', imgC)
                data = base64.b64encode(img).decode('utf-8')

                rawJson = {
                    "image_base64": data
                }

                response_recognition = requests.post(url='http://127.0.0.1:5000/recog', data=json.dumps(rawJson))
                result = (response_recognition.json())

                for value in result.values():
                    for value1 in value:
                        bulkname = value1

                        rawJson2 = {
                            "name": bulkname,
                            "image_base2": data
                        }

                        response_recognition2 = requests.post(url='http://127.0.0.1:5000/recogOut', data=json.dumps(rawJson2))
                        result2 = response_recognition2.json()

                        # print(bulkname)
                        temp.append(bulkname)

                self.fill_name1.setText(str(temp))
                print(str(temp))

                self.fill_status1.setText('Presensi Keluar')
            else:
                print("No Face Detected")
                self.fill_status1.setText('Wajah tidak terdeteksi')

    def add_data_to_table(self):
        name = self.name_edit.text()
        foto = self.number_edit.text()
        #status = self.status_edit.text()

        if name and foto: #and status:
            row_count = self.table_widget.rowCount()
            self.table_widget.setRowCount(row_count + 1)

            item_name = QTableWidgetItem(name)
            item_number = QTableWidgetItem(foto)
            #item_status = QTableWidgetItem(status)

            self.table_widget.setItem(row_count, 0, item_name)
            self.table_widget.setItem(row_count, 1, item_number)
            #self.table_widget.setItem(row_count, 2, item_status)

            self.name_edit.clear()
            self.number_edit.clear()
            self.status_edit.clear()

            self.save_data(name, foto)

    def menu1(self):
        self.menu1 = MultiFaceMenu()
        self.menu1.show()
        self.hide()

#REGISTRATION GUI
class RegisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WINDOW REGISTRASI")
        self.resize(1020, 700)
        self.video2 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.registrasi = QLabel("WINDOW REGISTRASI", self)
        self.registrasi.move(350, 20)
        self.registrasi.resize(361, 44)
        self.registrasi.setFont(QFont('Times', 18))

        # Camera frame
        self.camera2 = QLabel(self)
        self.camera2.setFixedSize(640, 480)
        self.camera2.move(40, 80)

        # Tanggal dan Waktu saat ini
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        layout_grid = QGridLayout()
        layoutdate = QHBoxLayout()
        self.dateText = QLabel("Tanggal :", self)
        self.dateText.move(720, 80)
        self.dateText.resize(120, 44)
        #-------------------------------------------------------------
        self.dateText.setFont(QFont('Times', 10))
        self.fill_date = QLabel("-", self)
        self.fill_date.move(800, 80)
        self.fill_date.resize(135, 44)
        self.fill_date.setFont(QFont('Times', 10))
        self.fill_date.setText(current_date)
        layoutdate.addWidget(self.dateText)
        layoutdate.addWidget(self.fill_date)
        #-------------------------------------------------------------
        layouttime = QHBoxLayout()
        self.timeText = QLabel("Waktu   :", self)
        self.timeText.move(720, 140)
        self.timeText.resize(120, 44)
        self.timeText.setFont(QFont('Times', 10))
        #-------------------------------------------------------------
        self.fill_time = QLabel("-", self)
        self.fill_time.move(800, 140)
        self.fill_time.resize(125, 44)
        self.fill_time.setFont(QFont('Times', 10))
        self.fill_time.setText(current_time)
        layouttime.addWidget(self.timeText)
        layouttime.addWidget(self.fill_time)
        #-------------------------------------------------------------
        layout_grid.addLayout(layoutdate, 0, 0)
        layout_grid.addLayout(layouttime, 1, 0)


        # Informasi nama
        layout_nama = QHBoxLayout()
        self.nameText = QLabel("Nama :", self)
        self.nameText.move(720, 230)
        self.nameText.resize(60, 50)
        self.nameText.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Enter Your Name")
        self.nameEdit.move(790, 230)
        self.nameEdit.resize(200,50)
        self.nameEdit.setFont(QFont('Times', 10))
        # -------------------------------------------------------------
        layout_nama.addWidget(self.nameText)
        layout_nama.addWidget(self.nameEdit)

        # Status Group Box
        self.info_box2 = QGroupBox("Status", self)
        self.info_box2.move(720, 320)
        self.info_box2.resize(251, 241)
        self.info_box2.setFont(QFont('Times', 10))
        #self.info_box2.setFont(QFont.setBold(True))
        self.name_regis = QLabel("-", self)
        self.name_regis.move(730, 400)
        self.name_regis.resize(231, 79)
        self.name_regis.setFont(QFont('Times', 10))

        # Button Capture
        layout_capture = QHBoxLayout()
        self.btn_capture = QPushButton("Capture Gambar", self)
        self.btn_capture.move(40, 590)
        self.btn_capture.resize(639, 50)
        self.btn_capture.setFont(QFont('Times', 10))
        layout_capture.addWidget(self.btn_capture)
        self.btn_capture.clicked.connect(self.savename)

        # Button Menu
        self.btn_menu = QPushButton("Menu", self)
        self.btn_menu.move(720, 590)
        self.btn_menu.resize(250, 50)
        self.btn_menu.setFont(QFont('Times', 10))
        self.btn_menu.clicked.connect(self.menu2)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update2)
        self.timer.start(15)

        # self.show()

    def update2(self):
        ret2, frame2 = self.video2.read()
        if ret2:
            imgC = frame2.copy()

            # img = captureScreen()
            imgS = cv2.resize(frame2, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame2 = face_recognition.face_locations(imgS)

            # Bounding Box 1 wajah dengan dlib
            if facesCurFrame2:
                y1, x2, y2, x1 = facesCurFrame2[0]
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame2, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # crop = frame2[y1:y2, x1:x2]

            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            h2, w2, ch2 = frame2.shape
            bytesPerLine2 = ch2 * w2
            qImg2 = QImage(frame2.data, w2, h2, bytesPerLine2, QImage.Format_RGB888)
            pixmap2 = QPixmap.fromImage(qImg2)
            self.camera2.setPixmap(pixmap2)


    #BUTTON SAVE NAME
    def savename(self):
        name = self.nameEdit.text().upper()

        ret2, frame2 = self.video2.read()

        if ret2:
            imgC2 = frame2.copy()

            # img = captureScreen()
            imgS2 = cv2.resize(frame2, (0, 0), None, 0.25, 0.25)
            imgS2 = cv2.cvtColor(imgS2, cv2.COLOR_BGR2RGB)

            facesCurFrame2 = face_recognition.face_locations(imgS2)

            # Bounding Box 1 wajah dengan dlib
            if facesCurFrame2:
                y1, x2, y2, x1 = facesCurFrame2[0]
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame2, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # crop = frame2[y1:y2, x1:x2]

            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            h2, w2, ch2 = frame2.shape
            bytesPerLine2 = ch2 * w2
            qImg2 = QImage(frame2.data, w2, h2, bytesPerLine2, QImage.Format_RGB888)
            pixmap2 = QPixmap.fromImage(qImg2)
            self.camera2.setPixmap(pixmap2)

            if facesCurFrame2:
                cv2.imwrite(directory + name + ".jpg", imgC2)
                res, img = cv2.imencode('.jpg', imgC2)
                data = base64.b64encode(img).decode('utf-8')

                rawJson = {
                    "image_base64": data,
                    "name": name
                }

                response_recognition = requests.post(url='http://127.0.0.1:5000/regis', data=json.dumps(rawJson))
                print(response_recognition.json())

                self.name_regis.setText(name + ' Berhasil Ditambahkan!')

                # subprocess_instance1 = restart_subprocess()

            else:
                print("No Face Detected")
                self.name_regis.setText('Tidak terdeteksi wajah')

    #BUTTON BACK
    def menu2(self):
        self.menu2 = MultiFaceMenu()
        self.menu2.show()
        self.hide()

#RECORD WINDOW
class RecordWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WINDOW RECORD")
        self.resize(957, 705)
        self.record = QLabel("WINDOW RECORD", self)
        self.record.move(350, 20)
        self.record.resize(251, 44)
        self.record.setFont(QFont('Times', 18))

        # Button Menu
        self.btn_menu = QPushButton("Menu", self)
        self.btn_menu.move(340, 590)
        self.btn_menu.resize(250, 50)
        self.btn_menu.setFont(QFont('Times', 10))
        self.btn_menu.clicked.connect(self.menu)

        # Table
        self.name_in = QLabel("Presensi Masuk",self)
        self.name_in.move(160, 90)
        self.name_in.resize(120, 44)
        self.name_in.setFont(QFont('Times', 10))

        self.name_out = QLabel("Presensi Keluar", self)
        self.name_out.move(650, 90)
        self.name_out.resize(120, 44)
        self.name_out.setFont(QFont('Times', 10))

        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.move(40, 140)
        self.table_widget.resize(398, 411)
        self.table_widget.setColumnCount(3)

        self.table_widget1 = QtWidgets.QTableWidget(self)
        self.table_widget1.move(500, 140)
        self.table_widget1.resize(398, 411)
        self.table_widget1.setColumnCount(3)

        self.load_data()
        self.load_data1()

    def load_data(self):
        header_labels = ["Nama", "Foto", "Waktu Absen"]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        response_in = requests.post(url='http://127.0.0.1:5000/recordIn')

        if response_in.status_code == 200:
            data = response_in.json()

            self.table_widget.setRowCount(len(data))

            for row, item in enumerate(data):
                column_1 = item["name"]
                column_2 = item["photo"]
                column_3 = item["presence_time"]

                item_1 = QTableWidgetItem(column_1)
                item_2 = QTableWidgetItem(column_2)
                item_3 = QTableWidgetItem(column_3)

                self.table_widget.setItem(row, 0, item_1)
                self.table_widget.setItem(row, 1, item_2)
                self.table_widget.setItem(row, 2, item_3)
        else:
            print("Error:", response_in.status_code)

    def load_data1(self):
        header_labels1 = ["Nama", "Foto", "Waktu Absen"]
        self.table_widget1.setHorizontalHeaderLabels(header_labels1)

        response_in1 = requests.post(url='http://127.0.0.1:5000/recordOut')

        if response_in1.status_code == 200:
            data = response_in1.json()

            self.table_widget1.setRowCount(len(data))

            for row, item in enumerate(data):
                column_1 = item["name"]
                column_2 = item["photo"]
                column_3 = item["presence_time"]

                item_1 = QTableWidgetItem(column_1)
                item_2 = QTableWidgetItem(column_2)
                item_3 = QTableWidgetItem(column_3)

                self.table_widget1.setItem(row, 0, item_1)
                self.table_widget1.setItem(row, 1, item_2)
                self.table_widget1.setItem(row, 2, item_3)
        else:
            print("Error:", response_in1.status_code)


    def menu(self):
        self.menu = MultiFaceMenu()
        self.menu.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiFaceMenu()
    window.show()
    sys.exit(app.exec_())