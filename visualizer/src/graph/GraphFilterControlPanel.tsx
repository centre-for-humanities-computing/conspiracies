import React from "react";
import { GraphFilter } from "./GraphService";
import "./graph.css";

interface GraphFilterControlPanelProps {
  graphFilter: GraphFilter;
  setGraphFilter: React.Dispatch<React.SetStateAction<GraphFilter>>;
}

export const GraphFilterControlPanel = ({
  graphFilter,
  setGraphFilter,
}: GraphFilterControlPanelProps) => {
  return (
    <div className={"flex-container"}>
      <div className={"flex-container__element"}>
        <span className={"flex-container__element__sub-element"}>
          Minimum Node Frequency: {graphFilter.minimumNodeFrequency}
        </span>
        <button
          className={"flex-container__element__sub-element"}
          onClick={() =>
            setGraphFilter({
              ...graphFilter,
              minimumNodeFrequency: graphFilter.minimumNodeFrequency + 1,
            })
          }
        >
          +
        </button>
        <button
          className={"flex-container__element__sub-element"}
          onClick={() =>
            setGraphFilter({
              ...graphFilter,
              minimumNodeFrequency: graphFilter.minimumNodeFrequency - 1,
            })
          }
        >
          -
        </button>
      </div>
      <div className={"flex-container__element"}>
        Minimum Edge Frequency: {graphFilter.minimumEdgeFrequency}
        <button
          className={"flex-container__element__sub-element"}
          onClick={() =>
            setGraphFilter({
              ...graphFilter,
              minimumEdgeFrequency: graphFilter.minimumEdgeFrequency + 1,
            })
          }
        >
          +
        </button>
        <button
          className={"flex-container__element__sub-element"}
          onClick={() =>
            setGraphFilter({
              ...graphFilter,
              minimumEdgeFrequency: graphFilter.minimumEdgeFrequency - 1,
            })
          }
        >
          -
        </button>
      </div>
      <div className={"flex-container__element"}>
        Show unconnected nodes:
        <input
          type={"checkbox"}
          className={"flex-container__element__sub-element"}
          checked={graphFilter.showUnconnectedNodes}
          onChange={(event) =>
            setGraphFilter({
              ...graphFilter,
              showUnconnectedNodes: event.target.checked,
            })
          }
        />
      </div>
      <div className={"flex-container__element"}>
        From:{" "}
        <input
          className={"flex-container__element__sub-element"}
          type={"date"}
          onChange={(event) =>
            setGraphFilter({
              ...graphFilter,
              earliestDate: event.target.valueAsDate ?? undefined,
            })
          }
        />
        To:{" "}
        <input
          className={"flex-container__element__sub-element"}
          type={"date"}
          onChange={(event) =>
            setGraphFilter({
              ...graphFilter,
              latestDate: event.target.valueAsDate ?? undefined,
            })
          }
        />
      </div>
    </div>
  );
};
