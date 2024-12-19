import { EnrichedEdge, EnrichedNode, GraphData } from "@shared/types/graph";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

export interface GraphService {
  getDataBounds(): Promise<DataBounds>;

  getGraph(filter?: GraphFilter): Promise<GraphData>;

  getEnrichedNode(id: string | number): Promise<EnrichedNode>;

  getEnrichedEdge(id: string | number): Promise<EnrichedEdge>;
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

    return await response.json();
  }

  async getEnrichedNode(id: string | number): Promise<EnrichedNode> {
    const response = await fetch(`${this.baseUrl}/graph/node/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch enriched node: ${response.statusText}`);
    }

    return await response.json();
  }

  async getEnrichedEdge(id: string | number): Promise<EnrichedEdge> {
    const response = await fetch(`${this.baseUrl}/graph/edge/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch enriched edge: ${response.statusText}`);
    }

    return await response.json();
  }
}
