import express, { Express } from "express";
import dotenv from "dotenv";
import cors from "cors";
import { routes as graphRoutes } from "./routes/graph";

dotenv.config();

export function createServer(): {
  start: (port: string | number) => void;
} {
  const app: Express = express();

  const databasePath = process.env.DB_PATH;
  if (!databasePath) {
    console.error("Error: DB_PATH environment variable is not set.");
    process.exit(1);
  }
  console.log(`Using database: ${databasePath}`);

  app.use(cors()); // Allow requests from frontend
  app.use(express.json());
  app.use("/graph", graphRoutes);

  return {
    start: (port: string | number) => {
      app.listen(port, () => {
        console.log(`Server running on http://localhost:${port}`);
      });
    },
  };
}
