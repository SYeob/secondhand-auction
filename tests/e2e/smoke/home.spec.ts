import { test, expect } from "@playwright/test";

test.describe("홈 화면 Smoke Test", () => {
  test("TS-SMOKE-001 홈 화면이 정상적으로 표시된다", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator("body")).toBeVisible();

    const title = await page.title();
    expect(title.trim().length).toBeGreaterThan(0);

    await expect(page.locator("h1").first()).toBeVisible();
  });
});
