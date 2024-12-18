export abstract class DocService {
  abstract getDocData(): Map<string, Doc>;

  getDoc(id: string): Doc | undefined {
    return this.getDocData().get(id);
  }

  getDocs(ids: string[]): Doc[] {
    return ids
      .map((id) => this.getDoc(id))
      .filter((v): v is Doc => v !== undefined);
  }
}

export interface TripletField {
  text: string;
  start_char: number;
  start: number;
  end_char: number;
  end: number;
}

export interface Triplet {
  subject: TripletField;
  predicate: TripletField;
  object: TripletField;
}

export interface Doc {
  id: string;
  text: string;
  timestamp: string;
  semantic_triplets: Triplet[];
}

export class SampleDocService extends DocService {
  readonly docData: Map<string, Doc> = new Map(
    [
      {
        id: "1",
        text: "sample text 1",
        timestamp: "",
        semantic_triplets: [],
      },
      {
        id: "2",
        text: "sample text 1",
        timestamp: "",
        semantic_triplets: [],
      },
      {
        id: "3",
        text: "sample text 1",
        timestamp: "",
        semantic_triplets: [],
      },
    ].map((d) => [d.id, d]),
  );

  getDocData(): Map<string, Doc> {
    return this.docData;
  }

  getDoc(id: string): Doc | undefined {
    return this.docData.get(id);
  }
}

export class FileDocService extends DocService {
  readonly docData: Map<string, Doc>;

  getDocData(): Map<string, Doc> {
    return this.docData;
  }

  constructor(docData: Doc[]) {
    super();
    this.docData = new Map(
      docData
        .filter((d) => d.semantic_triplets !== undefined)
        .map((d) => [
          d.id,
          {
            id: d.id,
            text: d.text,
            timestamp: d.timestamp,
            semantic_triplets: d.semantic_triplets,
          },
        ]),
    );
    console.log(this.docData.size);
  }
}
