const { Router } = require("express");
const products = require("../data/products");

const router = Router();

/**
 * GET /products?sort=price&order=asc
 *
 * BUG: Uses String.localeCompare for sorting prices.
 * This does lexicographic comparison ("9.99" > "100.00" because
 * '9' > '1'), not numeric comparison.
 */
router.get("/", (req, res) => {
  const { sort, order = "asc" } = req.query;

  let result = [...products];

  if (sort === "price") {
    result.sort((a, b) => {
      const aPrice = String(a.price);
      const bPrice = String(b.price);
      // BUG: string comparison instead of numeric subtraction
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
