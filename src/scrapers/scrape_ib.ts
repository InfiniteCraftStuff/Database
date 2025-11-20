import { ib } from "infinibrowser";

import { ElementsDatabaseManager, RecipesDatabaseManager } from "~/db_manager";

import { with_retries } from "./error_handler";

const fetch_recipes = with_retries()(async function fetch_recipes(
  element_db: string
) {
  const data = await ib.getRecipes(element_db);
  return data.recipes;
});

const fetch_uses = with_retries()(async function fetch_uses(
  element_db: string
) {
  const data = await ib.getUses(element_db);
  return data.uses;
});

export async function scrape_ib(
  db_path: string,
  offset: number,
  limit: number
) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);
  const recipes_db_manager = new RecipesDatabaseManager(db_path);

  const all_elements = elements_db_manager.get_all_elements({ offset, limit });

  let i = offset;
  for (const element_db of all_elements) {
    i++;
    const uses = await fetch_uses(element_db.name);
    if (!uses) {
      console.info("Skipping {element_db.name} (no uses)");
      continue;
    }
    const recipes_to_add: [string, string, string][] = [];
    let missing_elements: (readonly [string, string])[] = [];

    for (const use of uses) {
      try {
        const used_with_element = use.pair;
        const used_with_element_db = elements_db_manager.get_element(
          used_with_element.id
        );
        if (!used_with_element_db)
          missing_elements.push([
            used_with_element.id,
            used_with_element.emoji,
          ]);
        const result_element = use.pair;
        const result_element_db = elements_db_manager.get_element(
          result_element.id
        );
        if (!result_element_db)
          missing_elements.push([result_element.id, result_element.emoji]);
        recipes_to_add.push([
          element_db.name,
          used_with_element.id,
          use.result.id,
        ]);
      } catch (e) {
        console.error(`Error processing recipe: ${use}. Error: ${e}`);
      }
    }

    missing_elements = Array.from(new Set(missing_elements));

    if (missing_elements.length) {
      try {
        elements_db_manager.bulk_add_elements(missing_elements);
        console.info("Successfully added missing elements");
      } catch (e) {
        console.error(`Error adding missing elements: ${e}`);
      }
    }

    try {
      recipes_db_manager.bulk_add_recipes(recipes_to_add);
      console.info(`Successfully added uses for ${element_db.name}`);
    } catch (e) {
      console.error(
        `Error adding uses for ${element_db.name} to database: ${e}`
      );
    }
  }
}
