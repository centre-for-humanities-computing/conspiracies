import React, { useEffect, useState } from "react";
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
      <i>{subjectLabel}</i>
      <b> {label} </b>
      <i>{objectLabel}</i>
      <Info id={id} type={"relation"} />
      <hr />
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
    <div className={"node-info " + className}>
      {edge.group.map((r) => (
        <RelationInfo
          key={r.id}
          id={r.id}
          label={r.label}
          subjectLabel={edge.subjectLabel}
          objectLabel={edge.objectLabel}
        />
      ))}
    </div>
  );
};
