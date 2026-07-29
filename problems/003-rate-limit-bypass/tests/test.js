const assert = require("node:assert/strict");
const { describe, it, before, after } = require("node:test");
const http = require("http");
const app = require("../src/index");
const rateLimiter = require("../src/middleware/rateLimiter");

describe("Rate limiter", () => {
  let server, baseUrl;
  before(() => new Promise((resolve) => {
    server = app.listen(0, () => { baseUrl = `http://127.0.0.1:${server.address().port}`; resolve(); });
  }));
  after(() => { if (server) server.close(); });

  function fetch(path, opts = {}) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, baseUrl);
      const options = { hostname: url.hostname, port: url.port, path: url.pathname, method: opts.method || "GET", headers: opts.headers || {} };
      const req = http.request(options, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          let body;
          try { body = JSON.parse(data); } catch { body = data; }
          resolve({ status: res.statusCode, headers: res.headers, body });
        });
      });
      req.on("error", reject);
      if (opts.body) { req.write(JSON.stringify(opts.body)); }
      req.end();
    });
  }

  it("allows up to 10 requests from the same IP", async () => {
    rateLimiter.reset();
    for (let i = 0; i < 10; i++) {
      const resp = await fetch("/api/items");
      assert.equal(resp.status, 200, `request ${i + 1}`);
    }
  });
  it("rejects the 11th request from the same IP", async () => {
    rateLimiter.reset();
    for (let i = 0; i < 10; i++) await fetch("/api/items");
    const resp = await fetch("/api/items");
    assert.equal(resp.status, 429);
  });
  it("rate-limits based on real IP, not spoofed X-Forwarded-For", async () => {
    rateLimiter.reset();
    for (let i = 0; i < 10; i++) {
      const resp = await fetch("/api/items", { headers: { "X-Forwarded-For": `spoofed-${i}` } });
      assert.equal(resp.status, 200, `request ${i + 1}`);
    }
    const blocked = await fetch("/api/items", { headers: { "X-Forwarded-For": "another-spoof" } });
    assert.equal(blocked.status, 429, "Rate limiter should use real IP");
  });
});
