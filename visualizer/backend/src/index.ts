import { createServer } from "./server";

const { start } = createServer();
const port = process.env.PORT || 5000;

start(port);
