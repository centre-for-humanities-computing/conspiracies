import React from "react";
import { Info } from "./Info";
import { Node } from "@shared/types/graph";

export interface NodeInfoProps {
  node: Node;
  className?: string;
}

export const NodeInfo: React.FC<NodeInfoProps> = ({
  node,
  className,
}: NodeInfoProps) => {
  return (
    <div className={"panel node-info " + className}>
      <h2>{node.label}</h2>
      {node.supernode && <p>Supernode: {node.supernode.label}</p>}
      <Info id={node.id} type={"entity"} />

      {node.subnodes && node.subnodes.length > 0 && (
        <>
          <br />
          <details>
            <summary>Subnodes</summary>
            {node.subnodes.map((sn, i) => (
              <div key={sn.id}>
                <b>{sn.label}</b>
                <Info id={sn.id} type={"entity"} />
                {i + 1 < node.subnodes!.length && <hr />}
              </div>
            ))}
          </details>
        </>
      )}
    </div>
  );
};
