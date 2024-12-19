import {
  Column,
  Entity,
  Index,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryGeneratedColumn,
} from "typeorm";
import { EntityOrm } from "./EntityOrm";
import { TripletOrm } from "./TripletOrm";

@Entity("relations")
export class RelationOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column("text")
  @Index()
  label!: string;

  @Column("integer", { name: "subject_id" })
  subjectId!: number;

  @Column("integer", { name: "object_id" })
  objectId!: number;

  @ManyToOne(() => EntityOrm, { nullable: true })
  @JoinColumn({ name: "subject_id" })
  subject!: EntityOrm | null;

  @ManyToOne(() => EntityOrm, { nullable: true })
  @JoinColumn({ name: "object_id" })
  object!: EntityOrm | null;

  @OneToMany(() => TripletOrm, (triplet) => triplet.predicateRelation)
  triplets!: TripletOrm[];
}
