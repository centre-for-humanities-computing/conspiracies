import { Router } from "express";
import {
  getGraph,
  getBounds,
  getEntity,
  getRelation,
} from "../controllers/graph";

const router = Router();

router.post("/", getGraph);
router.get("/bounds", getBounds);
router.get("/node/:id", getEntity);
router.get("/edge/:id", getRelation);

export const routes = router;
