# ========== CUSTOMIZE THESE ==========
USERNAME = "O-0108_5"
PASSWORD = "megvJb"
# ====================================

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pytz
from datetime import datetime, timedelta

# ---------- AUTO DATE CALCULATION (Jakarta Time) ----------
jakarta_tz = pytz.timezone('Asia/Jakarta')
today = datetime.now(jakarta_tz)

end_date = today - timedelta(days=2)
start_date = datetime(today.year, today.month, 1, tzinfo=jakarta_tz)

if end_date < start_date:
    if today.month == 1:
        start_date = datetime(today.year - 1, 12, 1, tzinfo=jakarta_tz)
    else:
        start_date = datetime(today.year, today.month - 1, 1, tzinfo=jakarta_tz)

START_DATE = start_date.strftime("%d-%m-%Y")
END_DATE   = end_date.strftime("%d-%m-%Y")
print(f"Auto date range (Jakarta time): {START_DATE} → {END_DATE}")

# ---------- START BROWSER ----------
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # ---------- LOGIN ----------
    driver.get("https://b2b.alfamidiku.com/login.php")
    time.sleep(2)
    driver.find_element(By.NAME, "uname").send_keys(USERNAME)
    driver.find_element(By.NAME, "upass").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
    time.sleep(3)

    # ---------- CLOSE POPUP ----------
    try:
        wait = WebDriverWait(driver, 5)
        overlay = wait.until(EC.presence_of_element_located((By.ID, "promoOverlay")))
        if overlay.is_displayed():
            driver.find_element(By.CLASS_NAME, "close-btn").click()
            print("Promo popup closed.")
    except:
        print("No popup.")
    time.sleep(3)

    # ---------- OPEN Dashboard & Modular ----------
    wait = WebDriverWait(driver, 20)
    laporan_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Laporan')]")))
    actions = ActionChains(driver)
    actions.move_to_element(laporan_menu).perform()
    print("Hovered over Laporan menu.")
    time.sleep(2)

    dashboard_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='get_laporan_new_premium.php']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", dashboard_link)
    time.sleep(0.5)
    try:
        dashboard_link.click()
        print("Clicked Dashboard & Modular link.")
    except:
        driver.execute_script("arguments[0].click();", dashboard_link)
        print("JavaScript click executed.")

    # ---------- SWITCH TO NEW TAB ----------
    time.sleep(3)
    original_tab = driver.current_window_handle
    new_tab = None
    for tab in driver.window_handles:
        if tab != original_tab:
            new_tab = tab
            break
    if new_tab is None:
        raise Exception("New tab did not open!")
    driver.switch_to.window(new_tab)
    print("Switched to new tab.")
    
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "switch-dashboard")))
    print("Page loaded (switch-dashboard found).")

    # ---------- CLICK "Report Modular" ----------
    try:
        modular_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Report Modular"))
        )
        modular_link.click()
        print("Clicked 'Report Modular' using link text.")
    except:
        try:
            modular_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.gold-font[href='performancesales-modular']"))
            )
            modular_link.click()
            print("Clicked 'Report Modular' using CSS selector.")
        except:
            print("Could not click link, navigating directly to performancesales-modular")
            driver.get("https://b2b.alfamidiku.com/performancesales-modular")
    time.sleep(4)

    # ---------- SELECT "Performance by Item by Branch by Day" (value="5") ----------
    wait = WebDriverWait(driver, 15)
    jenis_dropdown = wait.until(EC.presence_of_element_located((By.ID, "jenis_performace")))
    jenis_performance = Select(jenis_dropdown)
    jenis_performance.select_by_value("5")
    print("Selected 'Performance by Item by Branch by Day'.")
    time.sleep(3)

    # ---------- SET DATE RANGE (branch version) ----------
    start_input = driver.find_element(By.ID, "periode_awal_bybranch")
    driver.execute_script("arguments[0].removeAttribute('readonly')", start_input)
    start_input.clear()
    start_input.send_keys(START_DATE)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", start_input)

    end_input = driver.find_element(By.ID, "periode_akhir_bybranch")
    driver.execute_script("arguments[0].removeAttribute('readonly')", end_input)
    end_input.clear()
    end_input.send_keys(END_DATE)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", end_input)
    print(f"Periode set: {START_DATE} to {END_DATE}")

    # ---------- LOOP THROUGH UNITS ----------
    units = [("v", "Value"), ("q", "Qty")]

    for unit_value, unit_name in units:
        print(f"\n{'='*60}")
        print(f"📥 Processing Unit: {unit_name}")
        print('='*60)

        unit_select = Select(driver.find_element(By.ID, "unit-filter-report-modular-5"))
        unit_select.select_by_value(unit_value)
        print(f"Unit set to {unit_name}.")
        time.sleep(1)

        download_btn = driver.find_element(By.ID, "download-xls")
        download_btn.click()
        print(f"   ⏳ Clicked download for Branch report | {unit_name}")

        try:
            time.sleep(1)
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   ⚠️ Alert: {alert_text}")
            alert.accept()
        except:
            print(f"   ✅ No alert – download triggered.")
        time.sleep(5)

    print("\n🎉 Alfamidi Branch reports done! Check your email.")

except Exception as e:
    print(f"An error occurred: {e}")
    try:
        driver.save_screenshot("error_screenshot.png")
        with open("page_source.html", "w") as f:
            f.write(driver.page_source)
    except:
        pass
    time.sleep(30)

finally:
    driver.quit()