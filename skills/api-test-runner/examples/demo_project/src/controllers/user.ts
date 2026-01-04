import { Request, Response } from "express";

export function registerRoutes(app: any) {
  app.get("/health", (_: Request, res: Response) => res.json({ ok: true }));
  app.post("/auth/login", (_: Request, res: Response) => res.json({ token: "demo" }));
  app.post("/users", (_: Request, res: Response) => res.status(201).json({ id: 1 }));
  app.get("/users/:id", (req: Request, res: Response) => res.json({ id: req.params.id }));
}
