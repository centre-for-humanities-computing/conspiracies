import React, { useEffect, useState } from "react";
import { Info } from "./Info";
import { Details, Edge } from "@shared/types/graph";
import { useServiceContext } from "../service/ServiceContextProvider";

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
  const { getGraphService } = useServiceContext();

  const [edgeDetails, setEdgeDetails] = useState<Details>();

  useEffect(() => {
    getGraphService().getRelationDetails(id).then(setEdgeDetails);
  }, [getGraphService, id]);

  return (
    <div>
      <i>{subjectLabel}</i>
      <b> {label} </b>
      <i>{objectLabel}</i>
      {!edgeDetails && <p>Loading ...</p>}
      {edgeDetails && <Info details={edgeDetails} type={"relation"} />}
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
