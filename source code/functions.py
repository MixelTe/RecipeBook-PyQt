import platform
import os
import subprocess
import re
import sqlite3
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGroupBox, QLabel, QLineEdit, QTextEdit
from settings import DB_PATH, IMAGES_PATH


def SaveParamsForCall(args, kwargs):
    def decorator(fun):
        def decoratorated():
            return fun(args, kwargs)
        return decoratorated
    return decorator


class List(list):
    def toggle(self, item, force=None):
        contains = self.__contains__(item)
        if (force is not None):
            if (force):
                if (not contains):
                    self.append(item)
            else:
                if (contains):
                    self.remove(item)
        else:
            if (contains):
                self.remove(item)
            else:
                self.append(item)


def join(s: str, lst: list):
    return s.join(str(el) for el in lst)


def fetch(request, param=None):
    con = None
    try:
        con = sqlite3.connect(DB_PATH)
        con.create_function("lower", 1, str.lower)
        con.create_function("upper", 1, str.upper)
        c = con.cursor()
        if (param is None):
            r = c.execute(request).fetchall()
        else:
            r = c.execute(request, param).fetchall()
        return (r, True)
    except Exception as e:
        print("fetch error:")
        print(e)
        print("fetch request:")
        print(request)
    finally:
        if con:
            con.close()
    return (None, False)


def commit(request, param=None):
    con = None
    try:
        con = sqlite3.connect(DB_PATH)
        con.create_function("lower", 1, str.lower)
        con.create_function("upper", 1, str.upper)
        c = con.cursor()
        c.execute("PRAGMA foreign_keys = 1")
        if (param is None):
            c.execute(request)
        else:
            c.execute(request, param)
        con.commit()
        return True
    except Exception as e:
        print("fetch error:")
        print(e)
        print("fetch request:")
        print(request)
    finally:
        if con:
            con.close()
    return False


def commitAndGetId(request, param=None):
    con = None
    try:
        con = sqlite3.connect(DB_PATH)
        con.create_function("lower", 1, str.lower)
        con.create_function("upper", 1, str.upper)
        c = con.cursor()
        c.execute("PRAGMA foreign_keys = 1")
        if (param is None):
            c.execute(request)
        else:
            c.execute(request, param)
        con.commit()
        r = c.execute("select last_insert_rowid()").fetchall()
        return (r, True)
    except Exception as e:
        print("fetch error:")
        print(e)
        print("fetch request:")
        print(request)
    finally:
        if con:
            con.close()
    return (None, False)


class QGroupBoxClickable(QGroupBox):
    def setOnPress(self, fun):
        self.onPress = fun

    def mousePressEvent(self, event):
        if (self.onPress):
            self.onPress()


class QLabelClickable(QLabel):
    def setOnPress(self, fun):
        self.onPress = fun

    def mousePressEvent(self, event):
        if (self.onPress):
            self.onPress()


class QTextEditFitText(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.onResize = None
        self.textChanged.connect(self.autoResize)

    def autoResize(self):
        self.document().setTextWidth(self.viewport().width())
        margins = self.contentsMargins()
        height = int(self.document().size().height() +
                     margins.top() + margins.bottom())
        self.setFixedHeight(height)
        if (self.onResize):
            self.onResize()

    def resize(self, width):
        self.document().setTextWidth(width)
        margins = self.contentsMargins()
        height = int(self.document().size().height() +
                     margins.top() + margins.bottom())
        self.setFixedHeight(height)
        if (self.onResize):
            self.onResize()

    def resizeEvent(self, event):
        self.autoResize()

    def setOnResize(self, f):
        self.onResize = f

    def setReadOnly(self, ro: bool):
        if (ro):
            self.setStyleSheet("border: none; background-color: transparent;")
        else:
            self.setStyleSheet("")
        return super().setReadOnly(ro)


class QLineEditP(QLineEdit):
    def setReadOnly(self, ro: bool):
        if (ro):
            self.setStyleSheet("border: none; background-color: transparent;")
        else:
            self.setStyleSheet("")
        return super().setReadOnly(ro)


# from random import randint
# def rand_color():
#     return f'rgb({randint(50, 255)}, {randint(50, 255)}, {randint(50, 255)})'


def clearText(text: str):
    return re.sub(r" +", " ", text.strip())


def openFile(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def clearLayout(layout):
    for i in range(layout.count() - 1, -1, -1):
        item = layout.itemAt(i)
        if (item.widget()):
            item.widget().close()
        else:
            layout.removeItem(item)


def displayImg(imgPath):
    def displayImg():
        openFile(imgPath)
    return displayImg


def resizeImg(lbl: QLabel, img: QPixmap, W, H):
    w, h = img.width(), img.height()
    mul = min(W / w, H / h)
    lbl.resize(int(w * mul), int(h * mul))


def getImgId(fname: str):
    name = fname[:fname.index(".")]
    id = int(name[:name.index("_")])
    subId = int(name[name.index("_") + 1:])
    return id, subId

def getImagesById(id: int):
    files = os.listdir(IMAGES_PATH)
    return list(filter(lambda el: getImgId(el)[0] == id, files))
