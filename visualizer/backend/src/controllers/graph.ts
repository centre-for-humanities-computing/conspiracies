import { Request, Response } from "express";

export const getGraph = (req: Request, res: Response) => {
  res.json({ message: "Graph data from backend!", data: [] });
};
