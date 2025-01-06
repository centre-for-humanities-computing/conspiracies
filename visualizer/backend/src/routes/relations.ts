import { Router } from "express";
import { getEntity } from "../controllers/entities";
import { getDocsByRelation, getRelation } from "../controllers/relations";

const router = Router();

router.get("/:id", getRelation);
router.get("/:id/docs", getDocsByRelation);

export const routes = router;
