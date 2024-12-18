import { Edge, GraphData, Node } from "react-vis-graph-wrapper";

export interface Stats {
  frequency: number;
  norm_frequency?: number;
  docs?: string[];
  first_occurrence?: string;
  last_occurrence?: string;
  alt_labels?: string[];
}

export interface EnrichedNode extends Node {
  stats: Stats;
}

export interface EnrichedEdge extends Edge {
  stats: Stats;
}

export interface EdgeGroup extends EnrichedEdge {
  group?: EnrichedEdge[];
}

export interface EnrichedGraphData extends GraphData {
  nodes: EnrichedNode[];
  edges: EdgeGroup[];
}

export class GraphFilter {
  minimumPossibleNodeFrequency: number;
  minimumNodeFrequency: number;
  maximumNodeFrequency: number;
  maximumPossibleNodeFrequency: number;
  minimumPossibleEdgeFrequency: number;
  minimumEdgeFrequency: number;
  maximumEdgeFrequency: number;
  maximumPossibleEdgeFrequency: number;
  labelSearch: string = "";
  earliestDate?: Date;
  latestDate?: Date;
  showUnconnectedNodes: boolean = false;

  constructor(
    minimumPossibleNodeFrequency: number,
    minimumNodeFrequency: number,
    maximumPossibleNodeFrequency: number,
    minimumPossibleEdgeFrequency: number,
    minimumEdgeFrequency: number,
    maximumPossibleEdgeFrequency: number,
  ) {
    this.minimumPossibleNodeFrequency = minimumPossibleNodeFrequency;
    this.minimumNodeFrequency = minimumNodeFrequency;
    this.maximumNodeFrequency = maximumPossibleNodeFrequency;
    this.maximumPossibleNodeFrequency = maximumPossibleNodeFrequency;
    this.minimumPossibleEdgeFrequency = minimumPossibleEdgeFrequency;
    this.minimumEdgeFrequency = minimumEdgeFrequency;
    this.maximumEdgeFrequency = maximumPossibleEdgeFrequency;
    this.maximumPossibleEdgeFrequency = maximumPossibleEdgeFrequency;
  }
}

function hasDateOverlap(
  nodeOrEdge: EnrichedNode | EnrichedEdge,
  filter: GraphFilter,
): boolean {
  if (!nodeOrEdge.stats.first_occurrence || !nodeOrEdge.stats.last_occurrence) {
    return true;
  }
  const first = new Date(nodeOrEdge.stats.first_occurrence);
  const last = new Date(nodeOrEdge.stats.last_occurrence);
  const afterEarliestDate =
    !filter.earliestDate ||
    filter.earliestDate < first ||
    filter.earliestDate < last;

  const beforeLatestDate =
    !filter.latestDate || filter.latestDate > first || filter.latestDate > last;

  return afterEarliestDate && beforeLatestDate;
}

export function filter(
  filter: GraphFilter,
  graphData: EnrichedGraphData,
): EnrichedGraphData {
  let nodes = graphData.nodes.filter(
    (node: EnrichedNode) =>
      node.stats.frequency >= filter.minimumNodeFrequency &&
      node.stats.frequency < filter.maximumNodeFrequency &&
      hasDateOverlap(node, filter),
  );
  let filteredNodes = new Set(nodes.map((node) => node.id));
  let groupedEdges = graphData.edges
    .filter(
      (edge: EnrichedEdge) =>
        edge.stats.frequency >= filter.minimumEdgeFrequency &&
        edge.stats.frequency < filter.maximumEdgeFrequency &&
        hasDateOverlap(edge, filter) &&
        filteredNodes.has(edge.from) &&
        filteredNodes.has(edge.to),
    )
    .reduce(
      (acc, curr) => {
        const key = curr.from + "->" + curr.to;
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(curr);
        return acc;
      },
      {} as Record<string, EnrichedEdge[]>,
    );
  let edges = Object.values(groupedEdges).map((group) => {
    group.sort((edge1, edge2) => edge2.stats.frequency - edge1.stats.frequency);
    const representative: EnrichedEdge = group.at(0)!;
    return {
      ...representative,
      id: representative.from + "->" + representative.to,
      label: group
        .slice(0, 3)
        .map((e) => e.label)
        .join(", "),
      width: Math.log(
        group.map((e) => e.stats.frequency).reduce((a, b) => a + b),
      ),
      group: group,
    };
  });

  let connectedNodes = new Set(edges.flatMap((edge) => [edge.from, edge.to]));
  if (!filter.showUnconnectedNodes) {
    nodes = nodes.filter((node) => connectedNodes.has(node.id));
  }
  nodes = nodes.map((node) => ({
    ...node,
    opacity: node.label?.toLowerCase().includes(filter.labelSearch) ? 1 : 0.2,
    font: {
      size: 14 + node.stats.frequency / 100,
    },
  }));

  return { nodes, edges };
}

