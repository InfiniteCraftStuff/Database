import { ElementsDatabaseManager } from "~/storage/database_manager";

export async function process(file_path: string, db_path: string) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);

  const file = Bun.file(file_path);
  const data: unknown = await file.json();
  const elements = Object.entries(data);
  elements_db_manager.bulk_add_elements(elements);
}
