// scraper/save_pdf.js
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

// Match Python's base path & IST date logic
const BASE_DIR = path.join("data", "Currency Rate RAW Data");

function istDateStrParts() {
  const tz = "Asia/Kolkata";
  const now = new Date();
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit"
  });
  const parts = Object.fromEntries(fmt.formatToParts(now).map(p => [p.type, p.value]));
  return { year: parts.year, month: parts.month, day: parts.day };
}

function todayFolder() {
  const { year, month, day } = istDateStrParts();
  const folder = path.join(BASE_DIR, year, month, day);
  fs.mkdirSync(folder, { recursive: true });
  return folder;
}

// Duplicate the same source list used by Python (name/url/ext)
const SOURCES = [
  { name: "HDFC_Rates",
    url: "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=/Personal/Home/content/rates.pdf",
    ext: "pdf" },
  { name: "AXIS_Rates",
    url: "https://application.axisbank.co.in/WebForms/corporatecardrate/index.aspx",
    ext: "html" },
  { name: "ICICI_Rates",
    url: "https://www.icicibank.com/corporate/global-markets/forex/forex-card-rate",
    ext: "html" },
];

(async () => {
  const folder = todayFolder();
  const browser = await puppeteer.launch({ args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");

  for (const s of SOURCES) {
    if (s.ext !== "html") {
      console.log(`Skip browser print for ${s.name} (already PDF).`);
      continue;
    }
    console.log(`PDF-printing ${s.name} from ${s.url}`);
    await page.goto(s.url, { waitUntil: "networkidle2", timeout: 120000 });
    const out = path.join(folder, `${s.name}.pdf`);
    await page.pdf({ path: out, format: "A4", printBackground: true });
    console.log(`Saved ${out}`);
  }

  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
