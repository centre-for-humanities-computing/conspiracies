import {Edge, GraphData, Node} from "react-vis-graph-wrapper";

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

export interface EnrichedGraphData extends GraphData {
    nodes: EnrichedNode[];
    edges: EnrichedEdge[];
}

export class GraphFilter {
    minimumNodeFrequency: number;
    minimumEdgeFrequency: number;
    earliestDate?: Date;
    latestDate?: Date;
    showUnconnectedNodes: boolean = false;

    constructor(minimumNodeFrequency: number = 1, minimumEdgeFrequency: number = 1) {
        this.minimumNodeFrequency = minimumNodeFrequency;
        this.minimumEdgeFrequency = minimumEdgeFrequency;
    }
}

function hasDateOverlap(node: EnrichedNode, filter: GraphFilter): boolean {
    if (!node.stats.first_occurrence || !node.stats.last_occurrence) {
        return true;
    }
    const first = new Date(node.stats.first_occurrence);
    const last = new Date(node.stats.last_occurrence);
    const afterEarliestDate = !filter.earliestDate
        || filter.earliestDate < first
        || filter.earliestDate < last;

    const beforeLatestDate = !filter.latestDate
        || filter.latestDate > first || filter.latestDate > last;

    return afterEarliestDate && beforeLatestDate;
}


export function filter(filter: GraphFilter, graphData: EnrichedGraphData): EnrichedGraphData {
    let nodes = graphData.nodes.filter((node: EnrichedNode) =>
        node.stats.frequency >= filter.minimumNodeFrequency
        && hasDateOverlap(node, filter)
    );
    let filteredNodes = new Set(nodes.map(node => node.id));
    let edges = graphData.edges.filter((edge: EnrichedEdge) =>
        edge.stats.frequency >= filter.minimumEdgeFrequency &&
        filteredNodes.has(edge.from) && filteredNodes.has(edge.to)
    );
    let connectedNodes = new Set(edges.flatMap(edge => [edge.from, edge.to]));
    if (!filter.showUnconnectedNodes) {
        nodes = nodes.filter(node => connectedNodes.has(node.id));
    }
    return {nodes, edges}
}

export abstract class GraphService {
    private nodesMap: Map<string, EnrichedNode> | null = null;

    abstract getGraph(): EnrichedGraphData;

    getSubGraph(nodeIds: Set<string>): EnrichedGraphData {
        return {
            nodes: this.getGraph().nodes.filter((n: EnrichedNode) => nodeIds.has(n.id!.toString())),
            edges: this.getGraph().edges
        }
    }

    getConnectedNodes(nodeId: string): Set<string> {
        return new Set(this.getGraph().edges.filter(edge => edge.from === nodeId || edge.to === nodeId)
            .flatMap(edge => [edge.from!.toString(), edge.to!.toString()]))
    }

    getNode(nodeId: string): EnrichedNode | undefined {
        if (this.nodesMap === null) {
            this.nodesMap = new Map(
                this.getGraph().nodes.map(node => [node.id!.toString(), node])
            )
        }

        // highly inefficient linear search; overwrite for actual use
        for (let node of this.getGraph().nodes) {
            if (node.id === nodeId) {
                return node;
            }
        }
        return undefined;
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
    private readonly data: EnrichedGraphData = {nodes: [], edges: []};

    constructor(data: EnrichedGraphData) {
        super();
        this.data = data;
    }

    getGraph(): EnrichedGraphData {
        return this.data;
    }

}
