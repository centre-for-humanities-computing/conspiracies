import React, { useMemo, useState } from "react";
import Graph, { GraphEvents, Options } from "react-vis-graph-wrapper";
import { GraphFilterControlPanel } from "./GraphFilterControlPanel";
import { GraphOptionsControlPanel } from "./GraphOptionsControlPanel";
import { useServiceContext } from "../service/ServiceContextProvider";
import { EnrichedGraphData } from "./GraphServiceOld";

export interface GraphViewerProps {}

export const GraphViewer: React.FC = () => {
  const { getGraphService } = useServiceContext();

  const [enrichedGraphData, setEnrichedGraphData] = useState<EnrichedGraphData>(
    { edges: [], nodes: [] },
  );

  getGraphService()
    .getGraph()
    .then((r) => setEnrichedGraphData(r));

  let events: GraphEvents = {};

  let [options, setOptions] = useState<Options>({
    physics: {
      enabled: true,
      barnesHut: {
        springLength: 200,
      },
    },
    edges: {
      smooth: false,
      font: {
        align: "top",
      },
    },
  });

  return (
    <div>
      <div className={"padded"}>
        {/*<GraphFilterControlPanel*/}
        {/*  graphFilter={graphFilter}*/}
        {/*  setGraphFilter={setGraphFilter}*/}
        {/*/>*/}
        <GraphOptionsControlPanel options={options} setOptions={setOptions} />
      </div>
      <div className={"padded"}>
        <div className={"flex-container"}>
          <div className={"flex-container__element"}>
            <span>
              <b>Shift+mark multiple</b> to make subgraph.
            </span>
          </div>
          <div className={"flex-container__element"}>
            <span>
              <b>Hold</b> node to remove it.
            </span>
          </div>
          <div className={"flex-container__element"}>
            <span>
              <b>Double-click</b> to expand from node.
            </span>
          </div>
          {/*<button*/}
          {/*  className={"flex-container__element"}*/}
          {/*  onClick={() => {*/}
          {/*    setSubgraphNodes(new Set<string>());*/}
          {/*  }}*/}
          {/*>*/}
          {/*  Reset selection*/}
          {/*</button>*/}
        </div>
      </div>
      <div className="graph-container">
        <Graph graph={enrichedGraphData} options={options} events={events} />
      </div>
    </div>
  );
};
