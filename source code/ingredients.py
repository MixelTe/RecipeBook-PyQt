import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView, QMessageBox, QPushButton, QTableWidgetItem
from functions import clearText, commit, fetch, join
from ui.Ui_IngredientsWindow import Ui_IngredientsWindow
from threading import Timer
# pyuic5 ui/Ui_IngredientsWindow.ui -o ui/Ui_IngredientsWindow.py


class IngredientsWindow(Ui_IngredientsWindow, QDialog):
    def __init__(self, parent, forbidden):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.forbidden = forbidden
        self.ingredients = {} # title, changed, new
        self.deleted = []
        self.maxId = 0
        self.disableChangeEvent = False
        try:
            self.setIngredients()
            self.btn_add.clicked.connect(self.addNewIngredient)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
            Timer(0.1, lambda: self.reject()).start()

    def setIngredients(self):
        ingredients, r = fetch(f"""select id, title from Ingredients order by title""")
        if (not r): raise Exception()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnHidden(0, True)
        for id, title in ingredients:
            self.addIngredientToTable(id, title, False)
        self.table.cellChanged.connect(self.onItemChange)

    def addIngredientToTable(self, id, title, new):
        self.disableChangeEvent = True
        self.ingredients[id] = (title, False, new)
        if (self.maxId < id): self.maxId = id
        i = self.table.rowCount()
        self.table.setRowCount(i + 1)
        idEl = QTableWidgetItem(str(id))
        idEl.setFlags(Qt.ItemFlag.ItemIsEnabled)
        titleEl = QTableWidgetItem(title)
        self.table.setItem(i, 0, idEl)
        self.table.setItem(i, 1, titleEl)

        res, r = fetch(f"""select recipeId from RecipesIngredients where ingredientId = {id} limit 1""")
        if (not r): raise Exception()
        if (id not in self.forbidden and len(res) == 0):
            btn = QPushButton()
            btn.setText("Удалить")
            self.table.setCellWidget(i, 2, btn)
            def delete():
                row = idEl.row()
                self.table.removeRow(row)
                self.deleted.append(id)
                if (id in self.ingredients):
                    del self.ingredients[id]
            btn.clicked.connect(delete)
        else:
            el = QTableWidgetItem("Используется")
            el.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(i, 2, el)
        self.disableChangeEvent = False

    def onItemChange(self):
        if (self.disableChangeEvent): return
        row = self.table.currentRow()
        id = int(self.table.item(row, 0).text())
        title = clearText(self.table.item(row, 1).text())
        allTitles = map(lambda key: self.ingredients[key][0], self.ingredients.keys())
        if (title in allTitles):
            QMessageBox.information(self, "Добавить/удалить ингредиент", f"Ингредиент {title} уже существует.")
        elif (title == ""):
            title = self.ingredients[id][0]
        else:
            self.ingredients[id] = (title, True, self.ingredients[id][2])
        self.disableChangeEvent = True
        self.table.item(row, 1).setText(self.ingredients[id][0])
        self.disableChangeEvent = False

    def addNewIngredient(self):
        title = "Название ингредиента"
        allTitles = map(lambda key: self.ingredients[key][0], self.ingredients.keys())
        if (title in allTitles):
            QMessageBox.information(self, "Добавить/удалить ингредиент", f"Измените название предыдущего ингредиента.")
            return
        self.addIngredientToTable(self.maxId + 1, title, True)
        self.table.scrollToBottom()

    def accept(self):
        title = "Название ингредиента"
        allTitles = map(lambda key: self.ingredients[key][0], self.ingredients.keys())
        if (title in allTitles):
            QMessageBox.information(self, "Добавить/удалить ингредиент", f"Вы не указали название ингредиента.")
            return
        self.updateData()
        return super().accept()

    def updateData(self):
        toAdd, toUpdate, toDelete = self.collectData()
        if (len(toAdd) > 0):
            request = "insert into Ingredients(title) values\n"
            request += ", ".join("(?)" for _ in range(len(toAdd)))
            r = commit(request, toAdd)
            if (not r):
                QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
        if (len(toUpdate) > 0):
            for update in toUpdate:
                request = "update Ingredients set title = ? where id = ?"
                r = commit(request, update)
                if (not r):
                    QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")
        if (len(toDelete) > 0):
            request = "delete from Ingredients where id in\n"
            request += "(" + join(", ", toDelete) + ")"
            r = commit(request)
            if (not r):
                QMessageBox.critical(self, "Книга рецептов", "Произошла ошибка")

    def collectData(self):
        toUpdate = []
        toAdd = []
        for key in self.ingredients.keys():
            el = self.ingredients[key]
            if (el[2]):
                toAdd.append((el[0]))
            elif (el[1]):
                toUpdate.append((el[0], key))
        return toAdd, toUpdate, self.deleted


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = IngredientsWindow(None, [])
    ex.show()
    sys.exit(app.exec_())
