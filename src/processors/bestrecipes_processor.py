import json
from storage.database_manager import RecipesDatabaseManager


def process(file_path: str, db_path: str, batch_size: int = 250_000):
    recipes_db_manager = RecipesDatabaseManager(db_path)

    batch: list[tuple[str, str, str]] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            recipe: tuple[str, str, str] = tuple(json.loads(line))

            # Collect batch for DB insertion
            batch.append(recipe)

            if len(batch) >= batch_size:
                print("\nAdding batch")
                recipes_db_manager.bulk_add_recipes(batch)
                print("Batch added")
                batch.clear()

    # Insert any remaining recipes
    if batch:
        recipes_db_manager.bulk_add_recipes(batch)
