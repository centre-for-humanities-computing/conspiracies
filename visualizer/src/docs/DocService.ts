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

export interface Doc {
  id: string;
  text: string;
  timestamp: string;
}

export class SampleDocService extends DocService {
  readonly docData: Map<string, Doc> = new Map(
    [
      {
        id: "1",
        text: "sample text 1",
        timestamp: "",
      },
      {
        id: "2",
        text: "sample text 1",
        timestamp: "",
      },
      {
        id: "3",
        text: "sample text 1",
        timestamp: "",
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
      docData.map((d) => [
        d.id,
        {
          id: d.id,
          text: d.text,
          timestamp: d.timestamp,
        },
      ]),
    );
  }
}
