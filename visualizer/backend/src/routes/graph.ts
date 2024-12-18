import { Router } from "express";
import { getGraph } from "../controllers/graph";

const router = Router();

router.get("/", getGraph);

export const routes = router;
