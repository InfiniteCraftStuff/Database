import * as z from "zod";

import { ElementsDatabaseManager } from "~/db_manager";

const EmojiFileSchema = z.record(z.string(), z.string());

export async function process_emojis(file_path: string, db_path: string) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);
  const file = Bun.file(file_path);
  const data = EmojiFileSchema.parse(await file.json());
  const elements = Object.entries(data);
  elements_db_manager.bulk_add_elements(elements);
}
