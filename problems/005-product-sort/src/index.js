const express = require("express");
const productsRouter = require("./routes/products");

const app = express();
app.use(express.json());

app.use("/products", productsRouter);

// Only start listening when run directly, not when imported by tests
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Listening on ${PORT}`));
}

module.exports = app;
