import express, { Express } from "express";
import dotenv from "dotenv";
import cors from "cors";
import { routes as graphRoutes } from "./routes/graph";

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 5000;

app.use(cors()); // Allow requests from frontend
app.use(express.json());
app.use("/graph", graphRoutes);

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
