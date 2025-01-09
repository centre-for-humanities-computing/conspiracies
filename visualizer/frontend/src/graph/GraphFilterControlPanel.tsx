import React, { useEffect, useState } from "react";
import "./graph.css";
import LogarithmicRangeSlider from "../common/LogarithmicRangeSlider";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";
import { useServiceContext } from "../service/ServiceContextProvider";

interface GraphFilterControlPanelProps {
  graphFilter: GraphFilter;
  setGraphFilter: React.Dispatch<React.SetStateAction<GraphFilter>>;
}

export const GraphFilterControlPanel = ({
  graphFilter,
  setGraphFilter,
}: GraphFilterControlPanelProps) => {
  const { graphService } = useServiceContext();

  const [dataBounds, setDataBounds] = useState<DataBounds>();
  useEffect(() => {
    graphService.getDataBounds().then((r) => setDataBounds(r));
  }, [graphService]);

  const [limit, setLimit] = useState<number>(graphFilter.limit);
  const [search, setSearch] = useState<string | undefined>(
    graphFilter.labelSearch,
  );

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

  if (!dataBounds) {
    return <div className={"flex-container"}>Loading ...</div>;
  }

  return (
    <div className={"flex-container"}>
      <div className={"flex-container__element"}>
        <span className={"flex-container__element__sub-element"}>
          Limit nodes:&nbsp;
        </span>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setGraphFilter((prevState) => ({
              ...prevState,
              limit: limit,
            }));
          }}
        >
          <input
            min={1}
            max={999}
            type={"number"}
            value={limit}
            onChange={(event) => {
              setLimit(Number(event.target.value));
            }}
          />
          <input type={"submit"} />
        </form>
      </div>
      <div className={"flex-container__element"}>
        Only supernodes:
        <input
          type={"checkbox"}
          checked={graphFilter.onlySupernodes || false}
          onChange={(event) =>
            setGraphFilter((prevState) => ({
              ...prevState,
              onlySupernodes: event.target.checked,
            }))
          }
        />
      </div>
      <div className={"flex-container__element"}>
        <span className={"flex-container__element__sub-element"}>
          Node Frequency:&nbsp;
        </span>
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
      </div>
      <div className={"flex-container__element"}>
        <span className={"flex-container__element__sub-element"}>
          Edge Frequency:&nbsp;
        </span>
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
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setGraphFilter((prevState) => ({
              ...prevState,
              labelSearch: search || undefined,
            }));
          }}
        >
          Search nodes:
          <input
            type={"text"}
            value={search || ""}
            onChange={(event) => {
              let value = event.target.value;
              setSearch(value);
            }}
          />
          <input type={"submit"} />
        </form>
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
