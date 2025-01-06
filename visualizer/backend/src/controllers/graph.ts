import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import {
  And,
  Between,
  In,
  LessThanOrEqual,
  Like,
  MoreThanOrEqual,
  Not,
} from "typeorm";
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
  const entityWhitelistFilter = {
    id: graphFilter.whitelistedEntityIds
      ? In(graphFilter.whitelistedEntityIds)
      : undefined,
  };
  const entityBlacklistFilter = {
    id: graphFilter.blacklistedEntityIds
      ? Not(In(graphFilter.blacklistedEntityIds))
      : undefined,
  };

  const entityFilter = {
    ...dateFilter,
    ...entityFreqFilter,
    ...entityBlacklistFilter,
  };

  const relationFilter = {
    ...dateFilter,
    termFrequency: rangeFilter(
      graphFilter.minimumEdgeFrequency,
      graphFilter.maximumEdgeFrequency,
    ),
  };

  let entities;

  if (graphFilter.whitelistedEntityIds || graphFilter.labelSearch) {
    const focusEntities = await ds.getRepository(EntityOrm).find({
      take: graphFilter.limit,
      select: { id: true, label: true, termFrequency: true },
      where: [entityWhitelistFilter, entityLabelFilter],
      order: { termFrequency: "desc" },
    });

    let extraEntities: EntityOrm[] = [];
    if (focusEntities.length < graphFilter.limit) {
      const focusEntityIds = focusEntities.map((e) => e.id);
      const connections = await ds.getRepository(RelationOrm).find({
        select: {
          subjectId: true,
          objectId: true,
        },
        where: [
          {
            ...relationFilter,
            subjectId: In(focusEntityIds),
          },
          {
            ...relationFilter,
            objectId: In(focusEntityIds),
          },
        ],
      });

      const connectedEntityIds = connections
        .flatMap((conn) => [conn.subjectId, conn.objectId])
        .filter((id) => focusEntityIds.indexOf(id) === -1);

      extraEntities = await ds.getRepository(EntityOrm).find({
        take: graphFilter.limit - focusEntities.length,
        select: { id: true, label: true, termFrequency: true },
        where: {
          ...entityFilter,
          // have to rebuild the ID condition here
          id: And(
            In(connectedEntityIds),
            Not(In(graphFilter.blacklistedEntityIds || [])),
          ),
        },
        order: { termFrequency: "desc" },
      });
    }

    entities = focusEntities
      .map((e) => ({ ...e, focus: true }))
      .concat(extraEntities.map((e) => ({ ...e, focus: false })));
  } else {
    entities = await ds.getRepository(EntityOrm).find({
      take: graphFilter.limit,
      select: { id: true, label: true, termFrequency: true },
      where: entityFilter,
      order: { termFrequency: "desc" },
    });
  }

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
      ...relationFilter,
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
