const { Router } = require("express");
const products = require("../data/products");

const router = Router();

/**
 * GET /products?sort=price&order=asc
 */
router.get("/", (req, res) => {
  const { sort, order = "asc" } = req.query;

  let result = [...products];

  if (sort === "price") {
    result.sort((a, b) => {
      const aPrice = String(a.price);
      const bPrice = String(b.price);
      return order === "desc"
        ? bPrice.localeCompare(aPrice)
        : aPrice.localeCompare(bPrice);
    });
  } else if (sort === "name") {
    result.sort((a, b) => {
      return order === "desc"
        ? b.name.localeCompare(a.name)
        : a.name.localeCompare(b.name);
    });
  }

  res.json(result);
});

module.exports = router;
