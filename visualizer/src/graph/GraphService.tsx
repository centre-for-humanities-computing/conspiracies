import {GraphData, Node, Edge} from "react-vis-graph-wrapper";

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

export class GraphFilter {
    minimumNodeFrequency: number;
    minimumEdgeFrequency: number;
    showUnconnectedNodes: boolean = true;

    constructor(minimumNodeFrequency: number = 1, minimumEdgeFrequency: number = 1) {
        this.minimumNodeFrequency = minimumNodeFrequency;
        this.minimumEdgeFrequency = minimumEdgeFrequency;
    }


}

export function filter(filter: GraphFilter, graphData: EnrichedGraphData): EnrichedGraphData {
    let nodes = graphData.nodes.filter((node: EnrichedNode) =>
        node.stats.frequency >= filter.minimumNodeFrequency
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
