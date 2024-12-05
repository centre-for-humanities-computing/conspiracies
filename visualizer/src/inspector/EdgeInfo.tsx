import { EdgeGroup } from "../graph/GraphService";
import React from "react";

export interface EdgeInfoProps {
  edges: EdgeGroup;
  className?: string;
}

export const EdgeInfo: React.FC<EdgeInfoProps> = ({ edges }: EdgeInfoProps) => {
  return (
    <div className={"node-info"}>
      {edges.group!.map((e, i) => (
        <div key={e.label}>
          <b>{e.label}</b>
          <div>
            <p>Frequency: {e.stats.frequency}</p>
            {/*<p>Norm. frequency: {e.stats.norm_frequency?.toPrecision(3)}</p>*/}
            {e.stats.first_occurrence && (
              <p>Earliest date: {e.stats.first_occurrence}</p>
            )}
            {e.stats.last_occurrence && (
              <p>Latest date: {e.stats.last_occurrence}</p>
            )}
            {e.stats.alt_labels && (
              <div>
                Alternative Labels:
                <ul>
                  {e.stats.alt_labels.map((l) => (
                    <li key={l}>{l}</li>
                  ))}
                </ul>
              </div>
            )}
            {e.stats.docs && (
              <details>
                <summary>Documents</summary>
                <ul>
                  {e.stats.docs.map((d) => (
                    <li key={d}>{d}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
          {i < edges.group!.length - 1 && <hr />}
        </div>
      ))}
    </div>
  );
};
