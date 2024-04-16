import "./App.css";
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";
import { GraphViewer } from "./graph/GraphViewer";

function NavBar() {
  return (
    <div className="navbar">
      <Link to={"/graph"}>Graph Viewer</Link>
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