export interface DataBounds {
  minNodeFrequency: number;
  maxNodeFrequency: number;
  maxEdgeFrequency: number;
}

export abstract class GraphService {
  abstract getGraph(): EnrichedGraphData;

  getBounds(): DataBounds {
    return {
      minNodeFrequency: Math.min(
        ...this.getGraph().nodes.map((n) => n.stats.frequency),
      ),
      maxNodeFrequency: Math.max(
        ...this.getGraph().nodes.map((n) => n.stats.frequency),
      ),
      maxEdgeFrequency: Math.max(
        ...this.getGraph().edges.map((n) => n.stats.frequency),
      ),
    };
  }

  getSubGraph(nodeIds: Set<string>): EnrichedGraphData {
    return {
      nodes: this.getGraph().nodes.filter((n: EnrichedNode) =>
        nodeIds.has(n.id!.toString()),
      ),
      edges: this.getGraph().edges,
    };
  }

  getConnectedNodes(nodeId: string): Set<string> {
    return new Set(
      this.getGraph()
        .edges.filter((edge) => edge.from === nodeId || edge.to === nodeId)
        .flatMap((edge) => [edge.from!.toString(), edge.to!.toString()]),
    );
  }
}

export class SampleGraphService extends GraphService {
  readonly sampleGraphData: EnrichedGraphData = {
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

  getGraph(): EnrichedGraphData {
    return this.sampleGraphData;
  }
}

export class FileGraphService extends GraphService {
  private readonly data: EnrichedGraphData = { nodes: [], edges: [] };

  constructor(data: EnrichedGraphData) {
    super();
    this.data = data;
  }

  getGraph(): EnrichedGraphData {
    return this.data;
  }
}
//
// export class DbGraphService extends GraphService {
//   private db: DataSource;
//
//   constructor(path: string) {
//     super();
//     this.db = new DataSource({
//       type: "sqlite",
//       api: path,
//       entities: [EntityOrm, RelationOrm, TripletOrm, DocumentOrm],
//       synchronize: true,
//     });
//
//     this.db.initialize();
//     this.initializeGraphData();
//   }
//
//   private entityData: EntityOrm[] = [];
//   private relationData: RelationOrm[] = [];
//
//   // Preload the data during initialization
//   async initializeGraphData(): Promise<void> {
//     this.entityData = await this.db.getRepository(EntityOrm).find();
//     this.relationData = await this.db.getRepository(RelationOrm).find();
//   }
//
//
//   getGraph(): EnrichedGraphData {
//     const nodes = this.entityData.map((entity) => ({
//       id: entity.id,
//       label: entity.label,
//     }));
//
//     const edges = this.relationData.map((relation) => ({
//       id: relation.id,
//       source: relation.subjectId,
//       target: relation.objectId,
//       label: relation.label,
//     }));
//
//     return {
//       nodes: [],
//       edges: [],
//     };
//   }
// }
