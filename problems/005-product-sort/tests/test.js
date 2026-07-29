const assert = require("node:assert/strict");
const { describe, it, before, after } = require("node:test");
const http = require("http");
const app = require("../src/index");

describe("Product sort", () => {
  let server, baseUrl;
  before(() => new Promise((resolve) => {
    server = app.listen(0, () => { baseUrl = `http://127.0.0.1:${server.address().port}`; resolve(); });
  }));
  after(() => { if (server) server.close(); });
  function fetch(path) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, baseUrl);
      const req = http.request(url, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve({ status: res.statusCode, body: JSON.parse(data) }));
      });
      req.on("error", reject);
      req.end();
    });
  }
  it("sorts ascending by price", async () => {
    const resp = await fetch("/products?sort=price&order=asc");
    assert.equal(resp.status, 200);
    const prices = resp.body.map((p) => p.price);
    for (let i = 1; i < prices.length; i++) {
      assert.ok(prices[i - 1] <= prices[i], `Expected ascending, but ${prices[i-1]} > ${prices[i]}`);
    }
  });
  it("sorts descending by price", async () => {
    const resp = await fetch("/products?sort=price&order=desc");
    assert.equal(resp.status, 200);
    const prices = resp.body.map((p) => p.price);
    for (let i = 1; i < prices.length; i++) {
      assert.ok(prices[i - 1] >= prices[i], `Expected descending, but ${prices[i-1]} < ${prices[i]}`);
    }
  });
  it("puts 9.99 before 100.00 in ascending order", async () => {
    const resp = await fetch("/products?sort=price&order=asc");
    assert.equal(resp.status, 200);
    const price99 = resp.body.find((p) => p.price === 9.99);
    const price100 = resp.body.find((p) => p.price === 100.0);
    assert.ok(resp.body.indexOf(price99) < resp.body.indexOf(price100), "9.99 should precede 100.00");
  });
});
