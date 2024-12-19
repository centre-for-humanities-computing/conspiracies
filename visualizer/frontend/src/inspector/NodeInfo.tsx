import React, { useEffect, useState } from "react";
import { Info } from "./Info";
import { EnrichedNode, Node } from "@shared/types/graph";
import { useServiceContext } from "../service/ServiceContextProvider";

export interface NodeInfoProps {
  node: Node;
  className?: string;
}

export const NodeInfo: React.FC<NodeInfoProps> = ({
  node,
  className,
}: NodeInfoProps) => {
  const { getGraphService } = useServiceContext();

  const [nodeEnrichment, setNodeEnrichment] = useState<
    EnrichedNode | undefined
  >(undefined);

  useEffect(() => {
    setNodeEnrichment(undefined);
    getGraphService().getEnrichedNode(node.id).then(setNodeEnrichment);
  }, [getGraphService, node.id]);

  return (
    <div className={"node-info " + className}>
      <b>{node.label}</b>
      <hr />
      {!nodeEnrichment && <p>Loading ...</p>}
      {nodeEnrichment && <Info enrichment={nodeEnrichment} type={"entity"} />}
    </div>
  );
};
