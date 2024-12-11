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

  @Column()
  docId!: number;

  @Column()
  subjectId!: number;

  @Column()
  relationId!: number;

  @Column()
  objectId!: number;

  @Column({ nullable: true })
  subjSpanStart!: number | null;

  @Column({ nullable: true })
  subjSpanEnd!: number | null;

  @Column({ nullable: true })
  predSpanStart!: number | null;

  @Column({ nullable: true })
  predSpanEnd!: number | null;

  @Column({ nullable: true })
  objSpanStart!: number | null;

  @Column({ nullable: true })
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
