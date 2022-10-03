import sqlite3
from settings import DB_PATH


TABLE_Recipes = """
CREATE TABLE IF NOT EXISTS Recipes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT
                         NOT NULL
                         UNIQUE,
    title        TEXT    NOT NULL,
    description  TEXT
);
"""
TABLE_Ingredients = """
CREATE TABLE IF NOT EXISTS Ingredients (
    id    INTEGER PRIMARY KEY AUTOINCREMENT
                  NOT NULL
                  UNIQUE,
    title TEXT    NOT NULL
                  UNIQUE,
    importance    INTEGER
                  NOT NULL
);
"""
TABLE_RecipesIngredients = """
CREATE TABLE IF NOT EXISTS RecipesIngredients (
    recipeId     INTEGER REFERENCES Recipes (id) ON DELETE CASCADE
                         NOT NULL,
    ingredientId INTEGER REFERENCES Ingredients (id)
                         NOT NULL,
    count        TEXT    NOT NULL
);
"""

def create_db():
    con = None
    try:
        con = sqlite3.connect(DB_PATH)
        c = con.cursor()
        c.execute(TABLE_Recipes)
        c.execute(TABLE_Ingredients)
        c.execute(TABLE_RecipesIngredients)
    except Exception as e:
        print(e)
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    create_db()
