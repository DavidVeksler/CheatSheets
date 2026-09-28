// Local stand-in for https://api.resend.com/emails during test/contract.sh.
// Accepts a send and answers like Resend; a "to" containing "+fail" gets a 500.
// Writes the last confirmation URL to $STUB_OUT so the test can click it, and a
// count of sends; never prints message contents. Nothing leaves this machine.
import http from "node:http";
import fs from "node:fs";
const port = Number(process.env.STUB_PORT || 8798);
const out = process.env.STUB_OUT;
let sends = 0;
let lastLink = null;
const subjects = [];
http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    let msg = {};
    try { msg = JSON.parse(body || "{}"); } catch {}
    const to = String(msg.to || "");
    if (to.includes("+fail")) {
      res.writeHead(500, { "content-type": "application/json" });
      return res.end(JSON.stringify({ message: "stub failure" }));
    }
    sends++;
    const link = /https?:\/\/[^\s"]*confirm\.php\?p=[^\s"&]+&(?:amp;)?s=[^\s"]+/.exec(String(msg.text || ""));
    if (link) lastLink = link[0];
    subjects.push(msg.subject || "");
    if (out) fs.writeFileSync(out, JSON.stringify({ sends, link: lastLink, subjects }));
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ id: "stub-" + sends }));
  });
}).listen(port, "127.0.0.1");
