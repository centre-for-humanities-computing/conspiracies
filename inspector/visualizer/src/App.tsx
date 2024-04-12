import "./App.css";
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";
import { GraphComp } from "./graph/GraphComp";
import {
  FileGraphService,
  GraphService,
  SampleGraphService,
  sampleGraphData,
} from "./graph/GraphService";
import FileUploadComponent from "./datasources/FileUploadComp";
import { GraphData } from "react-vis-graph-wrapper";
import { useState } from "react";
import { GraphViewer } from "./graph/GraphViewer";

function NavBar() {
  return (
    <div className="navbar">
      <Link to={"/graph"}>Graph Test</Link>
    </div>
  );
}

export function App() {


  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <>
              <NavBar /> <Outlet /> 
            </>
          }
        >
          <Route
            path="graph"
            element={<GraphViewer />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
