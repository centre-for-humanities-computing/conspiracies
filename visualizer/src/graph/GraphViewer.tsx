import React, { useMemo, useRef, useState } from "react";
import {
  EdgeGroup,
  EnrichedNode,
  FileGraphService,
  filter,
  GraphFilter,
  GraphService,
  SampleGraphService,
} from "./GraphService";
import FileUploadComponent from "../datasources/FileUploadComp";
import Graph, { GraphEvents, Options } from "react-vis-graph-wrapper";
import { GraphFilterControlPanel } from "./GraphFilterControlPanel";
import { GraphOptionsControlPanel } from "./GraphOptionsControlPanel";
import { NodeInfo } from "./NodeInfo";
import { EdgeInfo } from "./EdgeInfo";

export const GraphViewer: React.FC = () => {
  let graphServiceRef = useRef<GraphService>(new SampleGraphService());

  const handleFileLoaded = (data: any) => {
    graphServiceRef.current = new FileGraphService(data);
    const top50 =
      graphServiceRef.current
        .getGraph()
        .nodes.map((n) => n.stats.frequency)
        .sort((a, b) => b - a)
        .at(100) || 1;
    let { minNodeFrequency, maxNodeFrequency, maxEdgeFrequency } =
      graphServiceRef.current.getBounds();
    setGraphFilter(
      new GraphFilter(
        minNodeFrequency,
        top50,
        maxNodeFrequency,
        1,
        Math.floor(top50 / 10),
        maxEdgeFrequency,
      ),
    );
  };

  const [graphFilter, setGraphFilter] = useState<GraphFilter>(
    new GraphFilter(1, 1, 10, 1, 1, 10),
  );
  const [subgraphNodes, setSubgraphNodes] = useState(new Set<string>());
  const [selectedNode, setSelectedNode] = useState<EnrichedNode | undefined>(
    undefined,
  );
  const [selectedEdge, setSelectedEdge] = useState<EdgeGroup | undefined>(
    undefined,
  );

  const filteredGraphData = useMemo(() => {
    const baseGraphData =
      subgraphNodes.size > 0
        ? graphServiceRef.current.getSubGraph(subgraphNodes)
        : graphServiceRef.current.getGraph();
    return filter(graphFilter, baseGraphData);
  }, [graphFilter, subgraphNodes]);

  const graphDataMaps = useMemo(() => {
    return {
      nodesMap: new Map(
        filteredGraphData.nodes.map((node) => [node.id!.toString(), node]),
      ),
      edgeGroupMap: new Map(
        filteredGraphData.edges.map((edgeGroup) => [edgeGroup.id, edgeGroup]),
      ),
    };
  }, [filteredGraphData]);

  let events: GraphEvents = {
    hold: ({ nodes }) => {
      const newSubgraphNodes = new Set(subgraphNodes);
      nodes.forEach((element: string) => {
        newSubgraphNodes.delete(element);
      });
      setSubgraphNodes(newSubgraphNodes);
    },
    select: ({ nodes }) => {
      let newSelected: Set<string>;
      if (nodes.length > 1) {
        newSelected = new Set<string>();
        nodes.forEach((element: string) => {
          newSelected.add(element);
        });
        setSubgraphNodes(newSelected);
      }
    },
    doubleClick: ({ nodes }) => {
      const newSelected = new Set(subgraphNodes);
      nodes.forEach((element: string) => {
        Array.from(graphServiceRef.current.getConnectedNodes(element)).forEach(
          (c) => newSelected.add(c),
        );
      });
      setSubgraphNodes(newSelected);
    },
    selectNode: ({ nodes }) => {
      setSelectedEdge(undefined);
      setSelectedNode(graphDataMaps.nodesMap.get(nodes[0]));
    },
    selectEdge: ({ edges }) => {
      setSelectedNode(undefined);
      setSelectedEdge(graphDataMaps.edgeGroupMap.get(edges[0]));
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
      smooth: false,
      font: {
        align: "top",
      },
    },
  });

  return (
    <div>
      <div className={"padded flex-container"}>
        <FileUploadComponent onFileLoaded={handleFileLoaded} />
      </div>
      <hr />
      <div className={"padded"}>
        <GraphFilterControlPanel
          graphFilter={graphFilter}
          setGraphFilter={setGraphFilter}
        />
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
          <button
            className={"flex-container__element"}
            onClick={() => {
              setSubgraphNodes(new Set<string>());
            }}
          >
            Reset selection
          </button>
        </div>
      </div>
      <div className="graph-container">
        {selectedNode && <NodeInfo node={selectedNode} />}
        {selectedEdge && <EdgeInfo edges={selectedEdge} />}
        <Graph graph={filteredGraphData} options={options} events={events} />
      </div>
    </div>
  );
};
