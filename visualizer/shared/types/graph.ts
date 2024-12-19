interface Identifiable {
  id: string | number;
  label: string;
}

export interface Node extends Identifiable {
  supernodeId?: number;
}

export interface Edge extends Identifiable {
  from: string | number;
  to: string | number;
}

export interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

export interface Enriched extends Identifiable {
  frequency: number;
  docs?: string[] | number[];
  firstOccurrence?: string;
  lastOccurrence?: string;
  altLabels?: string[];
}

export interface EnrichedNode extends Node, Enriched {}

export interface EnrichedEdge extends Edge, Enriched {
  subjectLabel: string;
  objectLabel: string;
}
