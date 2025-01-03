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

  const [selectedNode, setSelectedNode] = useState<Node>();
  const [selectedEdge, setSelectedEdge] = useState<Edge>();

  const [whitelistSet, setWhitelistSet] = useState<Set<string>>(
    new Set<string>(),
  );
  const whitelist = useMemo<string[] | undefined>(() => {
    return whitelistSet.size === 0 ? undefined : [...whitelistSet];
  }, [whitelistSet]);

  const [graphFilter, setGraphFilter] = useState<GraphFilter>({
    limit: 50,
    minimumEdgeFrequency: 5,
  });

  const [graphData, setGraphData] = useState<GraphData>({
    edges: [],
    nodes: [],
  });
  useEffect(() => {
    graphService
      .getGraph({ ...graphFilter, whitelistedEntityIds: whitelist })
      .then((r) =>
        setGraphData({
          ...r,
          // TODO: do this elsewhere!
          nodes: r.nodes.map((n) => ({
            ...n,
            color: whitelistSet.has(n.id.toString()) ? "lightgreen" : "cyan",
          })),
        }),
      );
  }, [graphService, graphFilter, whitelist, whitelistSet]);

  const [dataBounds, setDataBounds] = useState<DataBounds>();
  useEffect(() => {
    graphService.getDataBounds().then((r) => setDataBounds(r));
  }, [graphService]);

  const graphDataMaps = useMemo(() => {
    return {
      nodesMap: new Map(graphData.nodes.map((node) => [node.id!, node])),
      edgeGroupMap: new Map(graphData.edges.map((edge) => [edge.id, edge])),
    };
  }, [graphData]);

  let events: GraphEvents = {
    doubleClick: ({ nodes }) => {
      if (nodes.length === 0) return;
      const node = nodes.map((v: number) => v.toString())[0];
      if (whitelistSet.has(node)) {
        setWhitelistSet(
          (prevState) => new Set([...prevState].filter((n) => n !== node)),
        );
      } else {
        setWhitelistSet((prevState) => new Set([...prevState, node]));
      }
    },
    // hold: ({ nodes }) => {
    //   nodes = nodes.map((v: number) => v.toString());
    //   setWhitelistSet(
    //     (prevState) =>
    //       new Set([...prevState].filter((n) => nodes.indexOf(n) < 0)),
    //   );
    // },
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
              <b>Double-click</b> to add or remove nodes from whitelist (marked
              green).
            </span>
          </div>
          {/*<div className={"flex-container__element"}>*/}
          {/*  <span>*/}
          {/*    <b>Hold</b> node to remove it from the whitelist.*/}
          {/*  </span>*/}
          {/*</div>*/}

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
