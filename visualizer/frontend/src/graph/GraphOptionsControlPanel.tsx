import React from "react";
import "./graph.css";
import { Options } from "react-vis-graph-wrapper";

interface GraphOptionsControlPanelProps {
  options: Options;
  setOptions: React.Dispatch<React.SetStateAction<Options>>;
}

function getSmoothEnabled(options: Options): boolean {
  if (typeof options.edges?.smooth === "boolean") {
    return options.edges.smooth;
  } else if (
    typeof options.edges?.smooth === "object" &&
    "enabled" in options.edges.smooth
  ) {
    return options.edges.smooth.enabled;
  } else {
    return false;
  }
}

export const GraphOptionsControlPanel = ({
  options,
  setOptions,
}: GraphOptionsControlPanelProps) => {
  return (
    <div className={"flex-container flex-container--vertical"}>
      <div className={"flex-container"}>
        <span className={"option-span"}>Physics enabled:</span>
        <input
          type={"checkbox"}
          checked={options.physics.enabled}
          onChange={(event) =>
            setOptions({
              ...options,
              physics: {
                ...options.physics,
                enabled: event.target.checked,
              },
            })
          }
        />
      </div>
      <div className={"flex-container"}>
        <span className={"option-span"}>Rounded edges:</span>
        <input
          type={"checkbox"}
          checked={getSmoothEnabled(options)}
          onChange={(event) =>
            setOptions({
              ...options,
              edges: {
                ...options.edges,
                smooth: !options.edges?.smooth,
              },
            })
          }
        />
      </div>
      <div className={"flex-container"}>
        <span className={"option-span"}>Edge length:</span>
        <input
          type="range"
          min="50"
          max="1000"
          value={options.physics.barnesHut.springLength}
          onChange={(event) =>
            setOptions({
              ...options,
              physics: {
                ...options.physics,
                barnesHut: {
                  springLength: Number(event.target.value),
                },
              },
            })
          }
          step="1"
        />
      </div>
    </div>
  );
};
