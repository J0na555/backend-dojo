/**
 * Simple in-memory sliding-window rate limiter.
 */

const requests = new Map();
const WINDOW_MS = 60_000; // 1 minute
const MAX_REQUESTS = 10;

function getClientIp(req) {
  return req.ip || req.socket.remoteAddress;
}

function rateLimiter(req, res, next) {
  const clientIp = getClientIp(req);

  const now = Date.now();
  if (!requests.has(clientIp)) {
    requests.set(clientIp, []);
  }

  const timestamps = requests.get(clientIp);
  // Remove entries outside the current window
  while (timestamps.length > 0 && timestamps[0] < now - WINDOW_MS) {
    timestamps.shift();
  }

  if (timestamps.length >= MAX_REQUESTS) {
    return res.status(429).json({ error: "Too many requests" });
  }

  timestamps.push(now);
  next();
}
rateLimiter.reset = function () {
  requests.clear();
};

module.exports = rateLimiter;
