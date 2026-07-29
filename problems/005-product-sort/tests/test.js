const assert = require("node:assert/strict");
const { describe, it, before, after } = require("node:test");
const http = require("http");

const app = require("../src/index");

describe("Product sort", () => {
  let server;
  let baseUrl;

  before(() => {
    return new Promise((resolve) => {
      server = app.listen(0, () => {
        const port = server.address().port;
        baseUrl = `http://127.0.0.1:${port}`;
        resolve();
      });
    });
  });

  after(() => {
    if (server) server.close();
  });

  function fetch(path) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, baseUrl);
      const req = http.request(url, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          resolve({ status: res.statusCode, body: JSON.parse(data) });
        });
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
      assert.ok(
        prices[i - 1] <= prices[i],
        `Expected prices to be ascending, but ${prices[i - 1]} > ${prices[i]}`,
      );
    }
  });

  it("sorts descending by price", async () => {
    const resp = await fetch("/products?sort=price&order=desc");
    assert.equal(resp.status, 200);

    const prices = resp.body.map((p) => p.price);
    for (let i = 1; i < prices.length; i++) {
      assert.ok(
        prices[i - 1] >= prices[i],
        `Expected prices to be descending, but ${prices[i - 1]} < ${prices[i]}`,
      );
    }
  });

  it("puts 9.99 before 100.00 in ascending order", async () => {
    const resp = await fetch("/products?sort=price&order=asc");
    assert.equal(resp.status, 200);

    const price99 = resp.body.find((p) => p.price === 9.99);
    const price100 = resp.body.find((p) => p.price === 100.0);

    const idx99 = resp.body.indexOf(price99);
    const idx100 = resp.body.indexOf(price100);

    assert.ok(
      idx99 < idx100,
      `Expected 9.99 before 100.00 in ascending sort, but got 9.99 at ${idx99} and 100.00 at ${idx100}`,
    );
  });
});
