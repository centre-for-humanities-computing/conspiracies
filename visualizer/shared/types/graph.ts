export interface Identifiable {
  id: string | number;
  label: string;
}

export interface Node extends Identifiable {
  supernode?: Identifiable;
  subnodes?: Identifiable[];
  focus?: boolean;
}

export interface Edge extends Identifiable {
  from: string | number;
  to: string | number;
  subjectLabel: string;
  objectLabel: string;
  width?: number;
  group: Identifiable[];
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
