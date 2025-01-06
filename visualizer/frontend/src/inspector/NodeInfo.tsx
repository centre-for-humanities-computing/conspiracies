import React, { useEffect, useState } from "react";
import { Info } from "./Info";
import { Details, Node } from "@shared/types/graph";
import { useServiceContext } from "../service/ServiceContextProvider";

export interface NodeInfoProps {
  node: Node;
  className?: string;
}

export const NodeInfo: React.FC<NodeInfoProps> = ({
  node,
  className,
}: NodeInfoProps) => {
  const { graphService } = useServiceContext();

  const [details, setDetails] = useState<Details | undefined>(undefined);

  useEffect(() => {
    setDetails(undefined);
    graphService.getEntityDetails(node.id).then(setDetails);
  }, [graphService, node.id]);

  return (
    <div className={"node-info " + className}>
      <b>{node.label}</b>
      <hr />
      {!details && <p>Loading ...</p>}
      {details && <Info details={details} type={"entity"} />}
    </div>
  );
};
