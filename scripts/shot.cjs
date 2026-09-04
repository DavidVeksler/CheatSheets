#!/usr/bin/env node
"use strict";

const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");

async function main() {
  const files = process.argv.slice(2);
  if (!files.length) {
    console.error("no files");
    return 1;
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1200, height: 630 },
    deviceScaleFactor: 1,
    colorScheme: "dark",
  });
  for (const file of files) {
    const absolute = path.resolve(root, file);
    await page.goto(pathToFileURL(absolute).href, { waitUntil: "load" });
    await page.evaluate(() => {
      document.documentElement.dataset.theme = "dark";
      for (const selector of ["#themeToggle", ".theme-button", ".skip-link", "#backTop", ".utility", "nav.sections"]) {
        document.querySelectorAll(selector).forEach((element) => { element.style.display = "none"; });
      }
      window.scrollTo(0, 0);
    });
    const capture = page.locator("[data-og-capture]");
    let y = 0;
    if (await capture.count()) {
      await capture.evaluate((target) => {
        [...document.body.children].forEach((element) => {
          if (element !== target.parentElement) element.style.display = "none";
        });
        [...target.parentElement.children].forEach((element) => {
          if (element !== target) element.style.display = "none";
        });
        Object.assign(target.parentElement.style, { padding: "0", width: "100%" });
        Object.assign(target.style, { margin: "0", transform: "none", width: "100%" });
        target.querySelectorAll(":scope > h2, :scope > .section-note, :scope > .matrix-key").forEach((element) => {
          element.style.display = "none";
        });
        window.scrollTo(0, 0);
      });
    }
    const stem = path.basename(file, path.extname(file));
    const output = path.join(root, "images", `${stem}.png`);
    await page.screenshot({ path: output, clip: { x: 0, y, width: 1200, height: 630 } });
    console.log("wrote", output);
  }
  await browser.close();
  return 0;
}

main().then((code) => { process.exitCode = code; }).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
