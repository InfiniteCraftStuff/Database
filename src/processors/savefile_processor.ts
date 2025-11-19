import { ElementsDatabaseManager } from "~/storage/database_manager";

type IC_Savefile_Element = {
  text: string;
  emoji: string;
};

async function load_json(file_path: string) {
  const file = Bun.file(file_path);
  const content = await file.text();
  const data: unknown = JSON.parse(content);
  return data;
}

export async function process(file_path: string, db_path: string) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);

  const data = await load_json(file_path);

  const elements: IC_Savefile_Element[] = data.elements;

  const len_elements = elements.length;

  const number_of_batches = 5000;
  const batch_size = Math.floor(len_elements / number_of_batches);

  for (let i = 0; i < len_elements; i += batch_size) {
    console.log(`Processing batch ${Math.round(i / batch_size)}`);
    const element_batch = elements.slice(i, i + batch_size);

    try {
      elements_db_manager.bulk_add_elements(
        element_batch.map((element) => [element.text, element.emoji])
      );
    } catch {}
  }
}
