import { Details, GraphData } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

export interface GraphService {
  getDataBounds(): Promise<DataBounds>;

  getGraph(filter?: GraphFilter): Promise<GraphData>;

  getEntityDetails(id: string | number): Promise<Details>;

  getRelationDetails(ids: string | number): Promise<Details>;
}

export class GraphServiceImpl implements GraphService {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getDataBounds(): Promise<DataBounds> {
    const response = await fetch(`${this.baseUrl}/graph/bounds`);

    if (!response.ok) {
      throw new Error(`Failed to fetch data bounds: ${response.statusText}`);
    }

    return await response.json();
  }

  async getGraph(filter?: GraphFilter): Promise<GraphData> {
    const response = await fetch(`${this.baseUrl}/graph`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ graphFilter: filter }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch graph: ${response.statusText}`);
    }

    const r = await response.json();
    return r;
  }

  async getEntityDetails(id: string | number): Promise<Details> {
    const response = await fetch(`${this.baseUrl}/entities/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch entity details: ${response.statusText}`);
    }

    return await response.json();
  }

  async getRelationDetails(id: string | number): Promise<Details> {
    const response = await fetch(`${this.baseUrl}/relations/${id}`);

    if (!response.ok) {
      throw new Error(
        `Failed to fetch relation details: ${response.statusText}`,
      );
    }

    return await response.json();
  }
}
