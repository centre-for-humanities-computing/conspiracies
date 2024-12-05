import { EnrichedNode } from "../graph/GraphService";
import React from "react";
import { StatsInfo } from "./StatsInfo";

export interface NodeInfoProps {
  node: EnrichedNode;
  className?: string;
}

export const NodeInfo: React.FC<NodeInfoProps> = ({
  node,
  className,
}: NodeInfoProps) => {
  return (
    <div className={"node-info " + className}>
      <b>{node.label}</b>
      <hr />
      <StatsInfo stats={node.stats} />
    </div>
  );
};
