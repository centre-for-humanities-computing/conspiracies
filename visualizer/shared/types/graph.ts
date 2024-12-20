export interface Identifiable {
  id: string | number;
  label: string;
}

export interface Node extends Identifiable {
  supernodeId?: number;
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
  docs?: string[] | number[];
  firstOccurrence?: Date;
  lastOccurrence?: Date;
  altLabels?: string[];
}
