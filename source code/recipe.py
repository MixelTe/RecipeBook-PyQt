import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QHeaderView, QMainWindow, QMessageBox, QTableWidgetItem
from functions import QLabelClickable, clearLayout, commit, displayImg, fetch, getImagesById
from recipeEditor import RecipeEditorWindow, resizeTable
from settings import IMAGES_PATH
from ui.Ui_RecipeWindow import Ui_RecipeWindow
# pyuic5 ui/Ui_RecipeWindow.ui -o ui/Ui_RecipeWindow.py


class RecipeWindow(Ui_RecipeWindow, QMainWindow):
    def __init__(self, recipeId: int, onDelete=None, onClose=None):
        super().__init__()
        self.setupUi(self)
        self.placeY = 0
        self.recipeId = recipeId
        self.onDelete = onDelete
        self.onClose = onClose
        self.action_edit.triggered.connect(self.openEditor)
        self.action_delete.triggered.connect(self.delete)
        self.action_save.triggered.connect(self.save)
        self.init()

    def init(self):
        try:
            self.setTitle()
            self.setImages()
            self.setInredients()
            self.setDescription()
        except Exception as x:
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            self.deleteLater()

    def setTitle(self):
        title, r = fetch(f"select title from Recipes where id = {self.recipeId}")
        if (not r or len(title) == 0): raise Exception()
        titleStr = title[0][0]
        self.setWindowTitle(titleStr)
        self.lbl_title.setText(titleStr)

    def setImages(self):
        images = getImagesById(self.recipeId)
        clearLayout(self.images)
        h = 150
        lbls = []
        for img in images:
            lbl = QLabelClickable()
            self.images.addWidget(lbl)
            lbls.append((lbl, img))
        for lbl, img in lbls:
            imgPath = IMAGES_PATH + "/" + img
            pixmap = QPixmap(imgPath)
            lbl.setOnPress(displayImg(imgPath))
            lbl.setPixmap(pixmap.scaled(lbl.width(), h, Qt.AspectRatioMode.KeepAspectRatio))

    def setInredients(self):
        ingredients, r = fetch(f"""
        select i.title, ri.count
        from RecipesIngredients as ri
        join Ingredients as i on i.id = ri.ingredientId
        where ri.recipeId = {self.recipeId}
        order by i.title
        """)
        if (not r): raise Exception()
        self.table_ingr.clear()
        self.table_ingr.setShowGrid(False)
        self.table_ingr.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header = self.table_ingr.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_ingr.setRowCount(len(ingredients))
        for i, el in enumerate(ingredients):
            item, count = el
            ingredient = QTableWidgetItem(item)
            ingredient.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            countEl = QTableWidgetItem(count)
            countEl.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_ingr.setItem(i, 0, ingredient)
            self.table_ingr.setItem(i, 1, countEl)
        f = self.table_ingr.font()
        self.table_ingr.setStyleSheet("border: none; background-color: transparent;")
        self.table_ingr.setFont(f)
        resizeTable(self.table_ingr)

    def setDescription(self):
        description, r = fetch(f"select description from Recipes where id = {self.recipeId}")
        if (not r or len(description) == 0): raise Exception()
        w = self.body.width() - 40
        self.inp_desc.setText(description[0][0])
        f = self.inp_desc.font()
        self.inp_desc.setReadOnly(True)
        self.inp_desc.setFont(f)
        self.inp_desc.resize(w)

    def openEditor(self):
        editor = RecipeEditorWindow(self, self.recipeId)
        editor.exec()
        self.init()

    def delete(self):
        title = self.lbl_title.text()
        r = QMessageBox.question(self, "Удаление рецепта", f"Вы действительно хотите удалить рецепт {title}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if (r != QMessageBox.StandardButton.Yes):
            return
        commit(f"delete from Recipes where id = {self.recipeId}")
        self.deleteLater()
        if (self.onDelete):
            self.onDelete()

    def save(self):
        fileName = cleanFilename(self.lbl_title.text())
        filePath = QFileDialog.getSaveFileName(self, "Сохранение рецепта", f"./{fileName}.txt", "Текстовый файл (*.txt)")[0]
        if (filePath == ""):
            return
        try:
            with open(filePath, "w") as f:
                f.write(self.lbl_title.text() + "\n\n")
                for i in range(self.table_ingr.rowCount()):
                    ingr = self.table_ingr.item(i, 0).text()
                    count = self.table_ingr.item(i, 1).text()
                    f.write(ingr + "\t\t\t" + count + "\n")
                f.write("\n" + self.inp_desc.toPlainText())
        except Exception as x:
            QMessageBox.critical(self, "Сохранение рецепта", "Произошла ошибка")

    def closeEvent(self, e):
        if (self.onClose):
            self.onClose()
        return super().closeEvent(e)

def cleanFilename(filename):
    return ''.join([ch for ch in filename if ch not in "%:/,.\\[]<>*?"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecipeWindow(1)
    ex.show()
    sys.exit(app.exec_())