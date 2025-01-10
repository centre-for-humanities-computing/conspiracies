import React, { useEffect, useMemo, useState } from "react";
import Graph, { GraphEvents, Options } from "react-vis-graph-wrapper";
import { GraphOptionsControlPanel } from "./GraphOptionsControlPanel";
import { useServiceContext } from "../service/ServiceContextProvider";
import { Edge, GraphData, Node } from "@shared/types/graph";
import { NodeInfo } from "../inspector/NodeInfo";
import { EdgeInfo } from "../inspector/EdgeInfo";
import { GraphFilter } from "@shared/types/graphfilter";
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

  const [blacklistParts, setBlacklistParts] = useState<string[][]>([]);
  const blacklistSet = useMemo(() => {
    const result = new Set<string>();
    for (let add of blacklistParts) {
      for (let member of add) {
        result.add(member);
      }
    }
    return result;
  }, [blacklistParts]);
  const blacklist = useMemo<string[] | undefined>(() => {
    return blacklistSet.size === 0 ? undefined : [...blacklistSet];
  }, [blacklistSet]);

  const [partialGraphFilter, setPartialGraphFilter] = useState<GraphFilter>({
    limit: 50,
    minimumEdgeFrequency: 5,
  });

  const [graphData, setGraphData] = useState<GraphData>({
    edges: [],
    nodes: [],
  });
  useEffect(() => {
    graphService
      .getGraph({
        ...partialGraphFilter,
        whitelistedEntityIds: whitelist,
        blacklistedEntityIds: blacklist,
      })
      .then((r) => setGraphData(r));
  }, [graphService, partialGraphFilter, whitelist, whitelistSet, blacklist]);

  const coloredGraphData = useMemo(() => {
    return {
      ...graphData,
      nodes: graphData.nodes.map((n) => ({
        ...n,
        // TODO: fix this horrible block
        color: whitelistSet.has(n.id.toString())
          ? "lightgreen"
          : n.focus
            ? "yellow"
            : blacklistSet.has(n.id.toString())
              ? "red"
              : "cyan",
      })),
    };
  }, [blacklistSet, graphData, whitelistSet]);

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
    hold: ({ nodes }) => {
      if (nodes.length === 0) return;
      const node = nodes.map((v: number) => v.toString())[0];
      if (whitelistSet.has(node)) {
        setWhitelistSet(
          (prevState) => new Set([...prevState].filter((n) => n !== node)),
        );
      }
      setBlacklistParts((prev) => [...prev, [node]]);
    },
    select: ({ nodes }) => {
      if (nodes.length < 2) return;
      nodes = nodes
        .map((v: number) => v.toString())
        .filter((n: string) => !whitelistSet.has(n));
      setBlacklistParts((prev) => [...prev, nodes]);
    },
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

  const [showControlPanel, setShowContralPanel] = useState<boolean>(true);

  return (
    <div>
      <button
        onClick={() => setShowContralPanel((prev) => !prev)}
        style={{
          position: "absolute",
          top: "1px",
          right: "1px",
          zIndex: 5,
          fontSize: "16px",
        }}
      >
        {showControlPanel ? <>&#8614;</> : <>&#8612;</>}
      </button>
      <div
        className={
          "panel control-panel " +
          (showControlPanel ? "" : "control-panel--hidden")
        }
      >
        <GraphOptionsControlPanel options={options} setOptions={setOptions} />
        <hr />
        {partialGraphFilter && (
          <GraphFilterControlPanel
            graphFilter={partialGraphFilter}
            setGraphFilter={setPartialGraphFilter}
          />
        )}
        <hr />
        <div className={"flex-container flex-container--vertical"}>
          <div>
            <span>
              <b>Double-click</b> to add or remove nodes from whitelist.
            </span>
          </div>
          <div className={"flex-container"}>
            <div>
              <b>Hold</b> or <b>shift+mark</b> to add nodes to blacklist.
            </div>
            <button
              disabled={blacklistParts.length === 0}
              onClick={() =>
                setBlacklistParts((prevState) =>
                  prevState.slice(0, prevState.length - 1),
                )
              }
            >
              &#8617;
            </button>
          </div>

          <button
            onClick={() => {
              setWhitelistSet(new Set<string>());
              setBlacklistParts([]);
            }}
          >
            Reset selection
          </button>
        </div>
      </div>

      <div className="graph-container">
        {selectedNode && <NodeInfo node={selectedNode} />}
        {selectedEdge && <EdgeInfo edge={selectedEdge} />}
        <Graph graph={coloredGraphData} options={options} events={events} />
      </div>
    </div>
  );
};
