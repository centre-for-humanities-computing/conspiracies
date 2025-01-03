import { Router } from "express";
import { getEntity, getDocsByEntity } from "../controllers/entities";

const router = Router();

router.get("/:id", getEntity);
router.get("/:id/docs", getDocsByEntity);

export const routes = router;
