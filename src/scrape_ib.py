import requests

from typing import TypedDict

import logging

from storage.database_manager import ElementsDatabaseManager, RecipesDatabaseManager

from temp.recipes import Recipe


logger = logging.getLogger(__name__)


class ApiResponseDate(TypedDict):
    recipes: list[Recipe]


def fetch_recipes(element_db: str) -> ApiResponseDate:
    url = f"https://infinibrowser.wiki/api/recipes?id={element_db}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            f"Error fetching recipes for element {element_db}: [{response.status_code}] {response.reason}"
        )
        return {"recipes": []}


def scrape(db_path: str):
    elements_db_manager = ElementsDatabaseManager(db_path)
    recipes_db_manager = RecipesDatabaseManager(db_path)

    all_elements = elements_db_manager.get_all_elements(offset=12_500, limit=500)

    for element in all_elements:
        element_db = element[0]
        recipes_data = fetch_recipes(element_db)
        recipes = recipes_data.get("recipes", [])
        if not recipes:
            continue

        recipes_to_add: list[tuple[str, str, str]] = []
        missing_elements: list[tuple[str, str]] = []

        for recipe_pair in recipes:
            try:
                first_element = recipe_pair[0]
                first_element_db = elements_db_manager.get_element(first_element["id"])

                if not first_element_db:
                    missing_elements.append((first_element["id"], first_element["emoji"]))

                second_element = recipe_pair[1]
                second_element_db = elements_db_manager.get_element(second_element["id"])

                if not second_element_db:
                    missing_elements.append((second_element["id"], second_element["emoji"]))

                result_element_name = element[1]  # element[1] is the name of the element

                recipes_to_add.append((first_element["id"], second_element["id"], result_element_name))

            except Exception as e:
                logger.error(f"Error processing recipe: {recipe_pair}. Error: {e}")

        # remove duplicates
        missing_elements = list(set(missing_elements))

        if missing_elements:
            try:
                elements_db_manager.bulk_add_elements(missing_elements)
                logger.info("Successfully added missing elements")
            except Exception as e:
                logger.error(f"Error adding missing elements: {e}")

        try:
            recipes_db_manager.bulk_add_recipes(recipes_to_add)
            logger.info("Successfully added recipes")
        except Exception as e:
            logger.error(f"Error adding recipes to database: {e}")
