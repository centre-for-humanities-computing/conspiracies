import {
  Column,
  Entity,
  Index,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryGeneratedColumn,
} from "typeorm";
import { TripletOrm } from "./TripletOrm";
import { getDataSource } from "../datasource";

@Entity("entities")
export class EntityOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column("text")
  @Index()
  label!: string;

  @Column("integer", { name: "supernode_id", nullable: true })
  supernodeId!: number | null;

  @ManyToOne(() => EntityOrm, (entity) => entity.subnodes)
  @JoinColumn({ name: "supernode_id" })
  supernode!: EntityOrm;

  @OneToMany(() => EntityOrm, (entity) => entity.supernode)
  subnodes!: EntityOrm[];

  @OneToMany(() => TripletOrm, (triplet) => triplet.subjectEntity)
  subjectTriplets!: TripletOrm[];

  @OneToMany(() => TripletOrm, (triplet) => triplet.objectEntity)
  objectTriplets!: TripletOrm[];

  async getDocumentIds(): Promise<number[]> {
    const dataSource = await getDataSource();

    const documentIds = await dataSource
      .createQueryBuilder()
      .select("triplet.docId", "docId")
      .where("triplet.subjectId = :entityId", { entityId: this.id })
      .orWhere("triplet.objectId = :entityId", { entityId: this.id })
      .distinct(true) // Ensure unique document IDs
      .getRawMany();

    return documentIds.map((record) => record.docId);
  }
}
