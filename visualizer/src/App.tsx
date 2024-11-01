import "./App.css";
import {BrowserRouter, HashRouter, Link, Route, Routes} from "react-router-dom";
import {GraphViewer} from "./graph/GraphViewer";

function NavBar() {
    return (
        <div className="navbar">
            <Link to={"/graph"}>Graph Viewer</Link>
        </div>
    );
}

export function App() {
    // Create actual routes if/when more functionality is added to the application
    return (
        <HashRouter>
            <Routes>
                <Route
                    path="/"
                    element={<GraphViewer/>}
                />
            </Routes>
        </HashRouter>
    );
}

export default App;
