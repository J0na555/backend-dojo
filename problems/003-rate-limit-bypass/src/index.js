const express = require("express");
const rateLimiter = require("./middleware/rateLimiter");
const apiRoutes = require("./routes/api");
const app = express();
app.use(express.json());
app.use(rateLimiter);
app.use("/api", apiRoutes);
app.get("/health", (_req, res) => res.json({ status: "ok" }));
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Listening on ${PORT}`));
}
module.exports = app;
