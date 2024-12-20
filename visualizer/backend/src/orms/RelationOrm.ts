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
import { getDataSource } from "../datasource";

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

  @Column("integer", { name: "term_frequency" })
  termFrequency!: number;

  @Column("integer", { name: "doc_frequency" })
  docFrequency!: number;

  async updateFrequencyCounts() {
    const dataSource = await getDataSource();
    const tripletRepository = dataSource.getRepository(TripletOrm);

    if (!this.triplets) {
      this.triplets = await tripletRepository.find({
        where: { relationId: this.id },
      });
    }

    // term frequency = total number of triplets involving this relation
    this.termFrequency = this.triplets.length;

    // document frequency = unique document IDs
    this.docFrequency = new Set(this.triplets.map((t) => t.docId)).size;

    // Commit the changes to the database
    const relationOrmRepository = dataSource.getRepository(RelationOrm);
    await relationOrmRepository.save(this);
  }
}
