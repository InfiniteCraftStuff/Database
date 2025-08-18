import logging

from infinibrowser import types, Infinibrowser

from storage.database_manager import ElementsDatabaseManager, RecipesDatabaseManager

from error_handler import with_retries


logger = logging.getLogger(__name__)


@with_retries(func_name="recipes")
def fetch_recipes(element_db: str) -> list[types.Recipe]:
    data = Infinibrowser.get_recipes(element_db)
    return data.recipes


@with_retries(func_name="uses")
def fetch_uses(element_db: str) -> list[types.Use]:
    data = Infinibrowser.get_uses(element_db)
    return data.uses


def scrape(db_path: str, offset: int, limit: int):
    elements_db_manager = ElementsDatabaseManager(db_path)
    recipes_db_manager = RecipesDatabaseManager(db_path)

    all_elements = elements_db_manager.get_all_elements(offset=offset, limit=limit)

    for i, element_db in enumerate(all_elements, offset):
        try:
            uses = fetch_uses(element_db.name)
            if not uses:
                logger.info(f"Skipping {element_db.name} (no uses)")
                continue

            recipes_to_add: list[tuple[str, str, str]] = []
            missing_elements: list[tuple[str, str]] = []

            for use in uses:
                try:
                    used_with_element = use.pair
                    used_with_element_db = elements_db_manager.get_element(used_with_element.id)

                    if not used_with_element_db:
                        missing_elements.append((used_with_element.id, used_with_element.emoji))

                    result_element = use.pair
                    result_element_db = elements_db_manager.get_element(result_element.id)

                    if not result_element_db:
                        missing_elements.append((result_element.id, result_element.emoji))

                    recipes_to_add.append((element_db.name, used_with_element.id, use.result.id))

                except Exception as e:
                    logger.error(f"Error processing recipe: {use}. Error: {e}")

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
                logger.info(f"Successfully added uses for {element_db.name}")
            except Exception as e:
                logger.error(f"Error adding uses for {element_db.name} to database: {e}")

        except KeyboardInterrupt:
            logger.warning(f"Interrupted at {i:_} for {element_db.name}")
            return
