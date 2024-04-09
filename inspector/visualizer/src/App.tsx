import "./App.css";
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";
import { GraphComp } from "./graph/GraphComp";
import {
  GraphService,
  SampleGraphService,
  sampleGraphData,
} from "./graph/GraphService";

function NavBar() {
  return (
    <div className="navbar">
      <Link to={"/test"}>Test</Link>
    </div>
  );
}

export function App() {
  let graphService: GraphService = new SampleGraphService();

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
            path="test"
            element={<GraphComp graphData={graphService.getGraph()} />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
