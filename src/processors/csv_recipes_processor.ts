import { RecipesDatabaseManager } from "~/db_manager";

const extractRecipe = (line: string) => {
  const recipe = line.split("=");

  if (
    recipe.length !== 3 ||
    typeof recipe[0] !== "string" ||
    typeof recipe[1] !== "string" ||
    typeof recipe[2] !== "string"
  ) {
    throw new Error("Invalid recipe format");
  }

  return [recipe[0], recipe[1], recipe[2]] as const;
};

export async function process_csv_recipes(
  file_path: string,
  db_path: string,
  batch_size: number = 250_000,
) {
  const recipes_db_manager = new RecipesDatabaseManager(db_path);
  const batch: (readonly [string, string, string])[] = [];
  const file = Bun.file(file_path);
  const lines = (await file.text()).split("\n");
  for (const line of lines) {
    const recipe = extractRecipe(line);

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
