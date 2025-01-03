import { getDataSource } from "../datasource";
import { DocumentOrm } from "../orms/DocumentOrm";
import { In } from "typeorm";
import { Doc } from "@shared/types/doc";

export function transformOrmToDto(docOrm: DocumentOrm): Doc {
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

export async function getDoc(id: number) {
  let ds = await getDataSource();
  const docOrm = await ds.getRepository(DocumentOrm).findOne({
    where: { id: id },
    relations: ["triplets"],
  });
  if (docOrm === null) {
    return null;
  }
  return transformOrmToDto(docOrm);
}

export async function getDocs(ids: number[], limit?: number) {
  let ds = await getDataSource();
  const docOrms = await ds.getRepository(DocumentOrm).find({
    take: limit,
    where: { id: In(ids) },
    relations: ["triplets"],
  });
  return docOrms.map(transformOrmToDto);
}
