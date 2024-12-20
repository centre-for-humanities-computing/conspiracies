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

  @Column("integer", { name: "term_frequency" })
  termFrequency!: number;

  @Column("integer", { name: "doc_frequency" })
  docFrequency!: number | null;

  async updateFrequencyCounts() {
    const dataSource = await getDataSource();
    const tripletRepository = dataSource.getRepository(TripletOrm);

    if (!this.subjectTriplets || !this.objectTriplets) {
      const [subjectTriplets, objectTriplets] = await Promise.all([
        tripletRepository.find({ where: { subjectId: this.id } }),
        tripletRepository.find({ where: { objectId: this.id } }),
      ]);

      this.subjectTriplets = subjectTriplets;
      this.objectTriplets = objectTriplets;
    }

    // term frequency = total number of triplets involving this entity
    this.termFrequency =
      this.subjectTriplets.length + this.objectTriplets.length;

    // document frequency = unique document IDs
    this.docFrequency = new Set(
      [...this.subjectTriplets, ...this.objectTriplets].map((t) => t.docId),
    ).size;

    // Commit the changes to the database
    const entityRepository = dataSource.getRepository(EntityOrm);
    await entityRepository.save(this);
  }

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
