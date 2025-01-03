export interface TripletField {
  id: string | number;
  start: number;
  end: number;
}

export interface Triplet {
  subject: TripletField;
  predicate: TripletField;
  object: TripletField;
}
export interface Doc {
  id: string | number;
  text: string;
  timestamp?: Date;
  triplets: Triplet[];
}
