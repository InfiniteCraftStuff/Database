import { RecipesDatabaseManager } from "~/db_manager";

export async function process_bestrecipes(
  file_path: string,
  db_path: string,
  batch_size: number = 250_000,
) {
  const recipes_db_manager = new RecipesDatabaseManager(db_path);
  const batch: [string, string, string][] = [];
  const file = Bun.file(file_path);
  const lines = (await file.text()).split("\n");
  for (const line of lines) {
    const recipe: [string, string, string] = JSON.parse(line);

    // Collect batch for DB insertion
    batch.push(recipe);
    if (batch.length >= batch_size) {
      console.log("\nAdding batch");
      recipes_db_manager.bulk_add_recipes(batch);
      console.log("Batch added");
      batch.length = 0;
    }
  }

  // Insert any remaining recipes
  if (batch.length) recipes_db_manager.bulk_add_recipes(batch);
}
