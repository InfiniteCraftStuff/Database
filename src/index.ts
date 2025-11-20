import * as path from "node:path";

import { process_emojis } from "~/processors";

const SRC_DIR = import.meta.dir;
const BASE_DIR = path.dirname(SRC_DIR);
const DB_PATH = path.join(BASE_DIR, "storage", "elements.db");

function main() {
  /*
   * Replace with CLI usage
   */
}

main();
