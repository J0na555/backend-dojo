/**
 * Simple in-memory sliding-window rate limiter.
 *
 * BUG: The client IP is read from X-Forwarded-For without validation.
 * An attacker can spoof the header to impersonate other IPs and
 * exhaust their rate-limit budget.
 */

const requests = new Map();
const WINDOW_MS = 60_000; // 1 minute
const MAX_REQUESTS = 10;

function getClientIp(req) {
  // BUG: trusts X-Forwarded-For without checking if we're behind a trusted proxy.
  // A client can set this header to any value.
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
// reset for the tests, cause they fuck u up more than than the actuall drill
rateLimiter.reset = function () {
  requests.clear();
};

module.exports = rateLimiter;
