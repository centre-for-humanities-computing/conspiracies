import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import { Between, In, LessThanOrEqual, Like, MoreThanOrEqual } from "typeorm";
import { getDataSource } from "../datasource";
import { Edge } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

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

  // console.log(graphFilter)

  let ds = await getDataSource();

  const dateFilter = {
    lastOccurrence: graphFilter.earliestDate
      ? MoreThanOrEqual(graphFilter.earliestDate)
      : undefined,
    firstOccurrence: graphFilter.latestDate
      ? LessThanOrEqual(graphFilter.latestDate)
      : undefined,
  };

  const entityLabelFilter = {
    label: graphFilter.labelSearch
      ? Like(`%${graphFilter.labelSearch}%`)
      : undefined,
  };
  const entityFreqFilter = {
    termFrequency: rangeFilter(
      graphFilter.minimumNodeFrequency,
      graphFilter.maximumNodeFrequency,
    ),
  };

  const entityFilter = {
    ...dateFilter,
    ...entityFreqFilter,
    ...entityLabelFilter,
  };

  const relationFilter = {
    ...dateFilter,
    termFrequency: rangeFilter(
      graphFilter.minimumEdgeFrequency,
      graphFilter.maximumEdgeFrequency,
    ),
  };

  const whiteListedEntities = graphFilter.whitelistedEntityIds
    ? await ds.getRepository(EntityOrm).find({
        take: graphFilter.limit,
        select: { id: true, label: true, termFrequency: true },
        where: {
          id: In(graphFilter.whitelistedEntityIds),
        },
        order: { termFrequency: "desc" },
      })
    : [];

  const extraEntities = await ds.getRepository(EntityOrm).find({
    take: graphFilter.limit - whiteListedEntities.length,
    select: { id: true, label: true, termFrequency: true },
    where: [
      {
        ...entityFilter,
        subjectRelations: graphFilter.whitelistedEntityIds
          ? {
              ...relationFilter,
              objectId: In(graphFilter.whitelistedEntityIds),
            }
          : undefined,
      },
      {
        ...entityFilter,
        objectRelations: graphFilter.whitelistedEntityIds
          ? {
              ...relationFilter,
              subjectId: In(graphFilter.whitelistedEntityIds),
            }
          : undefined,
      },
    ],
    order: { termFrequency: "desc" },
  });
  const entities = whiteListedEntities.concat(extraEntities);
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
      ...dateFilter,
      termFrequency: rangeFilter(
        graphFilter.minimumEdgeFrequency,
        graphFilter.maximumEdgeFrequency,
      ),
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
