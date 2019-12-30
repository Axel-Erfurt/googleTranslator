#/usr/bin/python3
# -*- coding: utf-8 -*-
# Credits: Lewis Tian (chtian@hust.edu.cn) https://github.com/ssut/py-googletrans
# adapted 2019-12-28 by Axel Schneider https://github.com/Axel-Erfurt
# @Version : Python3.6

from mwin import Ui_MWin
 
from PyQt5.QtCore import QTranslator, QUrl, QThread, pyqtSignal, Qt, QFileInfo, QCoreApplication
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog, 
                                QMessageBox, QLabel, QHBoxLayout, QPushButton)
from  PyQt5.QtGui import QIcon
import sys
from googletrans import Translator
import re

GTransData = ''

class MyWindow(QMainWindow, Ui_MWin):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.originText.setFocus(True)
        #  Translator
        self.trans = QTranslator()
        # destination language
        self.dest = 'de-DE'
        self.lan = 1 
        # real-time translate
        self.isRealTimeTrans = False
        self.isCopyFromTrans = False
        self.connectSlots()
        self.trans.load("de")
        self.dest = "en"
        
        root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        btnIcon = root + "/google.png"
        self.hbox = QHBoxLayout()
        self.btnDE_EN = QPushButton("Deutsch > Englisch (F6)", clicked = self.toggleLanguageDE)
        self.btnDE_EN.setIcon(QIcon(btnIcon))
        self.btnEN_DE = QPushButton("Englisch > Deutsch (F7)", clicked = self.toggleLanguageEN)
        self.btnEN_DE.setIcon(QIcon(btnIcon))
        self.btn_copy = QPushButton("Übersetzung kopieren (F8)", clicked = self.copySlot)
        self.btn_copy.setIcon(QIcon.fromTheme("edit-copy"))
        empty = QWidget()
        empty.setFixedWidth(100)
        self.hbox.addWidget(self.btnDE_EN)
        self.hbox.addWidget(self.btnEN_DE)
        self.hbox.addWidget(empty)
        self.hbox.addWidget(self.btn_copy)
        
        self.wid = QWidget()
        self.wid.setLayout(self.hbox)
        self.statusBar.addPermanentWidget(self.wid)
        self.statusBar.setStyleSheet("QStatusBar {font-size: 8pt;} QPushButton \
                                        {font-size: 9pt;} QPushButton::hover {background: #729fcf}")
        self.statusBar.showMessage("Ready", 0)
        self.setWindowIcon(QIcon(btnIcon))
        
    def toggleLanguageDE(self):
        self.trans.load("de")
        self.dest = "en"
        self.transTextTo()
            
    def toggleLanguageEN(self):
        self.trans.load("en")
        self.dest = "de"
        self.transTextTo()

    def connectSlots(self):
        # connect to slots
        self.openFile.triggered.connect(self.openFileSlot)
        self.exportFile.triggered.connect(self.exportFileSlot)
        self.exit.triggered.connect(self.close)

    def openFileSlot(self):
        filename, filetype = QFileDialog.getOpenFileName(self, 'Open File', '.')
        if filename:
            print(filename)
            with open(filename, encoding = 'utf-8') as f:
                try:
                    self.originText.setPlainText(str(f.read()))
                except Exception as e:
                    self.originText.setPlainText(e.args[1])

    def exportFileSlot(self):
        if not self.transText.toPlainText():
            return
        filename, filetype = QFileDialog.getSaveFileName(self, 'Save File', '.', '*.txt;;*')
        if filename:
            with open(filename, 'w', encoding = 'utf-8') as f:
                try:
                    f.write(self.transText.toPlainText())
                except Exception as e:
                    self.transText.setPlainText(e.args[1])

    def changeLanguage(self, lan):
        """:author : Tich
        :param lan: 0=>Deutsch, 1=>English
        change ui language
        """
        if lan == 0 and self.lan != 0:
            self.lan = 0
            print("[MainWindow] Change to Deutsch")
            self.trans.load("de")
        elif lan == 1 and self.lan != 1:
            self.lan =1
            print("[MainWindow] Change to Englisch")
            self.trans.load("en")
        else:
            return
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.retranslateUi(self)

    def destinationLanguage(self, lan):
        """:author : Tich
        :param lan: 0: Deutsch, 1: English
        change destination language
        """
        if lan == 0:
            self.dest = 'en'
        else:
            self.dest = 'de'
        print(self.dest)
 
    def transTextTo(self):
        text = self.originText.toPlainText()
        if text:
            self.originText.setPlainText(text)
            try:
                self.t=GTranslator(self.dest, text)
                self.t.start()
                self.transText.setPlainText("")
                self.transText.setPlaceholderText("...")
                self.t.trigger.connect(self.translated)
            except Exception as e:
                print(e.args[1])
                self.transText.setPlainText("error!")

    def translated(self):
        global GTransData
        if GTransData:
            self.transText.setPlainText(GTransData)
        else:
            self.transText.setPlainText("error!")
        GTransData = ""

    def alwaysFrontFunc(self):
        """change window status
        """
        if self.alwaysFront.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # always top
            self.show()
        else:
            self.setWindowFlags(Qt.Widget)
            self.show()

    def copySlot(self):
        s = self.transText.toPlainText()
        if s:
            self.isCopyFromTrans = True
            clipboard = QApplication.clipboard()
            clipboard.setText(s)

    def onClipboradChanged(self):
        if self.isCopyFromTrans:
            self.isCopyFromTrans = False
            return
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text and self.isRealTimeTrans:
            content = str(text)
            content = content.replace('', 'fi').replace('', 'ffi').replace('', 'ff').replace('', 'fl').replace('', 'th').replace('', 'ft').replace('', 'ft').replace('', 'tt')
            self.originText.setPlainText(content)
            self.transText.setPlainText(content)
            try:
                self.t=GTranslator(self.dest, content)
                self.t.start()
                self.transText.setPlainText("")
                self.transText.setPlaceholderText("...")
                self.t.trigger.connect(self.translated)
            except:
                self.transText.setPlainText("error!")


class GTranslator(QThread): 
    trigger = pyqtSignal()
    def __init__(self, dest, content):
        super().__init__()
        self.content = content
        self.dest = dest
  
    def run(self): 
        Data = []
        global GTransData
        T = Translator(service_urls=['translate.google.com'])
        try:
            ts = T.translate(self.content, dest=self.dest)
            if isinstance(ts.text, list):
                for i in ts:
                    Data.append(i.text)
                GTransData = Data
            else:
                GTransData = ts.text
        except:
            GTransData = 'An error happended. Please retry...'
        self.trigger.emit()         # emit signal once translati is finfished

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    clipboard = QApplication.clipboard()
    clipboard.dataChanged.connect(w.onClipboradChanged)
    sys.exit(app.exec_())
