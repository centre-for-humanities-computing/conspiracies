import { Doc } from "@shared/types/doc";

export interface DocService {
  getDoc(id: string | number): Promise<Doc>;

  getDocs(ids: string[] | number[]): Promise<Doc[]>;
}

export class DocServiceImpl implements DocService {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getDoc(id: string | number): Promise<Doc> {
    const response = await fetch(`${this.baseUrl}/docs/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch doc: ${response.statusText}`);
    }

    return await response.json();
  }

  async getDocs(ids: string[] | number[]): Promise<Doc[]> {
    const response = await fetch(`${this.baseUrl}/docs/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ids: ids,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch doc: ${response.statusText}`);
    }

    return await response.json();
  }
}
