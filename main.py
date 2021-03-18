import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import time
from PyQt5.QtCore import QTimer
import design
from port import serial_ports, speeds
import serial
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
# import face_recognition
# from matplotlib import cm
import tkinter as tk
from tensorflow import keras


class LedApp(QtWidgets.QMainWindow, design.Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Port.addItems(serial_ports())
        self.Speed.addItems(speeds)
        self.realport = None
        self.a = 0
        self.ConnectButton.clicked.connect(self.connect)
        self.EnableBtn.clicked.connect(self.start)
        self.check = False
        try:
            self.realport = serial.Serial(self.Port.currentText(), int(self.Speed.currentText()))
            self.ConnectButton.setStyleSheet("background-color: green")
            self.ConnectButton.setText('Подключено')
        except Exception as e:
            print(e)

        self.timer = QTimer()
        self.timer.timeout.connect(self.send)
        self.camera = cv2.VideoCapture(0)

        self.classNames = ['real', 'fake']

        self.faceCascade = cv2.CascadeClassifier('face.xml')

        self.model = keras.models.load_model('model.h5')

        # self.font = ImageFont.truetype('LEMONMILK-Regular.otf', 20)

        # self.window = tk.Tk()
        #
        # self.window.title("Join")
        # self.window.geometry("300x300")
        # self.window.configure(background='grey')
        # self.im = ImageTk.PhotoImage(Image.open('1.jpg'))
        # self.panel = tk.Label(self.window, image=self.im)
        # self.panel.pack(side="bottom", fill="both", expand="yes")
        self.j = 0
        self.a = ['fake', 'fake', 'fake', 'fake', 'fake']


    def start(self):
        self.timer.start(100)

    def connect(self):
        try:
            self.realport = serial.Serial(self.Port.currentText(), int(self.Speed.currentText()))
            self.ConnectButton.setStyleSheet("background-color: green")
            self.ConnectButton.setText('Подключено')
        except Exception as e:
            print(e)

    def send(self):
        if self.realport:
            testImages = []
            success, image = self.camera.read()

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 	faces = faceCascade.detectMultiScale(
            #     gray,
            #     scaleFactor=1.1,
            #     minNeighbors=5,
            #     minSize=(30, 30),
            #     flags = cv2.CASCADE_SCALE_IMAGE
            # )

            faces = self.faceCascade.detectMultiScale(gray, 1.3, 1)

            print('faces:', faces)
            # cv2.imshow('123', image)
            # time.sleep(1)
            image2 = np.array(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
            # print(face_recognition.face_encodings(image2))
            try:
                # i = face_recognition.face_locations(image2)[0]
                i = faces[0]
                self.check = True
            # print()
            except:
                print('no face for now')
                self.check = False
                # self.window.after(1, task(a))
                return
            # im = Image.fromarray(np.uint8(cm.gist_earth(image)*255))
            PIL_image = Image.fromarray(np.uint8(image2)).convert('RGB')
            # Image1 = PIL_image.crop((i[3],i[0],i[1],i[2])).resize((300, 300))
            Image1 = PIL_image.crop((i[0], i[1], i[0] + i[2], i[1] + i[3])).resize((300, 300))

            testImages.append(np.array(Image1))
            testImages = np.array(testImages)

            predictions = self.model.predict(testImages)
            print(predictions)
            for i in range(len(predictions)):
                print(i + 1, ':', self.classNames[np.argmax(predictions[i])],
                      predictions[i][np.argmax(predictions[i])] * 100, '%')
                # draw = ImageDraw.Draw(Image1)
                # a.append(classNames[np.argmax(predictions[i])])
                # draw.text((100, 250), self.classNames[np.argmax(predictions[i])] + " " + str(
                #     predictions[i][np.argmax(predictions[i])] * 100) + ' %', (255, 0, 0), font=self.font)
                self.a.append(self.classNames[np.argmax(predictions[i])])
                self.a.pop(0)
            # print(a)
            # a.clear()
            # im2 = ImageTk.PhotoImage(Image1)
            # im2  = ImageTk.PhotoImage(Image.open('1.jpg'))
            # self.panel.configure(image=im2)
            # self.panel.image = im2

            print(self.a)
            if self.a == ['real', 'real', 'real', 'real', 'real'] and self.check:
                print('OPENED')
                self.realport.write(b'd')
                # self.timer.timeout()
                time.sleep(5)
                self.realport.write(b'e')
                self.a = ['fake', 'fake', 'fake', 'fake', 'fake']
                print('CLOSED')
            else:
                print('NOT OPENED')
                # self.realport.write(b'e')
                # self.opened = 0

            # panel = tk.Label(window, image = img)

            # path = "1.jpg"

            # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
            # img = ImageTk.PhotoImage(Image.open(path))

            # The Label widget is a standard Tkinter widget used to display a text or image on the screen.

            # The Pack geometry manager packs widgets in rows or columns.
            # window.after(1, task(a))
            # print(self.a)
            # if self.a == ['real', 'real', 'real', 'real', 'real']:
            #     print('!!!!')
            #     self.realport.write(b'e')
            # else:
            #     self.realport.write(b'd')
            # Start the GUI
            # window.mainloop()

            # if self.a == 0:
            #     self.realport.write(b'e')
            #     print('1')
            #     self.a = 1
            # else:
            #     self.realport.write(b'd')
            #     print('2')
            #     self.a = 0


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LedApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
