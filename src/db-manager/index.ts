import { DatabaseManager } from "./db-manager";

type DB_IB_Element = {
  readonly id: string;
  readonly name: string;
  readonly emoji: string;
};

export class ElementsDatabaseManager extends DatabaseManager<
  DB_IB_Element,
  "elements"
> {
  constructor(db_path: string) {
    super(db_path, "elements");
  }

  add_element(name: string, emoji: string): void {
    this._insert_record({ id: name, name: name, emoji: emoji });
  }

  get_element(id: string): DB_IB_Element | null {
    const element = this._get_record({ condition: "id = ?", params: [id] });
    return element;
  }

  bulk_add_elements(elements: readonly (readonly [string, string])[]): void {
    const records = elements.map<DB_IB_Element>(([element_id, emoji]) => ({
      id: element_id,
      name: element_id,
      emoji,
    }));
    this._insert_records(["id", "name", "emoji"], records);
  }

  get_all_elements(options?: {
    offset?: number;
    limit?: number;
  }): DB_IB_Element[] {
    const elements = this._get_records({
      limit: options?.limit ?? 100,
      offset: options?.offset ?? 0,
    });
    return elements;
  }
}

type DB_IB_Recipe = {
  readonly id: string;
  readonly a: string;
  readonly b: string;
  readonly result: string;
};

export class RecipesDatabaseManager extends DatabaseManager<
  DB_IB_Recipe,
  "recipes"
> {
  constructor(db_path: string) {
    super(db_path, "recipes");
  }

  add_recipe(a: string, b: string, result: string): void {
    if (a > b) {
      [a, b] = [b, a];
    }
    const id = `${a}=${b}` as const;
    this._insert_record({ id, a, b, result });
  }

  get_all_recipes(result: string): DB_IB_Recipe[] | null {
    const recipes = this._get_records({
      condition: "result = ?",
      params: [result],
    });
    return recipes.length ? recipes : null;
  }

  bulk_add_recipes(
    recipes: readonly (readonly [string, string, string])[],
  ): void {
    const records: DB_IB_Recipe[] = [];
    for (let [a, b, result] of recipes) {
      if (a > b) {
        [a, b] = [b, a];
      }
      const id = `${a}=${b}` as const;
      records.push({ id, a, b, result });
    }
    console.log(`Adding ${records.length} recipes`);
    this._insert_records(["id", "a", "b", "result"], records);
  }
}
