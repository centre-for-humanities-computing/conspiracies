import { GraphData, Node, Edge, IdType } from "react-vis-graph-wrapper";

export interface Stats {
  frequency: number;
}

export interface EnrichedNode extends Node {
  stats: Stats;
}

export interface EnrichedEdge extends Edge {
  stats: Stats;
}

export interface EnrichedGraphData extends GraphData {
  nodes: EnrichedNode[];
  edges: EnrichedEdge[];
}

export const sampleGraphData: EnrichedGraphData = {
  nodes: [
    {
      id: "1",
      label: "node 1",
      stats: {
        frequency: 3,
      },
    },
    {
      id: "2",
      label: "node 2",
      stats: {
        frequency: 2,
      },
    },
    {
      id: "3",
      label: "node 3",
      stats: {
        frequency: 2,
      },
    },
    {
      id: "4",
      label: "node 4",
      stats: {
        frequency: 1,
      },
    },
  ],
  edges: [
    {
      from: "1",
      to: "2",
      stats: {
        frequency: 2,
      },
    },
    {
      from: "1",
      to: "3",
      stats: {
        frequency: 2,
      },
    },
    {
      from: "1",
      to: "4",
      stats: {
        frequency: 1,
      },
    },
    {
      from: "2",
      to: "3",
      stats: {
        frequency: 2,
      },
    },
  ],
};

export class GraphFilter {
  private filters: Map<string, (node: EnrichedNode) => boolean> = new Map();

  constructor() {}

  addFilter(name: string, filter: (node: EnrichedNode) => boolean) {
    this.filters.set(name, filter);
  }
  removeFilter(name: string) {
    this.filters.delete(name);
  }
  filter(graphData: EnrichedGraphData): EnrichedGraphData {
    let filters: ((node: EnrichedNode) => boolean)[] = Array.from(
      this.filters.values()
    );
    if (filters.length === 0) {
      return graphData;
    } else {
      return {
        nodes: graphData.nodes.filter((node: EnrichedNode) =>
          filters.some((f) => f(node))
        ),
        edges: graphData.edges,
      };
    }
  }
}

export interface GraphService {
  getGraph(): EnrichedGraphData;
  getSubGraph(nodeIds: Set<string>): EnrichedGraphData;
  getConnectedNodes(nodeId: string): Set<string>
}

export class SampleGraphService implements GraphService {
  getGraph(): EnrichedGraphData {
    return sampleGraphData;
  }
  getSubGraph(nodeIds: Set<string>): EnrichedGraphData {
    throw new Error("Method not implemented.");
  }
  getConnectedNodes(nodeId: string): Set<string> {
    throw new Error("Method not implemented.");
  }
}

export class FileGraphService implements GraphService {
  private data: EnrichedGraphData = { nodes: [], edges: [] };

  constructor(data: EnrichedGraphData) {
    this.data = data;
  }

  getGraph(): EnrichedGraphData {
    return this.data;
  }

  getSubGraph(nodeIds: Set<string>): EnrichedGraphData {
    return {
      nodes: this.data.nodes.filter((n: EnrichedNode) => nodeIds.has(n.id!.toString())),
      edges: this.data.edges
    }
  }

  getConnectedNodes(nodeId: string): Set<string> {
    return new Set(this.data.edges.filter(edge => edge.from === nodeId || edge.to === nodeId).flatMap(
      edge => [edge.from!.toString(), edge.to!.toString()]
    ))
  }
}
