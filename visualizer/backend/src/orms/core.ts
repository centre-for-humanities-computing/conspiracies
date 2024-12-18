import { DataSource, In } from "typeorm";
import { RelationOrm } from "./RelationOrm";
import { EntityOrm } from "./EntityOrm";
import { TripletOrm } from "./TripletOrm";
import { DocumentOrm } from "./DocumentOrm";

export class GraphBackend {
  dataSource: DataSource;

  constructor(dataSource: DataSource) {
    this.dataSource = dataSource;
  }

  async getGraph(): Promise<any> {
    const relations = await this.dataSource.getRepository(RelationOrm).find({
      take: 100,
      select: { id: true, label: true, subjectId: true, objectId: true },
      where: {},
    });
    const entityIds = relations.flatMap((r) => [r.subjectId, r.objectId]);
    let entities = await this.dataSource
      .getRepository(EntityOrm)
      .find({ where: { id: In(entityIds) } });
    return { edges: relations, nodes: entities };
  }
  //
  // getBounds(): Promise<DataBounds> {
  //   throw new Error("Method not implemented.");
  // }
  //
  // getSubGraph(nodeIds: Set<string>): Promise<EnrichedGraphData> {
  //   throw new Error("Method not implemented.");
  // }
  //
  // getConnectedNodes(nodeId: string): Promise<Set<string>> {
  //   throw new Error("Method not implemented.");
  // }
}

export function createDataSource(path: string) {
  return new DataSource({
    type: "sqlite",
    database: path,
    entities: [EntityOrm, RelationOrm, TripletOrm, DocumentOrm],
    synchronize: true,
  });
}
