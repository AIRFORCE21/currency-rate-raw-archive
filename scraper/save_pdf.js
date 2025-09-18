// scraper/save_pdf.js
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

// Match Python's base and folder naming exactly
const BASE_DIR = path.join("data", "Currency Raw Data");

// AXIS & ICICI are HTML pages we need to print to PDF
const SOURCES = [
  {
    name: "AXIS_Rates",
    url: "https://application.axisbank.co.in/WebForms/corporatecardrate/index.aspx",
  },
  {
    name: "ICICI_Rates",
    url: "https://www.icicibank.com/corporate/global-markets/forex/forex-card-rate",
  },
];

function istParts() {
  const tz = "Asia/Kolkata";
  const d = new Date();

  const longMonth = new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "long" }).format(d);  // December
  const shortMonth = new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "short" }).format(d); // Dec
  const yearFull = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric" }).format(d);  // 2026
  const year2 = yearFull.slice(-2);                                                                // 26
  const day = new Intl.DateTimeFormat("en-CA", { timeZone: tz, day: "2-digit" }).format(d);       // 12

  const monthFolder = `${longMonth} ${year2}`;   // "December 26"
  const dayFolder = `${day}${shortMonth} ${year2}`; // "12Dec 26"
  const folder = path.join(BASE_DIR, yearFull, monthFolder, dayFolder);
  fs.mkdirSync(folder, { recursive: true });
  return { folder };
}

(async () => {
  const { folder } = istParts();
  const browser = await puppeteer.launch({ args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  );

  for (const s of SOURCES) {
    console.log(`Printing ${s.name} → PDF`);
    await page.goto(s.url, { waitUntil: "networkidle2", timeout: 120000 });
    const out = path.join(folder, `${s.name}.pdf`);
    await page.pdf({ path: out, format: "A4", printBackground: true });
    console.log(`Saved ${out}`);
  }

  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
