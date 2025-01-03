import { Request, Response } from "express";
import { getDataSource } from "../datasource";
import { DocumentOrm } from "../orms/DocumentOrm";
import { Doc } from "@shared/types/doc";
import { In } from "typeorm";
import { getDoc, getDocs } from "../services/docs";

export async function getDocController(req: Request, res: Response) {
  const { id } = req.params;

  const doc = await getDoc(Number(id));
  if (doc === null) {
    res.status(404).send("Could not find document!");
    return;
  }
  res.json(doc);
}

export async function getDocsController(req: Request, res: Response) {
  const { ids } = req.body;
  const docs = await getDocs(ids);
  res.json(docs);
}
