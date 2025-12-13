import * as path from "node:path";

import { process_csv_recipes } from "~/processors";

const SRC_DIR = import.meta.dir;
const BASE_DIR = path.dirname(SRC_DIR);
const DB_PATH = path.join(BASE_DIR, "storage", "elements.db");

function main() {
  /*
   * Replace with CLI usage
   */

  const FILE_PATH = "C:/Users/roman/Documents/dev/ic-stuff/recipes/words.csv";
  process_csv_recipes(FILE_PATH, DB_PATH);
}

main();
