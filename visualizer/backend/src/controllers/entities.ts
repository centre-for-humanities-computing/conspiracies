import { Request, Response } from "express";
import { getDataSource } from "../datasource";
import { EntityOrm } from "../orms/EntityOrm";
import { Details } from "@shared/types/graph";
import { DocumentOrm } from "../orms/DocumentOrm";
import { getDocs } from "../services/docs";

function transformEntityOrmToDetails(entity: EntityOrm): Details {
  return {
    id: entity.id,
    label: entity.label,
    frequency: entity.termFrequency,
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