import { Router } from "express";
import {
  getEntity,
  getDocsByEntity,
  getEntityLabels,
} from "../controllers/entities";

const router = Router();

router.get("/:id", getEntity);
router.get("/:id/docs", getDocsByEntity);
router.post("/labels", getEntityLabels);

export const routes = router;
