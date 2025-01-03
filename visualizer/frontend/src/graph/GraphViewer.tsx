import React, { useEffect, useMemo, useState } from "react";
import Graph, { GraphEvents, Options } from "react-vis-graph-wrapper";
import { GraphOptionsControlPanel } from "./GraphOptionsControlPanel";
import { useServiceContext } from "../service/ServiceContextProvider";
import { Edge, GraphData, Node } from "@shared/types/graph";
import { NodeInfo } from "../inspector/NodeInfo";
import { EdgeInfo } from "../inspector/EdgeInfo";
import { DataBounds, GraphFilter } from "@shared/types/graphfilter";
import { GraphFilterControlPanel } from "./GraphFilterControlPanel";

export interface GraphViewerProps {}

export const GraphViewer: React.FC = () => {
  const { graphService } = useServiceContext();

  const [graphFilter, setGraphFilter] = useState<GraphFilter>({
    limit: 50,
    minimumEdgeFrequency: 5,
  });

  const [graphData, setGraphData] = useState<GraphData>({
    edges: [],
    nodes: [],
  });
  useEffect(() => {
    graphService.getGraph(graphFilter).then((r) => setGraphData(r));
  }, [graphService, graphFilter]);

  const [dataBounds, setDataBounds] = useState<DataBounds>();
  useEffect(() => {
    graphService.getDataBounds().then((r) => setDataBounds(r));
  }, [graphService]);

  const [selectedNode, setSelectedNode] = useState<Node>();
  const [selectedEdge, setSelectedEdge] = useState<Edge>();

  const graphDataMaps = useMemo(() => {
    return {
      nodesMap: new Map(graphData.nodes.map((node) => [node.id!, node])),
      edgeGroupMap: new Map(graphData.edges.map((edge) => [edge.id, edge])),
    };
  }, [graphData]);

  let events: GraphEvents = {
    selectNode: ({ nodes, edges }) => {
      setSelectedEdge(undefined);
      setSelectedNode(graphDataMaps.nodesMap.get(nodes[0]));
    },
    selectEdge: ({ nodes, edges }) => {
      if (nodes.length < 1) {
        setSelectedNode(undefined);
        setSelectedEdge(graphDataMaps.edgeGroupMap.get(edges[0]));
      }
    },
    deselectNode: () => {
      setSelectedNode(undefined);
    },
    deselectEdge: () => {
      setSelectedEdge(undefined);
    },
  };

  let [options, setOptions] = useState<Options>({
    physics: {
      enabled: true,
      barnesHut: {
        springLength: 200,
      },
    },
    edges: {
      smooth: true,
      font: {
        align: "top",
      },
    },
  });

  return (
    <div>
      <div className={"padded"}>
        <GraphOptionsControlPanel options={options} setOptions={setOptions} />
        {dataBounds && graphFilter && (
          <GraphFilterControlPanel
            dataBounds={dataBounds}
            graphFilter={graphFilter}
            setGraphFilter={setGraphFilter}
          />
        )}
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
        {selectedNode && <NodeInfo node={selectedNode} />}
        {selectedEdge && <EdgeInfo edge={selectedEdge} />}
        <Graph graph={graphData} options={options} events={events} />
      </div>
    </div>
  );
};
