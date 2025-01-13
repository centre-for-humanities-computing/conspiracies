import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { EntityOrm } from "../orms/EntityOrm";
import {
  And,
  Between,
  FindOptionsWhere,
  In,
  LessThanOrEqual,
  Like,
  MoreThanOrEqual,
  Not,
} from "typeorm";
import { getDataSource } from "../datasource";
import { Edge } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

function dateFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm | RelationOrm> {
  return {
    lastOccurrence: graphFilter.earliestDate
      ? MoreThanOrEqual(graphFilter.earliestDate)
      : undefined,
    firstOccurrence: graphFilter.latestDate
      ? LessThanOrEqual(graphFilter.latestDate)
      : undefined,
  };
}

function termFrequencyFilter(
  min: number | undefined,
  max: number | undefined,
): FindOptionsWhere<EntityOrm | RelationOrm> {
  let filter;
  if (min !== undefined && max !== undefined) {
    return { termFrequency: Between(min, max) };
  } else if (min !== undefined) {
    return { termFrequency: MoreThanOrEqual(min) };
  } else if (max !== undefined) {
    return { termFrequency: LessThanOrEqual(max) };
  } else {
    return {};
  }
}

function entityTermFrequencyFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm> {
  return termFrequencyFilter(
    graphFilter.minimumNodeFrequency,
    graphFilter.maximumNodeFrequency,
  );
}

function relationTermFrequencyFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<RelationOrm> {
  return termFrequencyFilter(
    graphFilter.minimumEdgeFrequency,
    graphFilter.maximumEdgeFrequency,
  );
}

function entitySupernodeFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm> {
  if (graphFilter.onlySupernodes) {
    return { isSupernode: true };
  } else {
    return {};
  }
}

function entityBlacklistFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm> {
  if (graphFilter.blacklistedEntityIds) {
    return {
      id: Not(In(graphFilter.blacklistedEntityIds)),
    };
  } else {
    return {};
  }
}

function entityWhitelistFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm> {
  if (graphFilter.whitelistedEntityIds) {
    return { id: In(graphFilter.whitelistedEntityIds) };
  } else {
    return {};
  }
}

function entityLabelFilter(
  graphFilter: GraphFilter,
): FindOptionsWhere<EntityOrm> {
  if (graphFilter.labelSearch) {
    return { label: Like(`%${graphFilter.labelSearch}%`) };
  } else {
    return {};
  }
}

function createEdgeGroups(relations: RelationOrm[], bySupernodeId: boolean) {
  let groupedEdges = relations.reduce(
    (acc, curr) => {
      const key = bySupernodeId
        ? curr.subject.supernodeId + "->" + curr.object.supernodeId
        : curr.subjectId + "->" + curr.objectId;
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
    const fromId = bySupernodeId
      ? representative.subject.supernodeId!
      : representative.subject.id;
    const toId = bySupernodeId
      ? representative.object.supernodeId!
      : representative.object.id;
    return {
      id: fromId + "->" + toId,
      from: fromId,
      to: toId,
      subjectLabel: representative.subject.label,
      objectLabel: representative.object.label,
      label:
        group
          .slice(0, 3)
          .map((e) => e.label)
          .join(", ") + (group.length > 3 ? ", ..." : ""),
      totalTermFrequency: group
        .map((e) => e.termFrequency)
        .reduce((a, b) => a + b),
      group: group.map((r) => ({ id: r.id, label: r.label })),
    };
  });
  return edges;
}

export async function getGraph(req: Request, res: Response) {
  const graphFilter: GraphFilter = req.body.graphFilter;
  const onlySupernodes: boolean = graphFilter.onlySupernodes || false;

  let ds = await getDataSource();

  const entityFilter: FindOptionsWhere<EntityOrm> = {
    ...dateFilter(graphFilter),
    ...entityTermFrequencyFilter(graphFilter),
    ...entityBlacklistFilter(graphFilter),
    ...entitySupernodeFilter(graphFilter),
  };

  const relationFilter = {
    ...dateFilter,
    ...relationTermFrequencyFilter(graphFilter),
  };

  let focusEntityIds: number[] = [];
  let entities: EntityOrm[];

  if (graphFilter.whitelistedEntityIds || graphFilter.labelSearch) {
    const focusFilters = [];
    if (graphFilter.whitelistedEntityIds) {
      focusFilters.push({
        ...entityWhitelistFilter(graphFilter),
        ...entitySupernodeFilter(graphFilter),
      });
    }
    if (graphFilter.labelSearch) {
      focusFilters.push({
        ...entityLabelFilter(graphFilter),
        ...entitySupernodeFilter(graphFilter),
      });
    }

    const focusEntities: EntityOrm[] = await ds.getRepository(EntityOrm).find({
      take: graphFilter.limitNodes,
      select: { id: true, label: true, termFrequency: true },
      relations: { supernode: true, subnodes: onlySupernodes },
      where: focusFilters,
      order: { termFrequency: "desc" },
    });

    focusEntityIds = focusEntities.map((e) => e.id);

    let extraEntities: EntityOrm[] = [];
    if (focusEntities.length < graphFilter.limitNodes) {
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
        take: graphFilter.limitNodes - focusEntities.length,
        select: { id: true, label: true, termFrequency: true },
        relations: { supernode: true, subnodes: onlySupernodes },
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
      take: graphFilter.limitNodes,
      select: { id: true, label: true, termFrequency: true },
      relations: { supernode: true, subnodes: onlySupernodes },
      where: entityFilter,
      order: { termFrequency: "desc" },
    });
  }

  const entityIds = entities.map((e) => e.id);

  if (onlySupernodes) {
    const subEntities = await ds.getRepository(EntityOrm).find({
      select: { id: true, label: true, termFrequency: true, supernodeId: true },
      where: {
        ...entityFilter,
        supernodeId: In(entityIds),
        isSupernode: false,
      },
    });
    entityIds.push(...subEntities.map((e) => e.id));
    entities = entities.map((e) => ({
      ...e,
      subnodes: e
        .subnodes!.filter((sn) => entityIds.indexOf(sn.id) > -1)
        .filter((sn) => sn.id !== e.id)
        .sort((sn1, sn2) => sn2.termFrequency - sn1.termFrequency),
    }));
  }

  const relations = await ds.getRepository(RelationOrm).find({
    select: {
      id: true,
      label: true,
      subjectId: true,
      objectId: true,
      termFrequency: true,
    },
    relations: {
      subject: true,
      object: true,
    },
    where: [
      {
        subjectId: In(focusEntityIds),
        objectId: In(focusEntityIds),
      },
      {
        ...relationFilter,
        subjectId: In(entityIds),
        objectId: In(entityIds),
      },
    ],
  });

  let edges = createEdgeGroups(relations, onlySupernodes);
  edges = edges
    .sort((a, b) => b.totalTermFrequency! - a.totalTermFrequency!)
    .slice(0, graphFilter.limitEdges);

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
