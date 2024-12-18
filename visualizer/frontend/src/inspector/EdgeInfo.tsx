import { EdgeGroup } from "../graph/GraphServiceOld";
import React from "react";
import { StatsInfo } from "./StatsInfo";

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
          <StatsInfo label={e.label!} stats={e.stats} />
        </div>
      ))}
    </div>
  );
};
