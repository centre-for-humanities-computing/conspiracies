import { DocInfo } from "./DocInfo";
import React from "react";
import { Stats } from "../graph/GraphServiceOld";
import { useServiceContext } from "../service/ServiceContextProvider";

export interface StatsInfoProps {
  label: string;
  stats: Stats;
}

export const StatsInfo: React.FC<StatsInfoProps> = ({ label, stats }) => {
  const { getDocService } = useServiceContext();

  return (
    <div>
      <p>Frequency: {stats.frequency}</p>
      {/*<p>Norm. frequency: {stats.norm_frequency?.toPrecision(3)}</p>*/}
      {stats.first_occurrence && <p>Earliest date: {stats.first_occurrence}</p>}
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
          {!getDocService() && (
            <ul>
              {stats.docs.map((d) => (
                <li key={d}>{d}</li>
              ))}
            </ul>
          )}

          {getDocService() && (
            <div>
              {getDocService()
                .getDocs(stats.docs)
                .map((d) => (
                  <DocInfo
                    key={d.id}
                    document={d}
                    highlightLabels={[label, ...(stats.alt_labels || [])]}
                  />
                ))}
            </div>
          )}
        </details>
      )}
    </div>
  );
};
