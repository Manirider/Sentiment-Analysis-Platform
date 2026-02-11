
import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080']
  });
  const page = await browser.newPage();
  
  try {
    console.log("Navigating to dashboard...");
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });
    await page.setViewport({ width: 1920, height: 1080 });
    
    page.on('console', msg => {
        const type = msg.type();
        const text = msg.text();
        console.log(`PAGE LOG [${type}]: ${text}`);
    });
    page.on('pageerror', err => {
        console.log(`PAGE ERROR: ${err.toString()}`);
    });
    page.on('error', err => {
        console.log(`BROWSER ERROR: ${err.toString()}`);
    });

    console.log("Initial URL:", page.url());
    await page.screenshot({ path: 'debug_nav_0_initial.png' });

    // Click "Live Stream"
    // Click "Live Stream"
    console.log("Looking for Live Stream link...");
    try {
        const liveStreamLink = await page.waitForSelector('a[href="/feed"]', { timeout: 5000 });
        console.log("Found Live Stream link. Clicking...");
        await liveStreamLink.click();
        await new Promise(r => setTimeout(r, 2000));
        console.log("URL after click:", page.url());
        await page.screenshot({ path: 'debug_nav_1_after_click.png' });
    } catch (e) {
        console.error("Could not find Live Stream link: " + e.message);
        const html = await page.content();
        console.log("PAGE HTML DUMP:", html.substring(0, 2000)); // dump start of HTML
    }

    // Click "Deep Dive"
    console.log("Looking for Deep Dive link...");
    try {
        const deepDiveLink = await page.waitForSelector("xpath///a[contains(., 'Deep Dive')]", { timeout: 5000 });
        console.log("Found Deep Dive link. Clicking...");
        await deepDiveLink.click();
        await new Promise(r => setTimeout(r, 2000));
        console.log("URL after Deep Dive click:", page.url());
        await page.screenshot({ path: 'debug_nav_2_after_deep_dive.png' });
    } catch (e) {
         console.error("Could not find Deep Dive link: " + e.message);
    }

  } catch (error) {
    console.error("Error:", error);
  } finally {
    await browser.close();
  }
})();
