import React, { useEffect, useState } from "react";
import { Info } from "./Info";
import { Edge, EnrichedEdge } from "@shared/types/graph";
import { useServiceContext } from "../service/ServiceContextProvider";

export interface EdgeInfoProps {
  edge: Edge;
  className?: string;
}

export const EdgeInfo: React.FC<EdgeInfoProps> = ({
  edge,
  className,
}: EdgeInfoProps) => {
  const { getGraphService } = useServiceContext();

  const [edgeEnrichment, setEdgeEnrichment] = useState<
    EnrichedEdge | undefined
  >(undefined);

  useEffect(() => {
    setEdgeEnrichment(undefined);
    getGraphService().getEnrichedEdge(edge.id).then(setEdgeEnrichment);
  }, [getGraphService, edge.id]);

  return (
    <div className={"node-info " + className}>
      {edgeEnrichment && <i>{edgeEnrichment.subjectLabel}</i>}
      <b> {edge.label} </b>
      {edgeEnrichment && <i>{edgeEnrichment.objectLabel}</i>}
      <hr />
      {!edgeEnrichment && <p>Loading ...</p>}
      {edgeEnrichment && <Info enrichment={edgeEnrichment} type={"relation"} />}
    </div>
  );
};
