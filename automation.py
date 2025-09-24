import asyncio
from playwright.async_api import async_playwright

EMAIL = "likepeas@gmail.com"
PASSWORD = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

async def click_grader_grade(page, grader: str, grade: str) -> bool:
    try:
        print(f"🎯 Selecting: {grader} {grade}")
        popup = page.locator("div[data-testid='card-pops']").first
        await popup.scroll_into_view_if_needed()
        await page.wait_for_timeout(900)

        header = page.get_by_text(f"{grader} population", exact=True)
        if not await header.count():
            print(f"❌ Header '{grader} population' not found")
            return False

        wrapper = header.locator("xpath=..")
        buttons = wrapper.locator("button")

        button_count = await buttons.count()
        for i in range(button_count):
            btn = buttons.nth(i)
            grade_span = btn.locator("span").first
            text = await grade_span.text_content()
            text = text.strip() if text else ""

            if text == grade:
                await btn.scroll_into_view_if_needed()
                await btn.click(timeout=2000)
                print(f"✅ Clicked: {grader} {grade}")
                await page.wait_for_timeout(500)
                return True

        print(f"❌ Exact grade '{grade}' not found under '{grader}'.")
    except Exception as e:
        print(f"❌ Error selecting {grader} {grade}: {e}")

    return False

async def fetch_prices(page, num_sales=4):
    print("💵 Waiting for recent sales to load...")
    await page.wait_for_timeout(3000)

    prices = []
    blocks = page.locator("div.MuiTypography-body1.css-vxna0y")

    block_count = await blocks.count()
    for i in range(block_count):
        try:
            price_span = blocks.nth(i).locator("span[class*='css-16tlq5a']")
            price_text = await price_span.inner_text()
            match = re.search(r"\$([0-9\s,\.]+)", price_text)
            if match:
                price_str = match.group(1).replace(" ", "").replace("\u202f", "").replace(",", "")
                price = float(price_str)
                prices.append(price)
            if len(prices) >= num_sales:
                break
        except Exception as e:
            print(f"⚠️ Skipping sale {i+1}: {e}")
    return prices

async def perform_login_if_needed(page) -> bool:
    try:
        login_btn = page.locator("button:has-text('Log in')").first
        if await login_btn.count():
            print("🔐 Login button detected — clicking it")
            await login_btn.click()
            await page.wait_for_timeout(1000)

            email_input = page.locator("input[type='email'], input[name='email'], input#email").first
            if await email_input.count():
                await email_input.fill(EMAIL)
                print("✅ Filled email")
            else:
                print("❌ Could not locate email input")
                return False

            password_input = page.locator("input[type='password'], input[name='password'], input#password").first
            if await password_input.count():
                await password_input.fill(PASSWORD)
                print("✅ Filled password")
            else:
                print("❌ Could not locate password input")
                return False

            submit_btn = page.locator("button:has-text('Log in'), button:has-text('Sign in'), button[type='submit']").first
            if await submit_btn.count():
                await submit_btn.click()
                await page.wait_for_load_state("networkidle", timeout=10000)
                print("🔓 Login successful")
                return True
            else:
                print("⚠️ Could not find submit button")
                return False
        else:
            return True
    except Exception as e:
        print(f"⚠️ Error during login: {e}")
        return False

async def process_rows_async(all_values, start_row, sheet):
    num_rows = len(all_values)

    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(
            headless=True,  # Run in headless mode
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        )
        
        page = await context.new_page()

        print(f"🚀 Processing rows {start_row}..{num_rows}")

        for row in range(start_row - 1, num_rows):
            rnum = row + 1
            try:
                row_vals = all_values[row]
                url = row_vals[5] if len(row_vals) > 5 else ""
                grader = row_vals[6] if len(row_vals) > 6 else ""
                fake_grade = row_vals[7] if len(row_vals) > 7 else ""

                if not url or not grader or not fake_grade:
                    print(f"⚠️ Skipping row {rnum}: Missing required data")
                    continue

                grade = fake_grade[:2] if len(fake_grade) > 3 else fake_grade
                print(f"\n🔁 Processing row {rnum}: {grader} {grade}")

                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(2000)

                button = page.locator("button.MuiButtonBase-root.css-1ege7gw").first
                await button.wait_for(state="visible", timeout=5000)
                await button.click()
                await page.wait_for_timeout(2000)

                await perform_login_if_needed(page)

                success = await click_grader_grade(page, grader, grade)
                await page.wait_for_timeout(1000)

                if success:
                    prices = await fetch_prices(page, 4)
                    if prices:
                        avg = sum(prices) / len(prices)
                        for i, price in enumerate(prices[:4]):
                            try:
                                sheet.update_cell(rnum, 12 + i, price)
                            except Exception as e:
                                print(f"⚠️ Failed to update cell for row {rnum}, col {12+i}: {e}")
                        try:
                            sheet.update_cell(rnum, 16, avg)
                        except Exception as e:
                            print(f"⚠️ Failed to update avg cell for row {rnum}: {e}")
                        print(f"✅ Updated row {rnum} with prices and average.")
                    else:
                        print(f"❌ No prices found for row {rnum}.")
                else:
                    print(f"❌ Could not select grader/grade for row {rnum}.")

                await page.wait_for_timeout(1200)

            except Exception as e:
                print(f"❌ Error processing row {rnum}: {e}")
                continue

        await browser.close()
        print("🎉 All rows processed. Browser closed.")