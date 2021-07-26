# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import sys
from threading import Thread

from PyQt5 import QtCore, QtWidgets

from server_cls import Server
from storage_sqlite import PATH, Storage, User, History_Message


class Ui_MainWindow(object):
    def __init__(self, mainwindow):
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)

    def setup_ui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.resize(704, 565)
        mainwindow.setStyleSheet("background-color : rgb(114, 159, 207)")
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2.setStyleSheet("border: 4px double black;")
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEdit_3.setMaximumSize(QtCore.QSize(150, 16777215))
        self.lineEdit_3.setAutoFillBackground(False)
        self.lineEdit_3.setStyleSheet("background-color: white")
        self.lineEdit_3.setText("7777")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_2.addWidget(self.lineEdit_3)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label.setStyleSheet("border: 4px double black;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit.setMaximumSize(QtCore.QSize(150, 16777215))
        self.lineEdit.setAutoFillBackground(False)
        self.lineEdit.setStyleSheet("background-color: white")
        self.lineEdit.setText("127.0.0.1")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_5.addWidget(self.pushButton_4)
        self.gridLayout.addLayout(self.verticalLayout_5, 1, 0, 1, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_3.addWidget(self.pushButton_2)
        self.gridLayout.addLayout(self.verticalLayout_3, 2, 1, 1, 1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.textBrowser.setStyleSheet("background-color: white")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_4.addWidget(self.textBrowser)
        self.gridLayout.addLayout(self.verticalLayout_4, 3, 0, 1, 2)
        mainwindow.setCentralWidget(self.centralwidget)

        self.retranslate_ui(mainwindow)
        self.pushButton_4.clicked.connect(self.server_click)
        self.pushButton.clicked.connect(self.server_list_contact)
        self.pushButton_2.clicked.connect(self.server_list_static)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

    def server_click(self):
        a = self.lineEdit.text()
        b = self.lineEdit_3.text()
        self.textBrowser.clear()
        if a != "" and b.isdigit():
            self.textBrowser.setText("Подключение удалось.")
            con = Server(a, int(b))
            server_proc = Thread(target=con.server_original)
            server_proc.daemon = True
            server_proc.start()
        else:
            self.textBrowser.setText("Подключение не удалось")

    def server_list_contact(self):
        base_data = Storage(PATH, "users")
        base_data.con_base()
        session = base_data.session_con()
        users_contacts = session.query(User).all()
        list_login = {}
        for item in users_contacts:
            list_login.update({item.id: item.login})
        self.textBrowser.setText(str(list_login))

    def server_list_static(self):
        base_data = Storage(PATH, "history_message")
        base_data.con_base()
        session = base_data.session_con()
        id_users = session.query(History_Message).group_by(History_Message.id_send).all()
        dict_static = {}
        for item in id_users:
            user_messages = session.query(History_Message).filter_by(id_send=item.id_send).count()
            dict_static.update({f"Пользователь: {item.id_send}": f"Сообщений: {user_messages}"})
        self.textBrowser.setText(str(dict_static))

    def retranslate_ui(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "TCP"))
        self.label.setText(_translate("MainWindow", "IP"))
        self.pushButton_4.setText(_translate("MainWindow", "Подключение к базе"))
        self.pushButton.setText(_translate("MainWindow", "Отобразить список всех клиентов"))
        self.pushButton_2.setText(_translate("MainWindow", "Статистика клиентов"))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(window)
    ui.setup_ui(window)

    window.show()
    sys.exit(app.exec_())
