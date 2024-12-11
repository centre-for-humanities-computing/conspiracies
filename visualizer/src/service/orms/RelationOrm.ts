import {
  Column,
  Entity,
  Index,
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

  @Column()
  @Index()
  label!: string;

  @Column({ nullable: true })
  subjectId!: number | null;

  @Column({ nullable: true })
  objectId!: number | null;

  @ManyToOne(() => EntityOrm, { nullable: true })
  subject!: EntityOrm | null;

  @ManyToOne(() => EntityOrm, { nullable: true })
  object!: EntityOrm | null;

  @OneToMany(() => TripletOrm, (triplet) => triplet.predicateRelation)
  triplets!: TripletOrm[];
}
