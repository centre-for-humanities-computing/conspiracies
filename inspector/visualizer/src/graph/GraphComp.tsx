import Graph, { GraphData } from "react-graph-vis";
import "./graph.css";
import { FileGraphService, SampleGraphService } from "./GraphService";

interface GraphCompProps {
  graphData: GraphData;
}

export function GraphComp(props: GraphCompProps) {
  let { graphData } = props;
  var options = {};

  var events = {};

  let service = new SampleGraphService();

  return (
    <div className="graph-container">
      <Graph graph={service.getGraph()} options={options} events={events} />
    </div>
  );
}
