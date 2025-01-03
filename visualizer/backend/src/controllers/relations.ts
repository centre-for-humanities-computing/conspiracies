import { Request, Response } from "express";
import { RelationOrm } from "../orms/RelationOrm";
import { getDataSource } from "../datasource";
import { Details } from "@shared/types/graph";
import { DocumentOrm } from "../orms/DocumentOrm";
import { getDocs, transformOrmToDto } from "../services/docs";

function transformRelationOrmToDetails(relation: RelationOrm): Details {
  return {
    id: relation.id,
    label: relation.label,
    frequency: relation.termFrequency,
    altLabels: [],
    firstOccurrence: undefined,
    lastOccurrence: undefined,
  };
}

export async function getRelation(req: Request, res: Response) {
  const { id } = req.params;

  let ds = await getDataSource();

  const relation = await ds.getRepository(RelationOrm).findOne({
    where: { id: Number(id) },
  });
  if (!relation) {
    res.status(404).send("Relation not found.");
    return;
  }
  res.json(transformRelationOrmToDetails(relation));
}

export async function getDocsByRelation(req: Request, res: Response) {
  const { id } = req.params;
  const { limit } = req.query;

  let ds = await getDataSource();

  const docIds = await ds.getRepository(DocumentOrm).find({
    select: { id: true },
    where: { triplets: { relationId: Number(id) } },
    take: limit ? Number(limit) : undefined,
  });

  if (docIds.length === 0) {
    res.status(404).send("No documents found.");
    return;
  }

  const docs = await getDocs(docIds.map((d) => d.id));

  res.json(docs);
}
