import {
  Column,
  DataSource,
  Entity,
  ManyToOne,
  PrimaryGeneratedColumn,
  Unique,
} from "typeorm";
import { EntityOrm } from "./EntityOrm";
import { RelationOrm } from "./RelationOrm";
import { DocumentOrm } from "./DocumentOrm";

@Entity("triplets")
// @Unique(["doc_id", "subject_id", "relation_id", "object_id"])
export class TripletOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column("integer", { name: "doc_id" })
  docId!: number;

  @Column("integer", { name: "subject_id" })
  subjectId!: number;

  @Column("integer", { name: "relation_id" })
  relationId!: number;

  @Column("integer", { name: "object_id" })
  objectId!: number;

  @Column("integer", { name: "subj_span_start" })
  subjSpanStart!: number | null;

  @Column("integer", { name: "subj_span_end", nullable: true })
  subjSpanEnd!: number | null;

  @Column("integer", { name: "pred_span_start", nullable: true })
  predSpanStart!: number | null;

  @Column("integer", { name: "pred_span_end", nullable: true })
  predSpanEnd!: number | null;

  @Column("integer", { name: "obj_span_start", nullable: true })
  objSpanStart!: number | null;

  @Column("integer", { name: "obj_span_end", nullable: true })
  objSpanEnd!: number | null;

  @ManyToOne(() => DocumentOrm, (document: DocumentOrm) => document.triplets)
  document!: DocumentOrm;

  @ManyToOne(() => EntityOrm)
  subjectEntity!: EntityOrm;

  @ManyToOne(() => RelationOrm)
  predicateRelation!: RelationOrm;

  @ManyToOne(() => EntityOrm)
  objectEntity!: EntityOrm;
}
