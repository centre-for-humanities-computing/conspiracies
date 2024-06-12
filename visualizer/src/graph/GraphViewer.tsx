import React, {useEffect, useRef, useState} from "react";
import {
    EnrichedGraphData,
    EnrichedNode,
    FileGraphService,
    filter,
    GraphFilter,
    GraphService,
    SampleGraphService,
} from "./GraphService";
import FileUploadComponent from "../datasources/FileUploadComp";
import Graph, {GraphEvents, Options} from "react-vis-graph-wrapper";
import {GraphFilterControlPanel} from "./GraphFilterControlPanel";
import {GraphOptionsControlPanel} from "./GraphOptionsControlPanel";
import {NodeInfo} from "./NodeInfo";


export const GraphViewer: React.FC = () => {
    let graphServiceRef = useRef<GraphService>(new SampleGraphService());
    const [graphData, setGraphData] = useState(
        graphServiceRef.current.getGraph()
    );

    const handleFileLoaded = (data: any) => {
        graphServiceRef.current = new FileGraphService(data);
        setGraphData(filter(graphFilter, graphServiceRef.current.getGraph()));
    };

    const [graphFilter, setGraphFilter] = useState(new GraphFilter(5, 3))
    const [selected, setSelected] = useState(new Set<string>())
    const [selectedNode, setSelectedNode] = useState<EnrichedNode | undefined>(undefined)

    useEffect(
        () => {
            let newGraphData: EnrichedGraphData;
            if (selected.size > 0) {
                newGraphData = graphServiceRef.current.getSubGraph(selected);
            } else {
                newGraphData = graphServiceRef.current.getGraph();
            }
            setGraphData(filter(graphFilter, newGraphData))
        },
        [graphFilter, selected]
    )

    let events: GraphEvents = {
        doubleClick: ({nodes}) => {
            const newSelected = new Set(selected);
            nodes.forEach((element: string) => {
                newSelected.delete(element);
            });
            setSelected(newSelected);
        },
        select: ({nodes}) => {
            let newSelected: Set<string>;
            if (nodes.length > 1) {
                newSelected = new Set<string>();
                nodes.forEach((element: string) => {
                    newSelected.add(element);
                });
                setSelected(newSelected);
            }
        },
        hold: ({nodes}) => {
            const newSelected = new Set(selected);
            nodes.forEach((element: string) => {
                Array.from(graphServiceRef.current.getConnectedNodes(element)).forEach(c => newSelected.add(c))
            });
            setSelected(newSelected);
        },
        selectNode: ({nodes}) => {
            setSelectedNode(graphServiceRef.current.getNode(nodes[0]));
        },
        deselectNode: () => {
            setSelectedNode(undefined);
        }
    };

    let [options, setOptions] = useState<Options>({
        physics: {
            enabled: true,
            barnesHut: {
                springLength: 200
            }
        },
        edges: {
            smooth: false,
            font: {
                align: 'top'
            }
        }
    })

    return (
        <div>

            <div className={"padded"}>
                <FileUploadComponent onFileLoaded={handleFileLoaded}/>
            </div>
            <div className={"padded"}>
                <GraphFilterControlPanel graphFilter={graphFilter} setGraphFilter={setGraphFilter}/>
                <GraphOptionsControlPanel options={options} setOptions={setOptions}/>
            </div>
            <div className={"padded"}>
                <div className={"flex-container"}>
                    <div className={"flex-container__element"}>
                        <span><b>Shift+select</b> to show subgraph.</span>
                    </div>
                    <div className={"flex-container__element"}>
                        <span><b>Double-click</b> node to remove it.</span>
                    </div>
                    <div className={"flex-container__element"}>
                        <span><b>Hold</b> to expand from node.</span>
                    </div>
                    <button className={"flex-container__element"} onClick={() => {
                        setGraphData(filter(graphFilter, graphServiceRef.current.getGraph()));
                        setSelected(new Set<string>());
                    }}>
                        Reset selection
                    </button>
                </div>


            </div>
            <div className="graph-container">
                {selectedNode && <NodeInfo node={selectedNode}/>}

                <Graph graph={graphData} options={options} events={events}/>
            </div>
        </div>
    );
};
