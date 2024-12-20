import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import {
  Between,
  FindOptionsWhere,
  In,
  LessThanOrEqual,
  Like,
  MoreThanOrEqual,
} from "typeorm";
import { getDataSource } from "../datasource";
import { Details, Edge } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

function transformEntityOrmToDetails(entity: EntityOrm): Details {
  const docs = [
    ...new Set(
      [...entity.subjectTriplets, ...entity.objectTriplets].map((t) => t.docId),
    ),
  ];

  return {
    id: entity.id,
    label: entity.label,
    frequency: entity.termFrequency,
    altLabels: [],
    docs: docs,
    firstOccurrence: undefined,
    lastOccurrence: undefined,
  };
}

function transformRelationOrmToDetails(relation: RelationOrm): Details {
  const docs = [...new Set(relation.triplets)].map((t) => t.docId);

  return {
    id: relation.id,
    label: relation.label,
    frequency: relation.termFrequency,
    altLabels: [],
    docs: docs,
    firstOccurrence: undefined,
    lastOccurrence: undefined,
  };
}

function rangeFilter(min: any | undefined, max: any | undefined) {
  if (min !== undefined && max !== undefined) {
    return Between(min, max);
  } else if (min !== undefined) {
    return MoreThanOrEqual(min);
  } else if (max !== undefined) {
    return LessThanOrEqual(max);
  } else {
    return undefined;
  }
}

export async function getGraph(req: Request, res: Response) {
  const graphFilter: GraphFilter = req.body.graphFilter;

  let ds = await getDataSource();

  const relationFindOptions: FindOptionsWhere<RelationOrm> = {
    termFrequency: rangeFilter(
      graphFilter.minimumEdgeFrequency,
      graphFilter.maximumEdgeFrequency,
    ),
  };
  const entityFindOptions: FindOptionsWhere<EntityOrm> = {
    label: graphFilter.labelSearch
      ? Like(`%${graphFilter.labelSearch}%`)
      : undefined,
    termFrequency: rangeFilter(
      graphFilter.minimumNodeFrequency,
      graphFilter.maximumNodeFrequency,
    ),
  };

  const entities = await ds.getRepository(EntityOrm).find({
    take: graphFilter.limit,
    select: { id: true, label: true, termFrequency: true },
    where: entityFindOptions,
    order: { termFrequency: "desc" },
  });
  const entityMap = new Map(entities.map((e) => [e.id, e]));
  const entityIds = [...new Set(entities.map((e) => e.id))];

  const relations = await ds.getRepository(RelationOrm).find({
    select: {
      id: true,
      label: true,
      subjectId: true,
      objectId: true,
      termFrequency: true,
    },
    where: {
      ...relationFindOptions,
      subjectId: In(entityIds),
      objectId: In(entityIds),
    },
  });
  let groupedEdges = relations.reduce(
    (acc, curr) => {
      const key = curr.subjectId + "->" + curr.objectId;
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(curr);
      return acc;
    },
    {} as Record<string, RelationOrm[]>,
  );
  let edges: Edge[] = Object.values(groupedEdges).map((group) => {
    group.sort((edge1, edge2) => edge2.termFrequency - edge1.termFrequency);
    const representative: RelationOrm = group.at(0)!;
    return {
      id: representative.subjectId + "->" + representative.objectId,
      from: representative.subjectId,
      subjectLabel: entityMap.get(representative.subjectId)!.label,
      to: representative.objectId,
      objectLabel: entityMap.get(representative.objectId)!.label,
      label: group
        .slice(0, 3)
        .map((e) => e.label)
        .join(", "),
      width: Math.log10(
        group.map((e) => e.termFrequency).reduce((a, b) => a + b),
      ),
      group: group.map((r) => ({ id: r.id, label: r.label })),
    };
  });

  res.json({
    edges: edges,
    nodes: entities,
  });
}

export async function getBounds(req: Request, res: Response) {
  let ds = await getDataSource();
  let entityOrmRepository = ds.getRepository(EntityOrm);
  let relationOrmRepository = ds.getRepository(RelationOrm);

  const dataBounds: DataBounds = {
    minimumPossibleNodeFrequency:
      (await entityOrmRepository.minimum("termFrequency")) || 0,
    maximumPossibleNodeFrequency:
      (await entityOrmRepository.maximum("termFrequency")) || NaN,
    minimumPossibleEdgeFrequency:
      (await relationOrmRepository.minimum("termFrequency")) || 0,
    maximumPossibleEdgeFrequency:
      (await relationOrmRepository.maximum("termFrequency")) || NaN,
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
  res.json(transformEntityOrmToDetails(entity));
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
  res.json(transformRelationOrmToDetails(relation));
}
