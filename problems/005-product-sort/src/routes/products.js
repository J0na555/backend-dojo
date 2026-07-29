const { Router } = require("express");
const products = require("../data/products");
const router = Router();

router.get("/", (req, res) => {
  const { sort, order = "asc" } = req.query;
  let result = [...products];
  if (sort === "price") {
    result.sort((a, b) => order === "desc" ? b.price - a.price : a.price - b.price);
  } else if (sort === "name") {
    result.sort((a, b) => order === "desc" ? b.name.localeCompare(a.name) : a.name.localeCompare(b.name));
  }
  res.json(result);
});
module.exports = router;
