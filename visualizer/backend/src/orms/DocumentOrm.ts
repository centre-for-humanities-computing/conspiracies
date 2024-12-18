import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from "typeorm";
import { TripletOrm } from "./TripletOrm";

@Entity("docs")
export class DocumentOrm {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column("text")
  text!: string;

  @Column("text", { nullable: true })
  origText!: string | null;

  @Column("datetime", { nullable: true })
  timestamp!: Date | null;

  @OneToMany(() => TripletOrm, (triplet) => triplet.document)
  triplets!: TripletOrm[];
}
