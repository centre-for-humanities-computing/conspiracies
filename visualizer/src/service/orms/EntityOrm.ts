import {
  Column,
  Entity,
  Index,
  ManyToOne,
  OneToMany,
  PrimaryGeneratedColumn,
} from "typeorm";
import { TripletOrm } from "./TripletOrm";

@Entity("entities")
export class EntityOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column()
  @Index()
  label!: string;

  @Column({ nullable: true })
  supernodeId!: number | null;

  @ManyToOne(() => EntityOrm, (entity) => entity.subnodes)
  supernode!: EntityOrm;

  @OneToMany(() => EntityOrm, (entity) => entity.supernode)
  subnodes!: EntityOrm[];

  @OneToMany(() => TripletOrm, (triplet) => triplet.subjectEntity)
  subjectTriplets!: TripletOrm[];

  @OneToMany(() => TripletOrm, (triplet) => triplet.objectEntity)
  objectTriplets!: TripletOrm[];
}
