import React, { useEffect, useState } from "react";
import { useServiceContext } from "../service/ServiceContextProvider";
import { Details } from "@shared/types/graph";
import { Doc } from "@shared/types/doc";
import { DocInfo } from "./DocInfo";

export interface InfoProps {
  id: string | number;
  type: "entity" | "relation";
}

export const Info: React.FC<InfoProps> = ({ type, id }) => {
  const { entityService, relationService } = useServiceContext();

  const [details, setDetails] = useState<Details>();

  useEffect(() => {
    setDetails(undefined);
    (type === "entity" ? entityService : relationService)
      .getDetails(id)
      .then(setDetails);
  }, [entityService, relationService, id, type]);

  const [visibleDocs, setVisibleDocs] = React.useState(50);

  const [docs, setDocs] = useState<Doc[] | null | undefined>(undefined);
  const loadDocs = () => {
    setDocs(null);
    (type === "entity" ? entityService : relationService)
      .getDocs(id)
      .then((r) => {
        setDocs(r);
      });
  };

  const loadMore = () => {
    setVisibleDocs((prev) => prev + 50);
  };

  if (details === undefined) {
    return <div>Loading ...</div>;
  }

  return (
    <div>
      <p>Frequency: {details.frequency}</p>
      {details.firstOccurrence && (
        <p>Earliest date: {details.firstOccurrence.toString()}</p>
      )}
      {details.lastOccurrence && (
        <p>Latest date: {details.lastOccurrence.toString()}</p>
      )}
      {details.altLabels && details.altLabels.length > 0 && (
        <div>
          Alternative Labels:
          <ul>
            {details.altLabels.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </div>
      )}
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
                    subjectId={type === "entity" ? details.id : undefined}
                    predicateId={type === "relation" ? details.id : undefined}
                    objectId={type === "entity" ? details.id : undefined}
                  />
                ))}
            {visibleDocs < docs.length && (
              <button onClick={loadMore}>Load More</button>
            )}{" "}
          </div>
        )}
      </div>
    </div>
  );
};
