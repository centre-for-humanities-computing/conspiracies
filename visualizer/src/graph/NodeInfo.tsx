import { EnrichedNode } from "./GraphService";
import React from "react";

export interface NodeInfoProps {
  node: EnrichedNode;
  className?: string;
}

export const NodeInfo: React.FC<NodeInfoProps> = ({
  node,
  className,
}: NodeInfoProps) => {
  const stats = node.stats;
  return (
    <div className={"node-info " + className}>
      <b>{node.label}</b>
      <hr />
      <div>
        <p>Frequency: {stats.frequency}</p>
        {/*<p>Norm. frequency: {stats.norm_frequency?.toPrecision(3)}</p>*/}
        {stats.first_occurrence && (
          <p>Earliest date: {stats.first_occurrence}</p>
        )}
        {stats.last_occurrence && <p>Latest date: {stats.last_occurrence}</p>}
        {stats.alt_labels && (
          <div>
            Alternative Labels:
            <ul>
              {stats.alt_labels.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
          </div>
        )}
        {stats.docs && (
          <details>
            <summary>Documents</summary>
            <ul>
              {stats.docs.map((d) => (
                <li key={d}>{d}</li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
};
