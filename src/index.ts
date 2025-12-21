import * as path from "node:path";

import {
  process_csv_recipes,
  process_jsonl_recipes,
  process_emojis,
  process_savefile,
} from "~/processors";

const SRC_DIR = import.meta.dir;
const BASE_DIR = path.dirname(SRC_DIR);
const DB_PATH = path.join(BASE_DIR, "storage", "elements.db");

async function main() {
  const command = process.argv[2];
  const file_path = process.argv[3];

  if (!command) {
    console.log("Available commands: jsonl, csv, emojis, savefile");
    throw new Error("No command provided");
  }

  if (!file_path) throw new Error("No file path provided");

  switch (command) {
    case "jsonl": {
      return process_jsonl_recipes(file_path, DB_PATH);
    }
    case "csv": {
      return process_csv_recipes(file_path, DB_PATH);
    }
    case "emojis": {
      return process_emojis(file_path, DB_PATH);
    }
    case "savefile": {
      return process_savefile(file_path, DB_PATH);
    }
    default: {
      throw new Error("Invalid command");
    }
  }
}

await main()
  .catch((err: unknown) => {
    if (!(err instanceof Error)) throw err;
    console.error(err.message);
  })
  .finally(() => process.exit(0));
