const { Router } = require("express");

const router = Router();

// In-memory "database"
let items = [
  { id: 1, name: "item-one" },
  { id: 2, name: "item-two" },
  { id: 3, name: "item-three" },
];
let nextId = 4;

router.get("/items", (_req, res) => {
  res.json(items);
});

router.post("/items", (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: "name is required" });
  const item = { id: nextId++, name };
  items.push(item);
  res.status(201).json(item);
});

router.delete("/items/:id", (req, res) => {
  const id = Number(req.params.id);
  const idx = items.findIndex((i) => i.id === id);
  if (idx === -1) return res.status(404).json({ error: "Not found" });
  items.splice(idx, 1);
  res.status(204).end();
});

module.exports = router;
