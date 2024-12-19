import { Request, Response } from "express";
import { getDataSource } from "../datasource";
import { DocumentOrm } from "../orms/DocumentOrm";
import { Doc } from "@shared/types/doc";
import { In } from "typeorm";

function transformOrmToDto(docOrm: DocumentOrm): Doc {
  return {
    id: docOrm.id!,
    text: docOrm.text!,
    timestamp: docOrm.timestamp!,
    triplets: docOrm.triplets!.map((tripletOrm) => ({
      subject: {
        id: tripletOrm.subjectId,
        start: tripletOrm.subjSpanStart,
        end: tripletOrm.subjSpanEnd,
      },
      predicate: {
        id: tripletOrm.relationId,
        start: tripletOrm.predSpanStart,
        end: tripletOrm.predSpanEnd,
      },
      object: {
        id: tripletOrm.objectId,
        start: tripletOrm.objSpanStart,
        end: tripletOrm.objSpanEnd,
      },
    })),
  };
}

export async function getDoc(req: Request, res: Response) {
  const { id } = req.params;

  let ds = await getDataSource();
  const docOrm = await ds.getRepository(DocumentOrm).findOne({
    where: { id: Number(id) },
    relations: ["triplets"],
  });
  if (docOrm === null) {
    res.status(404).send("Could not find document!");
    return;
  }
  res.json(transformOrmToDto(docOrm));
}

export async function getDocs(req: Request, res: Response) {
  const { ids } = req.body;

  let ds = await getDataSource();
  const docOrms = await ds.getRepository(DocumentOrm).find({
    where: { id: In(ids) },
    relations: ["triplets"],
  });
  if (docOrms === null) {
    res.status(404).send("Could not find documents!");
    return;
  }
  const dtos = docOrms.map(transformOrmToDto);
  res.json(dtos);
}
