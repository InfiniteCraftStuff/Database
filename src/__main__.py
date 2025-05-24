import os
import requests
from typing import TypedDict

from storage.database_manager import ElementsDatabaseManager, RecipesDatabaseManager

from temp.recipes import Recipe


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")


class ApiResponse(TypedDict):
    recipes: list[Recipe]


def fetch_recipes(element_db) -> ApiResponse:
    url = f"https://infinibrowser.wiki/api/recipes?id={element_db}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching recipes for element ID {element_db}: {response.status_code}")
        return {"recipes": []}


e_db = ElementsDatabaseManager(DB_PATH)
r_db = RecipesDatabaseManager(DB_PATH)

all_elements = e_db.get_all_elements(offset=100, limit=200)

for element in all_elements:
    element_db = element[0]
    recipes_data = fetch_recipes(element_db)
    recipes = recipes_data.get("recipes", [])

    recipes_to_add: list[tuple[str, str, str]] = []
    for recipe_pair in recipes:
        try:
            first_element = recipe_pair[0]
            second_element = recipe_pair[1]

            first_element_db = e_db.get_element(first_element["id"])
            second_element_db = e_db.get_element(second_element["id"])
            result_element = element[1]  # element[1] is the name of the element

            if not first_element_db:
                e_db.add_element(first_element["id"], first_element["emoji"])
                first_element_db = e_db.get_element(first_element["id"])
                print(f"Added missing element: {first_element["id"]}")
            if not second_element_db:
                e_db.add_element(second_element["id"], second_element["emoji"])
                second_element_db = e_db.get_element(second_element["id"])
                print(f"Added missing element: {second_element["id"]}")

            if first_element_db and second_element_db:
                recipes_to_add.append((first_element_db[0], second_element_db[0], result_element))
            else:
                print(f"Skipping recipe due to missing element: {recipe_pair}")
        except Exception as e:
            print(f"Error processing recipe: {recipe_pair}. Error: {e}")

    r_db.bulk_add_recipes(recipes_to_add)
