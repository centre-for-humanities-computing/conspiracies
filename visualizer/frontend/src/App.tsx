import "./App.css";
import { GraphViewer } from "./graph/GraphViewer";
import React from "react";
import { ServiceContextProvider } from "./service/ServiceContextProvider";

export function App() {
  return (
    <ServiceContextProvider>
      <GraphViewer />
    </ServiceContextProvider>
  );
}

export default App;
