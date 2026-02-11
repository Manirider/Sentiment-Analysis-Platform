import puppeteer from 'puppeteer';
import path from 'path';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Set viewport to a typical desktop size
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('Navigating to dashboard...');
  try {
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle0', timeout: 30000 });
    
    // Wait for key elements to ensure full load
    await page.waitForSelector('h1', { timeout: 10000 });
    console.log('Dashboard loaded.');

    // Add a small delay for animations
    await new Promise(r => setTimeout(r, 2000));

    const screenshotPath = String.raw`C:\Users\Anonymous\.gemini\antigravity\brain\1e9c4ab6-01ce-4b0d-a2ac-ae982c9d47d0\dashboard_verification.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    
    console.log(`Screenshot saved to: ${screenshotPath}`);
  } catch (error) {
    console.error('Verification failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
