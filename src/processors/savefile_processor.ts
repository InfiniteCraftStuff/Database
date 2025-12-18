import * as z from "zod";

import { ElementsDatabaseManager } from "~/db_manager";

const SavefileSchema = z.object({
  elements: z.array(z.object({ text: z.string(), emoji: z.string() })),
});

export async function process_savefile(file_path: string, db_path: string) {
  const elements_db_manager = new ElementsDatabaseManager(db_path);

  const file = Bun.file(file_path);
  const data = SavefileSchema.parse(await file.json());
  const elements = data.elements;

  const elements_count = elements.length;

  const number_of_batches = 5000;
  const batch_size = Math.floor(elements_count / number_of_batches);

  for (let i = 0; i < elements_count; i += batch_size) {
    console.log(`Processing batch ${Math.round(i / batch_size)}`);
    const element_batch = elements.slice(i, i + batch_size);

    try {
      elements_db_manager.bulk_add_elements(
        element_batch.map((element) => [element.text, element.emoji]),
      );
    } catch {}
  }
}
