import React from "react";
import "./graph.css";
import LogarithmicRangeSlider from "../common/LogarithmicRangeSlider";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";

interface GraphFilterControlPanelProps {
  dataBounds: DataBounds;
  graphFilter: GraphFilter;
  setGraphFilter: React.Dispatch<React.SetStateAction<GraphFilter>>;
}

export const GraphFilterControlPanel = ({
  dataBounds,
  graphFilter,
  setGraphFilter,
}: GraphFilterControlPanelProps) => {
  const setMinAndMaxNodeFrequency = (min: number, max: number) => {
    setGraphFilter({
      ...graphFilter,
      minimumNodeFrequency: min,
      maximumNodeFrequency: max,
    });
  };
  const setMinAndMaxEdgeFrequency = (min: number, max: number) => {
    setGraphFilter({
      ...graphFilter,
      minimumEdgeFrequency: min,
      maximumEdgeFrequency: max,
    });
  };

  return (
    <div className={"flex-container"}>
      <div className={"flex-container__element"}>
        <span className={"flex-container__element__sub-element"}>
          Node Frequency:
        </span>
      </div>
      <div style={{ width: "250px" }}>
        <LogarithmicRangeSlider
          onChange={(e) => {
            setMinAndMaxNodeFrequency(e.minValue, e.maxValue);
          }}
          min={dataBounds.minimumPossibleNodeFrequency}
          minValue={
            graphFilter.minimumNodeFrequency ||
            dataBounds.minimumPossibleNodeFrequency
          }
          maxValue={
            graphFilter.maximumNodeFrequency ||
            dataBounds.maximumPossibleNodeFrequency
          }
          max={dataBounds.maximumPossibleNodeFrequency}
          style={{ border: "none", boxShadow: "none", padding: "15px 10px" }}
        ></LogarithmicRangeSlider>
      </div>

      <div className={"flex-container__element"}>
        Edge Frequency:
        <div style={{ width: "250px" }}>
          <LogarithmicRangeSlider
            onChange={(e) => {
              setMinAndMaxEdgeFrequency(e.minValue, e.maxValue);
            }}
            min={dataBounds.minimumPossibleEdgeFrequency}
            minValue={
              graphFilter.minimumEdgeFrequency ||
              dataBounds.minimumPossibleEdgeFrequency
            }
            maxValue={
              graphFilter.maximumEdgeFrequency ||
              dataBounds.maximumPossibleEdgeFrequency
            }
            max={dataBounds.maximumPossibleEdgeFrequency}
            style={{ border: "none", boxShadow: "none", padding: "15px 10px" }}
          ></LogarithmicRangeSlider>
        </div>
      </div>
      {/*<div className={"flex-container__element"}>*/}
      {/*  Show unconnected nodes:*/}
      {/*  <input*/}
      {/*    type={"checkbox"}*/}
      {/*    className={"flex-container__element__sub-element"}*/}
      {/*    checked={graphFilter.showUnconnectedNodes}*/}
      {/*    onChange={(event) =>*/}
      {/*      setGraphFilter({*/}
      {/*        ...graphFilter,*/}
      {/*        showUnconnectedNodes: event.target.checked,*/}
      {/*      })*/}
      {/*    }*/}
      {/*  />*/}
      {/*</div>*/}
      <div className={"flex-container__element"}>
        Search nodes:
        <input
          type={"text"}
          onChange={(event) => {
            let value = event.target.value;
            setGraphFilter({
              ...graphFilter,
              labelSearch: value,
            });
          }}
        />
      </div>
      <div className={"flex-container__element"}>
        From:
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
        To:
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
