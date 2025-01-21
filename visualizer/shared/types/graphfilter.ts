export interface DataBounds {
  minimumPossibleNodeFrequency: number;
  maximumPossibleNodeFrequency: number;
  minimumPossibleEdgeFrequency: number;
  maximumPossibleEdgeFrequency: number;
}

export interface GraphFilter {
  limitNodes: number;
  limitEdges: number;
  onlySupernodes?: boolean;
  minimumNodeFrequency?: number;
  maximumNodeFrequency?: number;
  minimumEdgeFrequency?: number;
  maximumEdgeFrequency?: number;
  labelSearch?: string;
  earliestDate?: Date;
  latestDate?: Date;
  whitelistedEntityIds?: string[];
  blacklistedEntityIds?: string[];
}
