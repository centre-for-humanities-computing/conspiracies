import React from "react";
import { Info } from "./Info";
import { Edge } from "@shared/types/graph";

interface RelationInfoProps {
  id: string | number;
  label: string;
  subjectLabel: string;
  objectLabel: string;
}

const RelationInfo: React.FC<RelationInfoProps> = ({
  id,
  label,
  subjectLabel,
  objectLabel,
}) => {
  return (
    <div>
      <h2>
        <i>{subjectLabel}</i> <u>{label}</u> <i>{objectLabel}</i>
      </h2>
      <Info id={id} type={"relation"} />
    </div>
  );
};

export interface EdgeInfoProps {
  edge: Edge;
  className?: string;
}

export const EdgeInfo: React.FC<EdgeInfoProps> = ({
  edge,
  className,
}: EdgeInfoProps) => {
  return (
    <div className={"panel node-info " + className}>
      {edge.group.map((r, i) => (
        <div key={r.id}>
          <RelationInfo
            id={r.id}
            label={r.label}
            subjectLabel={edge.subjectLabel}
            objectLabel={edge.objectLabel}
          />
          {i + 1 < edge.group.length && (
            <>
              <br />
              <hr />
            </>
          )}
        </div>
      ))}
    </div>
  );
};
