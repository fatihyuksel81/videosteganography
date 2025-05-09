from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox, QStatusBar
import basicsteganography
import videosteganography
import os
import shutil
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.stegoText = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.stegoText.setGeometry(QtCore.QRect(120, 240, 113, 32))
        self.stegoText.setObjectName("stegoText")
        self.encodeBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.encodeBtn.setGeometry(QtCore.QRect(130, 280, 88, 34))
        self.encodeBtn.setObjectName("encodeBtn")
        self.decodeBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.decodeBtn.setGeometry(QtCore.QRect(450, 280, 88, 34))
        self.decodeBtn.setObjectName("decodeBtn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        self.menuvideo_steganografi_uygulamas = QtWidgets.QMenu(parent=self.menubar)
        self.menuvideo_steganografi_uygulamas.setObjectName("menuvideo_steganografi_uygulamas")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar) 
        self.menubar.addAction(self.menuvideo_steganografi_uygulamas.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.encodeBtn.clicked.connect(self.encode_message)
        self.decodeBtn.clicked.connect(self.decode_message)

        self.temp_dir = "temp_frames"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        self.temp_dir_path = os.path.abspath(self.temp_dir)


        self.input_video_path = "C:\\Users\\PC\\Downloads\\file.avi" 
        self.output_video_path = "stegovideo.avi"

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Video Steganografi Uygulaması"))
        self.encodeBtn.setText(_translate("MainWindow", "Encode"))
        self.decodeBtn.setText(_translate("MainWindow", "Decode"))
        self.menuvideo_steganografi_uygulamas.setTitle(_translate("MainWindow", "Video Steganografi Uygulaması"))

    def encode_message(self):
        message = self.stegoText.text()
        if not message:
            self.show_message("Hata", "Lütfen encode edilecek bir mesaj girin.")
            return

        try:
            videosteganography.splitframe(self.input_video_path, self.temp_dir_path)
            image_files = [os.path.join(self.temp_dir_path, f) for f in os.listdir(self.temp_dir_path) if f.endswith((".png"))]
            image_files.sort(key=videosteganography.numerical_sort)
            basicsteganography.encode(image_files, message)
            fps = videosteganography.get_video_fps(self.input_video_path)
            boyut = videosteganography.get_video_boyut(self.input_video_path)
            videosteganography.generate_video(self.output_video_path, self.temp_dir_path, fps, boyut)
            self.show_message("Başarılı", "Mesaj başarıyla encode edildi.")
        except Exception as e:
            self.show_message("Hata", f"Encode işlemi sırasında bir hata oluştu: {str(e)}")
        finally:
            self.cleanup_temp_dir()

    def decode_message(self):
        try:
            videosteganography.splitframe(self.output_video_path, self.temp_dir_path) 
            image_files = [os.path.join(self.temp_dir_path, f) for f in os.listdir(self.temp_dir_path) if f.endswith((".png"))]
            image_files.sort(key=videosteganography.numerical_sort)
            decoded_message = basicsteganography.decode(image_files)
            self.show_message("Decode Edilen Mesaj", decoded_message)
        except Exception as e:
            self.show_message("Hata", f"Decode işlemi sırasında bir hata oluştu: {str(e)}")
        finally:
            self.cleanup_temp_dir()

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def cleanup_temp_dir(self):
        """
        Geçici dizini ve içeriğini temizler.
        """
        if os.path.exists(self.temp_dir_path):
            shutil.rmtree(self.temp_dir_path)
            print(f"Geçici dizin silindi: {self.temp_dir_path}")
        else:
            print(f"Geçici dizin zaten yoktu: {self.temp_dir_path}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
