import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import { DataSource, In } from "typeorm";
import { TripletOrm } from "../orms/TripletOrm";
import { DocumentOrm } from "../orms/DocumentOrm";

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
    synchronize: true,
  });
  await dataSource.initialize();
  return dataSource;
}

async function getDataSource() {
  if (dataSource === null) {
    dataSource = await createDataSource();
  }
  return dataSource;
}

export async function getGraph(req: Request, res: Response) {
  let ds = await getDataSource();

  const relations = await ds.getRepository(RelationOrm).find({
    take: 100,
    select: { id: true, label: true, subjectId: true, objectId: true },
    where: {},
  });
  const entityIds = relations.flatMap((r) => [r.subjectId, r.objectId]);
  let entities = await ds
    .getRepository(EntityOrm)
    .find({ where: { id: In(entityIds) } });
  res.json({
    edges: relations.map((r) => ({
      id: r.id,
      from: r.subjectId,
      to: r.objectId,
      label: r.label,
    })),
    nodes: entities,
  });
}
