import Graph, { GraphData, GraphEvents } from "react-vis-graph-wrapper";
import "./graph.css";

interface GraphCompProps {
  graphData: GraphData;
  events?: GraphEvents;
}

export const GraphComp: React.FC<GraphCompProps> = ({
  graphData, events,
}: GraphCompProps) => {
  var options = {};

  return (
    <div className="graph-container">
      <Graph graph={graphData} options={options} events={events} />
    </div>
  );
};
