const express = require("express");
const rateLimiter = require("./middleware/rateLimiter");
const apiRoutes = require("./routes/api");

const app = express();
app.use(express.json());

// app.set("trust proxy", false);

// Apply rate limiter globally
app.use(rateLimiter);

app.use("/api", apiRoutes);

// Health check (not rate-limited, but fine for this demo)
app.get("/health", (_req, res) => res.json({ status: "ok" }));

// Only start listening when run directly, not when imported by tests
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Listening on ${PORT}`));
}

module.exports = app;
