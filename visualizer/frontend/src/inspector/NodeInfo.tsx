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

  const [details, setDetails] = useState<Details>();

  useEffect(() => {
    setDetails(undefined);
    graphService.getEntityDetails(node.id).then(setDetails);
  }, [graphService, node.id]);

  return (
    <div className={"node-info " + className}>
      <b>{node.label}</b>
      {node.supernode && <i> [{node.supernode.label}]</i>}
      <hr />
      {!details && <p>Loading ...</p>}
      {details && <Info id={node.id} type={"entity"} />}

      {node.subnodes && node.subnodes.length > 0 && (
        <details>
          <summary>Subnodes</summary>
          {node.subnodes.map((sn) => (
            <div key={sn.id}>
              <b>{sn.label}</b>
              <Info id={sn.id} type={"entity"} />
              <hr />
            </div>
          ))}
        </details>
      )}
    </div>
  );
};
