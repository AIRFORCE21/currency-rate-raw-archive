// scraper/save_pdf.js
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

// Match Python base path and the IST-named folders it already created
const BASE_DIR = path.join("data", "Currency Raw Data");

// AXIS & ICICI to render as PDF
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

  const longMonth = new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "long" }).format(d);  // e.g., December
  const shortMonth = new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "short" }).format(d); // e.g., Dec
  const yearFull = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric" }).format(d);  // e.g., 2026
  const yy = yearFull.slice(-2);
  const dd = new Intl.DateTimeFormat("en-CA", { timeZone: tz, day: "2-digit" }).format(d);        // e.g., 12

  const monthFolder = `${longMonth} ${yy}`;   // "December 26"
  const dayFolder = `${dd}${shortMonth} ${yy}`; // "12Dec 26"
  const folder = path.join(BASE_DIR, yearFull, monthFolder, dayFolder);
  fs.mkdirSync(folder, { recursive: true });
  return folder;
}

async function gotoWithRetry(page, url, tries = 3) {
  let lastErr;
  for (let i = 1; i <= tries; i++) {
    try {
      await page.goto(url, { waitUntil: "networkidle2", timeout: 120000 });
      return;
    } catch (e) {
      lastErr = e;
      console.warn(`goto failed (try ${i}/${tries}) for ${url}: ${e.message}`);
      await new Promise(r => setTimeout(r, 2000 * i));
    }
  }
  throw lastErr;
}

(async () => {
  const folder = istParts();
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });
  const page = await browser.newPage();
  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  );

  for (const s of SOURCES) {
    try {
      console.log(`Printing ${s.name} → PDF`);
      await gotoWithRetry(page, s.url);
      // Give late-loading tables a moment
      await page.waitForTimeout(2000);
      const out = path.join(folder, `${s.name}.pdf`);
      await page.pdf({ path: out, format: "A4", printBackground: true });
      console.log(`Saved ${out}`);
    } catch (err) {
      console.error(`FAILED to print ${s.name}: ${err.message}`);
    }
  }

  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
