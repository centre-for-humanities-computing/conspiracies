import { Router } from "express";
import { getGraph } from "../controllers/graph";
import { getDocController, getDocsController } from "../controllers/docs";

const router = Router();

router.get("/:id", getDocController);
router.post("/", getDocsController);

export const routes = router;
