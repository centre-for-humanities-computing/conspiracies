import { Router } from "express";
import { getGraph } from "../controllers/graph";
import { getDoc, getDocs } from "../controllers/docs";

const router = Router();

router.get("/:id", getDoc);
router.post("/", getDocs);

export const routes = router;
