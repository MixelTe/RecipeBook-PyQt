# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/Ui_IngredientsWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IngredientsWindow(object):
    def setupUi(self, IngredientsWindow):
        IngredientsWindow.setObjectName("IngredientsWindow")
        IngredientsWindow.resize(370, 350)
        IngredientsWindow.setMinimumSize(QtCore.QSize(370, 350))
        font = QtGui.QFont()
        font.setPointSize(10)
        IngredientsWindow.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(IngredientsWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table = QtWidgets.QTableWidget(IngredientsWindow)
        self.table.setObjectName("table")
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.table)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_add = QtWidgets.QPushButton(IngredientsWindow)
        self.btn_add.setObjectName("btn_add")
        self.horizontalLayout.addWidget(self.btn_add)
        self.buttonBox = QtWidgets.QDialogButtonBox(IngredientsWindow)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(IngredientsWindow)
        self.buttonBox.accepted.connect(IngredientsWindow.accept)
        self.buttonBox.rejected.connect(IngredientsWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(IngredientsWindow)

    def retranslateUi(self, IngredientsWindow):
        _translate = QtCore.QCoreApplication.translate
        IngredientsWindow.setWindowTitle(_translate("IngredientsWindow", "????????????????/?????????????? ????????????????????"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("IngredientsWindow", "????????????????????"))
        self.btn_add.setText(_translate("IngredientsWindow", "???????????????? ????????????????????"))
