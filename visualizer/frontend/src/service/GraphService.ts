import { EnrichedGraphData, GraphFilter } from "../graph/GraphServiceOld";

export interface GraphService {
  getGraph(filter?: GraphFilter): Promise<EnrichedGraphData>;
}

export class HostedGraphService implements GraphService {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getGraph(filter?: GraphFilter): Promise<EnrichedGraphData> {
    const response = await fetch(`${this.baseUrl}/graph`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch graph: ${response.statusText}`);
    }

    return await response.json();
  }
}
