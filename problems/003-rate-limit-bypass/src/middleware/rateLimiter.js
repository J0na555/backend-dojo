const requests = new Map();
const WINDOW_MS = 60_000;
const MAX_REQUESTS = 10;

function getClientIp(req) {
  // Only use req.ip — never trust client-supplied X-Forwarded-For.
  return req.ip || req.socket.remoteAddress;
}

function rateLimiter(req, res, next) {
  const clientIp = getClientIp(req);
  const now = Date.now();
  if (!requests.has(clientIp)) {
    requests.set(clientIp, []);
  }
  const timestamps = requests.get(clientIp);
  while (timestamps.length > 0 && timestamps[0] < now - WINDOW_MS) {
    timestamps.shift();
  }
  if (timestamps.length >= MAX_REQUESTS) {
    return res.status(429).json({ error: "Too many requests" });
  }
  timestamps.push(now);
  next();
}

// Exposed for test isolation
rateLimiter.reset = function () {
  requests.clear();
};

module.exports = rateLimiter;
