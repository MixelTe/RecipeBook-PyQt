import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QLabel, QMainWindow, QMessageBox, QSizePolicy, QVBoxLayout
from functions import List, QGroupBoxClickable, SaveParamsForCall, clearLayout, clearText, fetch, getImagesById, join
from recipe import RecipeWindow
from recipeEditor import RecipeEditorWindow
from settings import IMAGES_PATH
from ui.Ui_MainWindow import Ui_MainWindow
# pyuic5 ui/Ui_MainWindow.ui -o ui/Ui_MainWindow.py


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.windows = []
        self.include = List()
        self.exclude = List()
        if (self.setIngredients()):
            return
        self.inp_title.textChanged.connect(self.find)
        self.btn_addRecipe.clicked.connect(self.addNewRecipe)
        self.btn_update.clicked.connect(self.update)
        self.list_results.setSpacing(16)
        self.find()

    def setIngredients(self):
        clearLayout(self.list_ingr)
        clearLayout(self.list_ingr_exc)
        ingredients, r = fetch(
            "select id, title from Ingredients order by title")
        if (not r):
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            self.deleteLater()
            return True
        self.setIngredients_one(self.list_ingr, ingredients, self.include)
        self.setIngredients_one(self.list_ingr_exc, ingredients, self.exclude)

    def setIngredients_one(self, el: QVBoxLayout, ingredients: list[tuple[int, str]], lst: List):
        for id, title in ingredients:
            cbox = QCheckBox()
            cbox.setText(title)
            el.addWidget(cbox)
            if (id in lst):
                cbox.setChecked(True)

            @SaveParamsForCall(id, cbox)
            def changeFilter(id: int, cbox: QCheckBox):
                lst.toggle(id, cbox.isChecked())
                self.find()
            cbox.clicked.connect(changeFilter)

    def find(self):
        request = "SELECT id, title FROM Recipes\n"
        text = clearText(self.inp_title.text()).lower()
        if (len(text) > 0):
            request += "WHERE lower(title) LIKE ?\n"
        if (len(self.include) > 0):
            if (len(text) > 0):
                request += "AND "
            else:
                request += "WHERE "
            for i, id in enumerate(self.include):
                if (i != 0):
                    request += "and "
                request += "id in (\n"
                request += f"    SELECT recipeId FROM RecipesIngredients WHERE ingredientId = {id}\n"
                request += "    )\n"
        if (len(self.exclude) > 0):
            if (len(self.include) > 0):
                request += "AND "
            else:
                request += "WHERE "
            request += "id not in (\n"
            request += "    SELECT recipeId FROM RecipesIngredients WHERE ingredientId in\n"
            request += "        (" + join(", ", self.exclude) + ")\n"
            request += "    )\n"
        request += "order by title"
        # print(request)
        # print()
        recipes, r = fetch(
            request, (f"%{text}%",) if (len(text) > 0) else None)
        if (not r):
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            self.deleteLater()
            return
        self.showRecipes(recipes)

    def showRecipes(self, recipes: list[tuple[int, str]]):
        clearLayout(self.list_results)
        for id, title in recipes:
            item = QGroupBoxClickable()
            item.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)
            item.setTitle(title)
            self.list_results.addWidget(item)
            if (self.createRecipeIngredList(id, item)):
                return True
            item.setStyleSheet("font-size: 20px;")
            item.setObjectName("RecipeBox")
            item.setOnPress(self.openRecipe(id))
        self.list_results.addStretch()

    def createRecipeIngredList(self, recipeId, parent: QGroupBoxClickable):
        layout = QGridLayout(parent)
        grid = QGridLayout()
        layout.addLayout(grid, 0, 1)
        ingredients, r = fetch(f"""
            SELECT i.title
            FROM RecipesIngredients as ri
            INNER JOIN Ingredients as i on i.id = ri.ingredientId
            WHERE ri.recipeId = {recipeId}
            ORDER BY title
        """)
        if (not r):
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            self.deleteLater()
            return True
        images = getImagesById(recipeId)
        img = images[0] if len(images) > 0 else None
        i = 0
        ingredInRow = 6 if img is None else 4
        for i, inred in enumerate(ingredients):
            inred = inred[0]
            lbl = QLabel()
            lbl.setStyleSheet("font-size: 10pt")
            lbl.setText(inred)
            grid.addWidget(lbl, i // ingredInRow, i % ingredInRow)
        height = (i // ingredInRow + 1) * 40 + 20
        if img is not None:
            height = max(height, 120)
            imgEl = QLabel()
            pixmap = QPixmap(IMAGES_PATH + "/" + img).scaled(150,
                                                             height - 40, Qt.AspectRatioMode.KeepAspectRatio)
            imgEl.setPixmap(pixmap)
            imgEl.setFixedWidth(pixmap.width())
            grid.setContentsMargins(10, 0, 0, 0)
            layout.addWidget(imgEl, 0, 0)
        parent.setFixedHeight(height)

    def openRecipe(self, id: int):
        def openRecipe():
            def onClose():
                self.windows.remove(w)
                self.find()
            w = RecipeWindow(id, self.find, onClose)
            self.windows.append(w)
            w.show()
        return openRecipe

    def addNewRecipe(self):
        w = RecipeEditorWindow(self, None)
        w.exec()
        self.find()

    def update(self):
        self.setIngredients()
        self.find()


if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
