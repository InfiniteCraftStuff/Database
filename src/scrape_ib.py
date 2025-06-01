import requests
import time
import logging

from infinibrowser import types, Infinibrowser

from storage.database_manager import ElementsDatabaseManager, RecipesDatabaseManager


logger = logging.getLogger(__name__)


def fetch_recipes(element_db: str) -> list[types.Recipe]:
    MAX_RETRIES = 3
    RETRY_DELAYS = (0.1, 0.15)

    for retries in range(MAX_RETRIES + 1):
        try:
            data = Infinibrowser.get_recipes(element_db)
            return data.recipes

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if retries < MAX_RETRIES:
                    delay = RETRY_DELAYS[min(retries, len(RETRY_DELAYS) - 1)]
                    logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"[{e.response.status_code}] {e.response.reason}. "
                        f"Error fetching recipes for element {element_db} after multiple retries"
                    )
                    return []
            elif e.response.status_code == 404:
                logger.error(
                    f"[{e.response.status_code}] {e.response.reason}. Element {element_db} not found"
                )
                return []
            else:
                logger.error(
                    f"[{e.response.status_code}] {e.response.reason}. "
                    f"Error fetching recipes for element {element_db}"
                )
                return []

        except requests.exceptions.RequestException as e:
            if retries < MAX_RETRIES:
                delay = RETRY_DELAYS[min(retries, len(RETRY_DELAYS) - 1)]
                logger.warning(f"Request failed ({e}). Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                logger.error(
                    f"Error fetching recipes for element {element_db} after multiple retries: {e}"
                )
                return []

    return []


def fetch_uses(element_db: str) -> list[types.Use]:
    MAX_RETRIES = 3
    RETRY_DELAYS = (0.1, 0.15)

    for retries in range(MAX_RETRIES + 1):
        try:
            data = Infinibrowser.get_uses(element_db)
            return data.uses

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if retries < MAX_RETRIES:
                    delay = RETRY_DELAYS[min(retries, len(RETRY_DELAYS) - 1)]
                    logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"[{e.response.status_code}] {e.response.reason}. "
                        f"Error fetching uses for element {element_db} after multiple retries"
                    )
                    return []
            elif e.response.status_code == 404:
                logger.error(
                    f"[{e.response.status_code}] {e.response.reason}. Element {element_db} not found"
                )
                return []
            else:
                logger.error(
                    f"[{e.response.status_code}] {e.response.reason}. "
                    f"Error fetching uses for element {element_db}"
                )
                return []

        except requests.exceptions.RequestException as e:
            if retries < MAX_RETRIES:
                delay = RETRY_DELAYS[min(retries, len(RETRY_DELAYS) - 1)]
                logger.warning(f"Request failed ({e}). Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                logger.error(
                    f"Error fetching uses for element {element_db} after multiple retries: {e}"
                )
                return []

    return []


def scrape(db_path: str, offset: int, limit: int):
    elements_db_manager = ElementsDatabaseManager(db_path)
    recipes_db_manager = RecipesDatabaseManager(db_path)

    all_elements = elements_db_manager.get_all_elements(offset=offset, limit=limit)

    for i, element_db in enumerate(all_elements, offset):
        element_db_name = element_db[0]
        try:
            uses = fetch_uses(element_db_name)
            if not uses:
                continue

            recipes_to_add: list[tuple[str, str, str]] = []
            missing_elements: list[tuple[str, str]] = []

            for use in uses:
                try:
                    used_with_element = use.pair
                    used_with_element_db = elements_db_manager.get_element(used_with_element.id)

                    if not used_with_element_db:
                        missing_elements.append((used_with_element.id, used_with_element.emoji))

                    recipes_to_add.append((element_db_name, used_with_element.id, use.result.id))

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
                logger.error(f"Error adding uses to database: {e}")

        except KeyboardInterrupt:
            logger.warning(f"Interrupted at {i:_}, element_db_name={element_db_name}")
            return
