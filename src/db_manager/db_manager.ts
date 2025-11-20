import { Database } from "bun:sqlite";

type Param = number | string | null;
type Params = Param[];

export class DatabaseManager<
  TSchema extends Record<string, string>,
  TTable extends string
> {
  readonly db_path: string;
  private readonly _TABLE: TTable;

  constructor(db_path: string, table: TTable) {
    this.db_path = db_path;
    this._TABLE = table;
  }

  private _connect(): Database {
    return new Database(this.db_path);
  }

  protected _insert_record(values: TSchema): void {
    const columns = Object.keys(values);
    const params = Object.values(values);
    const placeholders = Array(columns.length).fill("?").join(", ");
    const col_names = columns.join(", ");
    const query =
      `INSERT INTO ${this._TABLE} (${col_names}) VALUES (${placeholders})` as const;
    const db = this._connect();
    db.query(query).run(...params);
    db.close();
  }

  protected _insert_records(
    columns: readonly (keyof TSchema)[],
    records: readonly TSchema[]
  ): void {
    const columns_str = columns.join(", ");
    const placeholders = Array(columns.length).fill("?").join(", ");
    const query =
      `INSERT OR IGNORE INTO ${this._TABLE} (${columns_str}) VALUES (${placeholders})` as const;
    const db = this._connect();
    const stmt = db.query<unknown, TSchema[keyof TSchema][]>(query);
    const insertBatch = db.transaction((batchRecords: readonly TSchema[]) => {
      for (const record of batchRecords) {
        const values = columns.map((col) => record[col]);
        stmt.run(...values);
      }
    });

    insertBatch(records);
    db.close();
  }

  protected _get_records({
    condition,
    params,
    limit,
    offset,
  }: {
    condition?: string;
    params?: Params;
    limit?: number;
    offset?: number;
  }): TSchema[] {
    if (!params) params = [];
    let query = `SELECT * FROM ${this._TABLE}`;
    if (condition) {
      query += ` WHERE ${condition}` as const;
    }
    if (limit !== undefined) {
      query += " LIMIT ?";
      params.push(limit);
    }
    if (offset !== undefined) {
      query += " OFFSET ?";
      params.push(offset);
    }
    const db = this._connect();
    const records = db.query<TSchema, Params>(query).all(...params);
    db.close();
    return records;
  }

  protected _get_record({
    condition,
    params,
  }: {
    condition: string;
    params?: Params;
  }): TSchema | null {
    const query = `SELECT * FROM ${this._TABLE} WHERE ${condition}` as const;
    const db = this._connect();
    const records = db
      .query<TSchema, Params>(query)
      .all(...(params ? params : []));
    db.close();
    if (records.length > 1) {
      throw new Error("More than one record!");
    }
    if (!records) {
      return null;
    }
    return records[0]!;
  }

  protected _update_record({
    updates,
    condition,
    params,
  }: {
    updates: Record<string, Param>;
    condition: string;
    params: Params;
  }) {
    const columns_str = Object.keys(updates)
      .map((col) => `${col}=?`)
      .join(", ");
    const update_values = Object.values(updates);
    const query =
      `UPDATE ${this._TABLE} SET ${columns_str} WHERE ${condition}` as const;

    const db = this._connect();
    db.query(query).run(...update_values.concat(params));
    db.close();
  }
}
