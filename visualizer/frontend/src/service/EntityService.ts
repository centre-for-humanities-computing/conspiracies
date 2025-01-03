import { Doc } from "@shared/types/doc";
import { Details } from "@shared/types/graph";

export interface EntityService {
  getDetails(id: string | number): Promise<Details>;

  getDocs(id: string | number, limit?: number): Promise<Doc[]>;
}

export class EntityServiceImpl implements EntityService {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getDetails(id: string | number): Promise<Details> {
    const response = await fetch(`${this.baseUrl}/entities/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch entity: ${response.statusText}`);
    }

    return await response.json();
  }

  async getDocs(id: string | number, limit?: number): Promise<Doc[]> {
    const response = await fetch(
      `${this.baseUrl}/entities/${id}/docs${limit ? "?limit=" + limit : ""}`,
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch doc: ${response.statusText}`);
    }

    return await response.json();
  }
}
