import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import { FindManyOptions, In, Like } from "typeorm";
import { getDataSource } from "../datasource";
import { EnrichedEdge, EnrichedNode } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

function transformEntityOrmToEnrichedNode(entity: EntityOrm): EnrichedNode {
  const frequency =
    entity.subjectTriplets.length + entity.objectTriplets.length;
  const docs = [
    ...new Set(
      [...entity.subjectTriplets, ...entity.objectTriplets].map((t) => t.docId),
    ),
  ];

  return {
    id: entity.id,
    label: entity.label,
    frequency: frequency,
    altLabels: [],
    docs: docs,
    firstOccurrence: "",
    lastOccurrence: "",
  };
}

function transformRelationOrmToEnrichedEdge(
  relation: RelationOrm,
): EnrichedEdge {
  const frequency = relation.triplets.length;
  const docs = [...new Set(relation.triplets)].map((t) => t.docId);

  return {
    id: relation.id,
    label: relation.label,
    from: relation.subjectId.toString(),
    subjectLabel: relation.subject!.label,
    to: relation.objectId.toString(),
    objectLabel: relation.object!.label,
    frequency: frequency,
    altLabels: [],
    docs: docs,
    firstOccurrence: "",
    lastOccurrence: "",
  };
}

export async function getGraph(req: Request, res: Response) {
  let findOptions: FindManyOptions;
  const graphFilter: GraphFilter = req.body.graphFilter;
  if (graphFilter) {
    findOptions = {
      take: graphFilter.limit,
      select: { id: true, label: true, subjectId: true, objectId: true },
      where: {
        label: Like(`%${graphFilter.labelSearch}%`),
      },
    };
  } else {
    findOptions = {
      take: 100,
      select: { id: true, label: true, subjectId: true, objectId: true },
      where: {},
    };
  }

  let ds = await getDataSource();

  const relations = await ds.getRepository(RelationOrm).find(findOptions);
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

export async function getBounds(req: Request, res: Response) {
  // let ds = await getDataSource();
  const dataBounds: DataBounds = {
    minimumPossibleNodeFrequency: 1,
    maximumPossibleNodeFrequency: 1000,
    minimumPossibleEdgeFrequency: 1,
    maximumPossibleEdgeFrequency: 1000,
  };
  res.json(dataBounds);
}

export async function getEntity(req: Request, res: Response) {
  const { id } = req.params;

  let ds = await getDataSource();

  const entity = await ds.getRepository(EntityOrm).findOne({
    where: { id: Number(id) },
    relations: ["subjectTriplets", "objectTriplets"],
  });
  if (!entity) {
    res.status(404).send("Node/Entity not found.");
    return;
  }
  res.json(transformEntityOrmToEnrichedNode(entity));
}

export async function getRelation(req: Request, res: Response) {
  const { id } = req.params;

  let ds = await getDataSource();

  const relation = await ds.getRepository(RelationOrm).findOne({
    where: { id: Number(id) },
    relations: ["subject", "object", "triplets"],
  });
  if (!relation) {
    res.status(404).send("Node/Entity not found.");
    return;
  }
  res.json(transformRelationOrmToEnrichedEdge(relation));
}
