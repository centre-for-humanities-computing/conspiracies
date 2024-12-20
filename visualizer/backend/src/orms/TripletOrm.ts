import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  PrimaryGeneratedColumn,
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
  subjSpanStart!: number;

  @Column("integer", { name: "subj_span_end" })
  subjSpanEnd!: number;

  @Column("text", { name: "subj_span_text" })
  subjSpanText!: string;

  @Column("integer", { name: "pred_span_start" })
  predSpanStart!: number;

  @Column("integer", { name: "pred_span_end" })
  predSpanEnd!: number;

  @Column("text", { name: "pred_span_text" })
  predSpanText!: string;

  @Column("integer", { name: "obj_span_start" })
  objSpanStart!: number;

  @Column("integer", { name: "obj_span_end" })
  objSpanEnd!: number;

  @Column("text", { name: "obj_span_text" })
  objSpanText!: string;

  @ManyToOne(() => DocumentOrm, (document: DocumentOrm) => document.triplets)
  @JoinColumn({ name: "doc_id" })
  document!: DocumentOrm;

  @ManyToOne(() => EntityOrm)
  @JoinColumn({ name: "subject_id" })
  subjectEntity!: EntityOrm;

  @ManyToOne(() => RelationOrm)
  @JoinColumn({ name: "relation_id" })
  predicateRelation!: RelationOrm;

  @ManyToOne(() => EntityOrm)
  @JoinColumn({ name: "object_id" })
  objectEntity!: EntityOrm;
}
