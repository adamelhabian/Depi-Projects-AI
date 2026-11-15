import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const artifactDir = 'C:/Users/Youssef Mohamed/.gemini/antigravity/brain/52ed6862-6062-4f6c-acb6-27b6592500a9';
const liveUrl = 'https://eduflow-ai-brand.vercel.app';

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

try {
  // 1. Admin AR Desktop
  const contextDesktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pageDesktop = await contextDesktop.newPage();
  await pageDesktop.goto(`${liveUrl}#overview`);
  await pageDesktop.waitForSelector('.hero-banner.compact-hero');
  await pageDesktop.waitForTimeout(500);
  await pageDesktop.screenshot({ path: resolve(artifactDir, '13-live-admin-ar.png') });

  // 2. Secretary AR Desktop (showing new Financial Pulse)
  await pageDesktop.selectOption('.demo-toolbar select', 'secretary');
  await pageDesktop.waitForTimeout(500);
  await pageDesktop.screenshot({ path: resolve(artifactDir, '14-live-secretary-pulse-ar.png') });

  // 3. Teacher AR Desktop
  await pageDesktop.selectOption('.demo-toolbar select', 'teacher');
  await pageDesktop.waitForTimeout(500);
  await pageDesktop.screenshot({ path: resolve(artifactDir, '15-live-teacher-ar.png') });

  // 4. Tablet 768px (iPad portrait showing full width + mobile drawer)
  const contextTablet = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  const pageTablet = await contextTablet.newPage();
  await pageTablet.goto(`${liveUrl}#overview`);
  await pageTablet.waitForSelector('.hero-banner.compact-hero');
  await pageTablet.waitForTimeout(500);
  await pageTablet.screenshot({ path: resolve(artifactDir, '16-live-tablet-768px.png') });

  console.log('Screenshots saved to artifact directory successfully.');
} finally {
  await browser.close();
}
