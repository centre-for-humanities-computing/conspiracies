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
@Unique(["docId", "subjectId", "relationId", "objectId"]) // Matches the Python unique constraint
export class TripletOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column("integer")
  docId!: number;

  @Column("integer")
  subjectId!: number;

  @Column("integer")
  relationId!: number;

  @Column("integer")
  objectId!: number;

  @Column("integer", { nullable: true })
  subjSpanStart!: number | null;

  @Column("integer", { nullable: true })
  subjSpanEnd!: number | null;

  @Column("integer", { nullable: true })
  predSpanStart!: number | null;

  @Column("integer", { nullable: true })
  predSpanEnd!: number | null;

  @Column("integer", { nullable: true })
  objSpanStart!: number | null;

  @Column("integer", { nullable: true })
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
