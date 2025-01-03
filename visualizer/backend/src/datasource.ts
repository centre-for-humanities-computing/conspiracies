import { DataSource } from "typeorm";
import { EntityOrm } from "./orms/EntityOrm";
import { RelationOrm } from "./orms/RelationOrm";
import { TripletOrm } from "./orms/TripletOrm";
import { DocumentOrm } from "./orms/DocumentOrm";

let dataSource: DataSource | null = null;

async function createDataSource() {
  const path = process.env.DB_PATH;
  if (path === undefined) {
    console.error("Error: DB_PATH environment variable is not set.");
    process.exit(1);
  }
  const dataSource = new DataSource({
    type: "sqlite",
    database: path,
    entities: [EntityOrm, RelationOrm, TripletOrm, DocumentOrm],
    synchronize: false,
  });
  await dataSource.initialize();
  return dataSource;
}

export async function getDataSource() {
  if (dataSource === null) {
    dataSource = await createDataSource();
  }
  return dataSource;
}
