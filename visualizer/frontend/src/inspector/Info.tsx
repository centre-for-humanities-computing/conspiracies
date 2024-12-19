import React, { useState } from "react";
import { useServiceContext } from "../service/ServiceContextProvider";
import { Enriched } from "@shared/types/graph";
import { Doc } from "@shared/types/doc";
import { DocInfo } from "./DocInfo";

export interface InfoProps {
  enrichment: Enriched;
  type: "entity" | "relation";
}

export const Info: React.FC<InfoProps> = ({ type, enrichment }) => {
  const { getDocService } = useServiceContext();

  const [docs, setDocs] = useState<Doc[] | null | undefined>(undefined);
  const loadDocs = () => {
    setDocs(null);
    getDocService()
      .getDocs(enrichment.docs!)
      .then((r) => {
        setDocs(r);
      });
  };

  const [visibleDocs, setVisibleDocs] = React.useState(20);

  const loadMore = () => setVisibleDocs((prev) => prev + 20);

  return (
    <div>
      <p>Frequency: {enrichment.frequency}</p>
      {/*<p>Norm. frequency: {stats.norm_frequency?.toPrecision(3)}</p>*/}
      {enrichment.firstOccurrence && (
        <p>Earliest date: {enrichment.firstOccurrence}</p>
      )}
      {enrichment.lastOccurrence && (
        <p>Latest date: {enrichment.lastOccurrence}</p>
      )}
      {enrichment.altLabels && (
        <div>
          Alternative Labels:
          <ul>
            {enrichment.altLabels.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </div>
      )}
      {enrichment.docs && (
        <div>
          {docs === undefined && <button onClick={loadDocs}>Load docs</button>}
          {docs === null && <p>Loading ...</p>}
          {docs && (
            <div>
              {docs &&
                docs
                  .slice(0, visibleDocs)
                  .map((d) => (
                    <DocInfo
                      key={d.id}
                      document={d}
                      subjectId={type === "entity" ? enrichment.id : undefined}
                      predicateId={
                        type === "relation" ? enrichment.id : undefined
                      }
                      objectId={type === "entity" ? enrichment.id : undefined}
                    />
                  ))}
              {visibleDocs < docs.length && (
                <button onClick={loadMore}>Load More</button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
