export interface Identifiable {
  id: string | number;
  label: string;
}

export interface Node extends Identifiable {
  supernode?: Identifiable;
  subnodes?: Identifiable[];
  focus?: boolean;
}

export interface LabeledEdge extends Identifiable {
  subjectLabel: string;
  objectLabel: string;
}

export interface Edge extends Identifiable {
  from: number;
  to: number;
  subjectLabel: string;
  objectLabel: string;
  totalTermFrequency?: number;
  group: LabeledEdge[];
}

export interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

export interface Details extends Identifiable {
  frequency: number;
  docFrequency: number;
  docs?: string[] | number[];
  firstOccurrence?: Date | null;
  lastOccurrence?: Date | null;
  altLabels?: string[];
}
