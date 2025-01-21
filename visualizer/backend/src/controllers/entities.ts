import { Request, Response } from "express";
import { getDataSource } from "../datasource";
import { EntityOrm } from "../orms/EntityOrm";
import { Details } from "@shared/types/graph";
import { DocumentOrm } from "../orms/DocumentOrm";
import { getDocs } from "../services/docs";
import { In } from "typeorm";

function transformEntityOrmToDetails(entity: EntityOrm): Details {
  // const altLabels = entity.subjectTriplets
  //   .map((t) => t.subjSpanText)
  //   .concat(entity.objectTriplets.map((t) => t.objSpanText));
  // const countMap: Record<string, number> = altLabels.reduce(
  //   (acc, item) => {
  //     acc[item] = (acc[item] || 0) + 1;
  //     return acc;
  //   },
  //   {} as Record<string, number>,
  // );
  // const sortedAltLabels = Object.keys(countMap)
  //   .filter((al) => al !== entity.label)
  //   .sort((a, b) => countMap[b] - countMap[a]);

  return {
    id: entity.id,
    label: entity.label,
    frequency: entity.termFrequency,
    docFrequency: entity.docFrequency,
    altLabels: [],
    firstOccurrence: entity.firstOccurrence,
    lastOccurrence: entity.lastOccurrence,
  };
}

export async function getEntity(req: Request, res: Response) {
  const { id } = req.params;

  let ds = await getDataSource();

  const entity = await ds.getRepository(EntityOrm).findOne({
    where: { id: Number(id) },
    // relations: { subjectTriplets: true, objectTriplets: true },
  });
  if (!entity) {
    res.status(404).send("Node/Entity not found.");
    return;
  }
  res.json(transformEntityOrmToDetails(entity));
}

export async function getTriplets(req: Request, res: Response) {
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

export async function getDocsByEntity(req: Request, res: Response) {
  const { id } = req.params;
  const { limit } = req.query;

  let ds = await getDataSource();

  const docIds = await ds.getRepository(DocumentOrm).find({
    select: { id: true },
    where: { triplets: [{ subjectId: Number(id) }, { objectId: Number(id) }] },
    take: limit ? Number(limit) : undefined,
  });

  if (docIds.length === 0) {
    res.status(404).send("No documents found.");
    return;
  }

  const docs = await getDocs(docIds.map((d) => d.id));

  res.json(docs);
}

export async function getEntityLabels(req: Request, res: Response) {
  const ids: number[] = req.body.ids;
  let ds = await getDataSource();

  const entityLabels = await ds.getRepository(EntityOrm).find({
    select: { id: true, label: true },
    where: { id: In(ids) },
  });

  if (entityLabels.length === 0) {
    res.status(404).send("No entities found.");
    return;
  }

  res.json(entityLabels.map((d) => ({ id: d.id, label: d.label })));
}
