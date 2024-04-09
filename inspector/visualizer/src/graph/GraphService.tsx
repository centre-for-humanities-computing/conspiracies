import { GraphData } from "react-graph-vis";
import { TypePredicateBase } from "typescript";
import vis, { IdType, Node, Edge } from "vis";

export const sampleGraphData: GraphData = {
  nodes: [
    {
      id: "1",
      label: "node 1",
    },
    {
      id: "2",
      label: "node 2",
    },
    {
      id: "3",
      label: "node 3",
    },
    {
      id: "4",
      label: "node 4",
    },
  ],
  edges: [
    {
      from: "1",
      to: "2",
    },
    {
      from: "1",
      to: "3",
    },
    {
      from: "1",
      to: "4",
    },
    {
      from: "2",
      to: "3",
    },
  ],
};

class GraphFilter {
  private filters: Map<string, (id: IdType | undefined) => boolean> = new Map();

  constructor() {}

  addFilter(name: string, filter: (id: IdType | undefined) => boolean) {
    this.filters.set(name, filter);
  }
  removeFilter(name: string) {
    this.filters.delete(name);
  }
  filter(graphData: GraphData): GraphData {
    let filters: Function[] = Array.from(this.filters.values());
    if (filters.length === 0) {
      return graphData;
    } else {
      return {
        nodes: graphData.nodes.filter((node: Node) =>
          filters.some((f) => !f(node.id))
        ),
        edges: graphData.edges.filter((edge: Edge) =>
          filters.some((f) => !f(edge.from) && !f(edge.to))
        ),
      };
    }
  }
}

export interface GraphService {
  getGraph(): GraphData;
  getSubGraph(nodeIds: string[]): GraphData;
}

export class SampleGraphService implements GraphService {
  getGraph(): GraphData {
    return sampleGraphData;
  }
  getSubGraph(nodeIds: string[]): GraphData {
    throw new Error("Method not implemented.");
  }
}

export class FileGraphService implements GraphService {
  data: any = { nodes: [], edges: [] };

  constructor(filename: string) {
    // TODO: probably does not work, but this is the idea
    this.data = fetch(filename).then((result) => {
      this.data = result.json();
    });
  }
  getGraph(): GraphData {
    let nodes: Node[] = this.data.nodes.map((n: { label: string }) => ({
      id: n.label,
      label: n.label.slice(0, 50),
    }));
    let edges: Edge[] = this.data.edges.map(
      (e: { from: string; to: string }) => ({ ...e })
    );
    return {
      nodes: nodes,
      edges: edges,
    };
  }
  getSubGraph(nodeIds: string[]): GraphData {
    throw new Error("Method not implemented.");
  }
}
