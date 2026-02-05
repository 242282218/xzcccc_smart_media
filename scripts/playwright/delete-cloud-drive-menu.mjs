import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3001/";
const HEADLESS = process.env.HEADLESS !== "0";
const OUTPUT_DIR = path.resolve(process.cwd(), "output", "playwright");
const TIMEOUT = Number(process.env.PW_TIMEOUT_MS ?? 10000);
const KEEP_OPEN_SECONDS = Number(process.env.KEEP_OPEN_SECONDS ?? 30);
const LOGIN_USER = process.env.LOGIN_USER ?? "";
const LOGIN_PASS = process.env.LOGIN_PASS ?? "";
const USE_SYSTEM_PROFILE =
  process.env.USE_SYSTEM_PROFILE === "0" ? false : !HEADLESS;
const WAIT_FOR_MANUAL_LOGIN_SECONDS = Number(process.env.WAIT_FOR_MANUAL_LOGIN_SECONDS ?? 90);

function getSystemProfile() {
  const home = process.env.USERPROFILE ?? process.env.HOME ?? "";
  const edge = path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data");
  const chrome = path.join(home, "AppData", "Local", "Google", "Chrome", "User Data");
  if (fs.existsSync(edge)) return { dir: edge, channel: "msedge" };
  if (fs.existsSync(chrome)) return { dir: chrome, channel: "chrome" };
  return null;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

async function clickIfVisible(locator) {
  if ((await locator.count()) === 0) return false;
  if (!(await locator.first().isVisible())) return false;
  await locator.first().click();
  return true;
}

async function confirmDelete(page) {
  const dialog = page.getByRole("dialog");
  if ((await dialog.count()) === 0) return false;
  const confirmBtn = dialog.getByRole("button", { name: /^(确定|删除)$/ });
  if ((await confirmBtn.count()) === 0) return false;
  await confirmBtn.first().click();
  return true;
}

async function deleteViaContextMenu(page, menuItem) {
  await menuItem.click({ button: "right" });
  const menuDelete = page.getByRole("menuitem", { name: /删除|移除/ });
  if (await clickIfVisible(menuDelete)) return true;
  const fallbackDelete = page.getByText(/删除|移除/, { exact: false });
  if (await clickIfVisible(fallbackDelete)) return true;
  return false;
}

async function deleteViaInlineButton(menuItem) {
  const row = menuItem.locator("..");
  const buttonByLabel = row.getByRole("button", { name: /删除|移除/ });
  if (await clickIfVisible(buttonByLabel)) return true;
  const iconButton = row.locator(
    "button[title*='删除'], button[aria-label*='删除'], button[title*='移除'], button[aria-label*='移除']"
  );
  if (await clickIfVisible(iconButton)) return true;
  return false;
}

async function expandAllSidebarGroups(sidebar) {
  const expanders = sidebar.locator("[aria-expanded='false']");
  const count = await expanders.count();
  for (let i = 0; i < count; i += 1) {
    try {
      await expanders.nth(i).click();
    } catch {
      // ignore individual failures; we just try to expand likely groups
    }
  }
}

async function tryAutoLogin(page) {
  const passwordInput = page.locator("input[type='password']");
  if ((await passwordInput.count()) === 0) return false;
  if (!(await passwordInput.first().isVisible())) return false;
  if (!LOGIN_USER || !LOGIN_PASS) {
    console.warn("检测到登录页，但未提供 LOGIN_USER / LOGIN_PASS，跳过自动登录");
    return "manual";
  }
  const userInput =
    page.locator("input[type='text'], input[type='email'], input[name*='user'], input[name*='account']")
      .first();
  await userInput.fill(LOGIN_USER);
  await passwordInput.first().fill(LOGIN_PASS);
  const submitBtn = page.getByRole("button", { name: /登录|登\s*录|sign in|login/i });
  if (await clickIfVisible(submitBtn)) return true;
  await page.keyboard.press("Enter");
  return true;
}

(async () => {
  ensureDir(OUTPUT_DIR);
  let browser;
  let context;
  const systemProfile = USE_SYSTEM_PROFILE ? getSystemProfile() : null;
  if (systemProfile) {
    context = await chromium.launchPersistentContext(systemProfile.dir, {
      headless: HEADLESS,
      channel: systemProfile.channel,
    });
  } else {
    browser = await chromium.launch({ headless: HEADLESS });
    context = await browser.newContext();
  }
  const page = await context.newPage();
  page.setDefaultTimeout(TIMEOUT);

  try {
    await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle");
    const loginResult = await tryAutoLogin(page);
    if (loginResult === "manual" && !HEADLESS && WAIT_FOR_MANUAL_LOGIN_SECONDS > 0) {
      console.log(`请在 ${WAIT_FOR_MANUAL_LOGIN_SECONDS}s 内完成登录，脚本将自动继续`);
      const start = Date.now();
      while (Date.now() - start < WAIT_FOR_MANUAL_LOGIN_SECONDS * 1000) {
        const hasMenu = (await page.getByText(/云盘管理/).count()) > 0;
        if (hasMenu) break;
        const passwordVisible =
          (await page.locator("input[type='password']").count()) > 0 &&
          (await page.locator("input[type='password']").first().isVisible());
        if (!passwordVisible) break;
        await page.waitForTimeout(1000);
      }
    }
    await page.waitForLoadState("networkidle");

    await page.screenshot({ path: path.join(OUTPUT_DIR, "before-delete.png"), fullPage: true });

    const sidebar = page.locator("aside, nav, [role='navigation']").first();
    if ((await sidebar.count()) > 0) {
      await expandAllSidebarGroups(sidebar);
    }

    const menuItem =
      (await sidebar.getByRole("menuitem", { name: /云盘管理/ }).count())
        ? sidebar.getByRole("menuitem", { name: /云盘管理/ }).first()
        : (await sidebar.getByRole("link", { name: /云盘管理/ }).count())
          ? sidebar.getByRole("link", { name: /云盘管理/ }).first()
          : (await sidebar.getByText(/云盘管理/).count())
            ? sidebar.getByText(/云盘管理/).first()
            : page.getByText(/云盘管理/).first();

    if ((await menuItem.count()) === 0 || !(await menuItem.isVisible())) {
      throw new Error("未找到侧边栏菜单项：云盘管理");
    }

    let deleted = false;
    deleted = await deleteViaContextMenu(page, menuItem);
    if (!deleted) {
      deleted = await deleteViaInlineButton(menuItem);
    }

    if (!deleted) {
      throw new Error("未找到删除入口（右键菜单或行内删除按钮）");
    }

    await confirmDelete(page);

    // 验证菜单项已消失
    await page.waitForTimeout(500);
    const stillExists = (await page.getByText("云盘管理", { exact: true }).count()) > 0;
    if (stillExists) {
      throw new Error("删除后仍能看到“云盘管理”菜单项");
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, "delete-cloud-drive-menu-success.png"), fullPage: true });
    if (!HEADLESS && KEEP_OPEN_SECONDS > 0) {
      console.log(`已删除“云盘管理”，保留窗口 ${KEEP_OPEN_SECONDS}s 供检查`);
      await page.waitForTimeout(KEEP_OPEN_SECONDS * 1000);
    }
    await context.close();
    if (browser) await browser.close();
    process.exit(0);
  } catch (error) {
    await page.screenshot({ path: path.join(OUTPUT_DIR, "delete-cloud-drive-menu-failure.png"), fullPage: true });
    await context.close();
    if (browser) await browser.close();
    console.error(error);
    process.exit(1);
  }
})();
