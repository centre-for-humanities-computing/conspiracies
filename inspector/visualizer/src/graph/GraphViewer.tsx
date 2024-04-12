import { useRef, useState } from "react";
import {
  EnrichedGraphData,
  FileGraphService,
  GraphFilter,
  GraphService,
  SampleGraphService,
} from "./GraphService";
import FileUploadComponent from "../datasources/FileUploadComp";
import { GraphComp } from "./GraphComp";
import { GraphData, GraphEvents } from "react-vis-graph-wrapper";

interface GraphViewerProps {}

export const GraphViewer: React.FC<
  GraphViewerProps
> = ({}: GraphViewerProps) => {
  let graphServiceRef = useRef(new SampleGraphService());
  const [graphData, setGraphData] = useState(
    graphServiceRef.current.getGraph()
  );

  let graphFilter: GraphFilter = new GraphFilter();
  graphFilter.addFilter("minimumFrequency", (node) => node.stats.frequency > 3);

  const handleFileLoaded = (data: any) => {
    graphServiceRef.current = new FileGraphService(data);
    setGraphData(graphFilter.filter(graphServiceRef.current.getGraph()));
  };

  const [selected, setSelected] = useState(new Set<string>())

  const handleSubGraphClick = () => {
    setGraphData(graphFilter.filter(graphServiceRef.current.getSubGraph(selected)))
  }

  let events: GraphEvents = {
    doubleClick: ({ nodes }) => {
        const newSelected = new Set(selected);
        nodes.forEach((element: string) => {
          newSelected.delete(element);
        });
        setSelected(newSelected);

    },
    select: ({ nodes }) => {
        const newSelected = new Set<string>(); // Create a new Set based on the current state
        nodes.forEach((element: string) => {
          Array.from(graphServiceRef.current.getConnectedNodes(element)).forEach(c => newSelected.add(c))
        });
        setSelected(newSelected);


    },
    hold: ({ nodes }) => {
        console.log("holding")
        const newSelected = new Set(selected); // Create a new Set based on the current state
        nodes.forEach((element: string) => {
          newSelected.add(element); // Modify the new Set
        });
        setSelected(newSelected);

    },
  };

  return (
    <div>
      <button onClick={handleSubGraphClick}>Show sub-graph of selected</button>
      <FileUploadComponent onFileLoaded={handleFileLoaded} />
      <GraphComp graphData={graphData} events={events} />
    </div>
  );
};
