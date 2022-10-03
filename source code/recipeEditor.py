import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QFileDialog, QHeaderView, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem
from functions import QLabelClickable, clearText, commit, commitAndGetId, displayImg, fetch, getImagesById, getImgId, join
from ingredients import IngredientsWindow
from settings import IMAGES_PATH
from ui.Ui_RecipeEditorWindow import Ui_RecipeEditorWindow
from threading import Timer
from shutil import copyfile
# pyuic5 ui/Ui_RecipeEditorWindow.ui -o ui/Ui_RecipeEditorWindow.py


class RecipeEditorWindow(Ui_RecipeEditorWindow, QDialog):
    def __init__(self, parent, recipeId):
        super().__init__(parent)
        self.setupUi(self)
        self.recipeId = recipeId
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        try:
            self.setTitle()
            self.setIngredients()
            self.setIngredientInp()
            self.setImages()
            self.setDescription()
            self.btn_editIngredients.clicked.connect(self.openIngredientEditor)
            self.btn_ingredient.clicked.connect(self.addIngredient)
            self.btn_addImage.clicked.connect(self.addImage)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            Timer(0.1, lambda: self.reject()).start()

    def setTitle(self):
        if (self.recipeId == None): return
        title, r = fetch(f"select title from Recipes where id = {self.recipeId}")
        if (not r or len(title) == 0): raise Exception()
        self.inp_title.setText(title[0][0])

    def setIngredients(self):
        self.ingredients = {} # count, changed, new
        self.ingredients_deleted = []
        header = self.table_inredients.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_inredients.setColumnHidden(0, True)
        self.table_inredients.cellChanged.connect(self.onIngredientChange)
        if (self.recipeId == None): return
        ingredients, r = fetch(f"""
        select i.id, i.title, ri.count
        from RecipesIngredients as ri
        join Ingredients as i on i.id = ri.ingredientId
        where ri.recipeId = {self.recipeId}
        order by i.title
        """)
        if (not r): raise Exception()
        for id, title, count in ingredients:
            self.addIngredientToTable(id, title, count, False)

    def addIngredientToTable(self, id, title, count, new):
        self.disableChangeEvent = True
        self.ingredients[id] = (count, False, new)
        if (id in self.ingredients_deleted):
            self.ingredients_deleted.remove(id)
        i = self.table_inredients.rowCount()
        self.table_inredients.setRowCount(i + 1)
        btn = QPushButton()
        btn.setText("Удалить")
        idEl = QTableWidgetItem(str(id))
        idEl.setFlags(Qt.ItemFlag.ItemIsEnabled)
        titleEl = QTableWidgetItem(title)
        titleEl.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table_inredients.setItem(i, 0, idEl)
        self.table_inredients.setItem(i, 1, titleEl)
        self.table_inredients.setItem(i, 2, QTableWidgetItem(count))
        self.table_inredients.setCellWidget(i, 3, btn)
        def delete():
            row = idEl.row()
            self.table_inredients.removeRow(row)
            self.ingredients_deleted.append(id)
            if (id in self.ingredients):
                del self.ingredients[id]
            self.inp_ingredient.addItem(title, id)
            resizeTable(self.table_inredients)
        btn.clicked.connect(delete)
        self.disableChangeEvent = False
        resizeTable(self.table_inredients)

    def onIngredientChange(self):
        if (self.disableChangeEvent): return
        row = self.table_inredients.currentRow()
        id = int(self.table_inredients.item(row, 0).text())
        count = clearText(self.table_inredients.item(row, 2).text())
        if (count == ""):
            count = self.ingredients[id][0]
        else:
            self.ingredients[id] = (count, True, self.ingredients[id][2])
        self.ingredients[id] = (count, True, self.ingredients[id][2])
        self.disableChangeEvent = True
        self.table_inredients.item(row, 2).setText(self.ingredients[id][0])
        self.disableChangeEvent = False

    def setIngredientInp(self):
        ingredients, r = fetch("select id, title from Ingredients order by title")
        if (not r): raise Exception()
        self.inp_ingredient.clear()
        curIngredients = list(self.ingredients.keys())
        for id, title in ingredients:
            if (id not in curIngredients):
                self.inp_ingredient.addItem(title, id)
        self.inp_ingredient.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

    def addIngredient(self):
        title = self.inp_ingredient.currentText()
        i = self.inp_ingredient.currentIndex()
        id = self.inp_ingredient.itemData(i)
        if (id is None): return
        self.addIngredientToTable(id, title, "", True)
        self.inp_ingredient.removeItem(i)

    def openIngredientEditor(self):
        forbidden = [int(self.table_inredients.item(i, 0).text()) for i in range(self.table_inredients.rowCount())]
        editor = IngredientsWindow(self, forbidden)
        editor.exec()
        self.setIngredientInp()

    def setImages(self):
        self.images_deleted = []
        self.images_added = []
        self.images_maxI = 0
        self.imageHeight = 100
        headerH = self.table_images.horizontalHeader()
        headerH.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        headerH.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        headerV = self.table_images.verticalHeader()
        headerV.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_images.setColumnHidden(0, True)
        images = getImagesById(self.recipeId)
        for img in images:
            id = getImgId(img)[1]
            if (self.images_maxI < id):
                self.images_maxI = id
            self.addImageToTable(IMAGES_PATH + "/" + img)

    def addImageToTable(self, imgPath):
        i = self.table_images.rowCount()
        self.table_images.setRowCount(i + 1)

        pathId = QTableWidgetItem(imgPath)
        pathId.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table_images.setItem(i, 0, pathId)

        lbl = QLabelClickable()
        pixmap = QPixmap(imgPath)
        lbl.setOnPress(displayImg(imgPath))
        w = self.table_images.width() - self.table_images.columnWidth(2)
        lbl.setPixmap(pixmap.scaled(w, self.imageHeight, Qt.AspectRatioMode.KeepAspectRatio))
        self.table_images.setCellWidget(i, 1, lbl)
        self.table_images.setRowHeight(i, self.imageHeight)

        btn = QPushButton()
        btn.setText("Удалить")
        self.table_images.setCellWidget(i, 2, btn)
        def delete():
            row = pathId.row()
            self.table_images.removeRow(row)
            self.images_deleted.append(imgPath)
            resizeTable(self.table_images)
        btn.clicked.connect(delete)

        resizeTable(self.table_images)

    def addImage(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', 'Картинка (*.png, *.jpg)')[0]
        if (fname == ""):
            return
        self.images_maxI += 1
        imgType = "png" if fname.endswith(".png") else "jpg"
        imgPath = IMAGES_PATH + f"/{self.recipeId}_{self.images_maxI}.{imgType}"
        copyfile(fname, imgPath)
        self.images_added.append(imgPath)
        self.addImageToTable(imgPath)

    def setDescription(self):
        def onResize():
            if (self.inp_description.hasFocus()):
                vbar = self.scrollArea.verticalScrollBar()
                vbar.setValue(vbar.maximum())
        self.inp_description.setOnResize(onResize)
        if (self.recipeId == None): return
        description, r = fetch(f"select description from Recipes where id = {self.recipeId}")
        if (not r or len(description) == 0): raise Exception()
        self.inp_description.setText(description[0][0])

    def accept(self):
        if (self.commit_title()):
            return
        self.commit_ingredients()
        self.commit_images()
        self.commit_description()
        return super().accept()

    def commit_title(self):
        title = clearText(self.inp_title.text())
        if (title == ""):
            QMessageBox.information(self, "Книга рецептов", "Введите название рецепта")
            return True
        if (self.recipeId == None):
            id, r = commitAndGetId(f"insert into Recipes(title, description) values(?, '')", (title,))
            if (not r):
                QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
                return True
            self.recipeId = id[0][0]
            return
        r = commit(f"update Recipes set title = ? where id = {self.recipeId}", (title,))
        if (not r):
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")

    def commit_description(self):
        description = self.inp_description.toPlainText()
        r = commit(f"update Recipes set description = ? where id = {self.recipeId}", (description,))
        if (not r):
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")

    def commit_images(self):
        for img in self.images_deleted:
            os.remove(img)

    def commit_ingredients(self):
        toUpdate = []
        toAdd = []
        toDelete = self.ingredients_deleted
        for key in self.ingredients.keys():
            el = self.ingredients[key]
            if (el[2]):
                toAdd.append((el[0], key))
            elif (el[1]):
                toUpdate.append((el[0], key))

        if (len(toAdd) > 0):
            request = "insert into RecipesIngredients(recipeId, ingredientId, count) values\n"
            request += ", ".join(f"({self.recipeId}, {el[1]}, ?)" for el in toAdd)
            counts = tuple(map(lambda el: el[0], toAdd))
            r = commit(request, counts)
            if (not r):
                QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
        if (len(toUpdate) > 0):
            for update in toUpdate:
                request = f"update RecipesIngredients set count = ? where recipeId = {self.recipeId} and ingredientId = ?"
                r = commit(request, update)
                if (not r):
                    QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
        if (len(toDelete) > 0):
            request = f"delete from RecipesIngredients where recipeId = {self.recipeId} and ingredientId in\n"
            request += "(" + join(", ", toDelete) + ")"
            r = commit(request)
            if (not r):
                QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")

    def reject(self):
        for img in self.images_added:
            os.remove(img)
        return super().reject()

def resizeTable(table: QTableWidget):
    h = table.rowHeight(0) * table.rowCount() + table.horizontalHeader().height() + 2
    table.setMinimumHeight(h)
    table.setFixedHeight(h)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecipeEditorWindow(None, 1)
    # ex = RecipeEditorWindow(None, None)
    ex.show()
    sys.exit(app.exec_())
