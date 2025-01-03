import { Router } from "express";
import { getGraph, getBounds } from "../controllers/graph";

const router = Router();

router.post("/", getGraph);
router.get("/bounds", getBounds);

export const routes = router;
