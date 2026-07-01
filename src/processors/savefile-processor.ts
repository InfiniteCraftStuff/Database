import { Savefile } from "savefile.js";

import { ElementsDatabaseManager, RecipesDatabaseManager } from "#db-manager";

export async function process_savefile(file_path: string, db_path: string) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);
  const recipes_db_manager = new RecipesDatabaseManager(db_path);

  const file = Bun.file(file_path);

  const savefile = await Savefile.decode(await file.bytes());
  if (!savefile) {
    throw new Error("Invalid Savefile");
  }

  const elements = savefile.elements;

  const elements_count = elements.length;

  const number_of_batches = 2000;
  const batch_size = Math.floor(elements_count / number_of_batches);

  for (let i = 0; i < elements_count; i += batch_size) {
    console.log(
      `Processing batch ${Math.round(i / batch_size)}/${number_of_batches}`,
    );
    const element_batch = elements.slice(i, i + batch_size);

    try {
      elements_db_manager.bulk_add_elements(
        element_batch.map((element) => [element.text, element.emoji]),
      );

      recipes_db_manager.bulk_add_recipes(
        element_batch.flatMap((el) =>
          el.recipes.map((recipe) => [recipe.a.text, recipe.b.text, el.text]),
        ),
      );
    } catch {}
  }
}
