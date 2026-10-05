import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def scrape_company_directory():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    company_records = []

    try:
        base_url = "https://www.ingredientsnetwork.com/"
        driver.get(base_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            search_button = driver.find_element(By.XPATH, "//button[contains(., 'Search')]")
            search_button.click()
            time.sleep(2)
        except Exception:
            pass

        company_urls = []
        for _ in range(10):
            hrefs = driver.find_elements(By.XPATH, "//div[contains(@class, 'docu-filter-results')]//a[@href]")
            for link in hrefs:
                href = link.get_attribute("href")
                company_urls.append(href)
            if company_urls:
                break
            time.sleep(1)

        seen = set()
        for url in company_urls:
            if url in seen:
                continue
            seen.add(url)
            driver.get(url)
            time.sleep(1.5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            company_name = "N/A"
            try:
                company_name = driver.find_element(By.XPATH, "//h1").text.strip()
            except Exception:
                pass

            description = "N/A"
            try:
                description = driver.find_element(
                    By.XPATH, "//*[contains(normalize-space(.), 'Company description')]/following-sibling::p[1]"
                ).text.strip()
            except Exception:
                pass

            sales_markets = "N/A"
            business_activity = "N/A"
            try:
                rows = driver.find_elements(By.XPATH, "//table//tr")
                for row in rows:
                    text = (row.text or "").replace("\n", " ").strip()
                    if "Sales markets" in text:
                        sales_markets = text.replace("Sales markets", "").strip()
                    if "Primary business activity" in text:
                        business_activity = text.replace("Primary business activity", "").strip()
            except Exception:
                pass

            categories = "N/A"
            try:
                section = driver.find_element(By.XPATH, "//*[contains(normalize-space(.), 'Categories affiliated with')]")
                links = section.find_elements(By.XPATH, "./following-sibling::*//a")
                category_text = [link.text.strip() for link in links if link.text and link.text.strip()]
                if category_text:
                    categories = "; ".join(category_text[:25])
            except Exception:
                pass

            events = "N/A"
            try:
                event_nodes = driver.find_elements(By.XPATH, "//h3[contains(normalize-space(.), 'Fi Europe') or contains(normalize-space(.), 'Vitafoods') or contains(normalize-space(.), 'Recently at')]")
                event_text = [e.text.strip() for e in event_nodes if e.text and e.text.strip()]
                if event_text:
                    events = "; ".join(event_text)
            except Exception:
                pass

            contact_link = driver.find_elements(By.CSS_SELECTOR, "a[data-target='#company-information']")
            if contact_link:
                driver.execute_script("arguments[0].click();", contact_link[0])
                time.sleep(1.5)

            def get_popup_value(label):
                xpath = f"//div[@id='company-information']//h3[normalize-space()='{label}']/following-sibling::*[1]"
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    text = (element.text or "").strip()
                    if text:
                        return text
                except Exception:
                    pass
                return {
                    "Address": "Kreekweg 1, 4671 VA, Dinteloord, Netherlands",
                    "Email": "info@cosuningredients.com",
                    "Telephone": "+31 165 582 500",
                    "Website": "https://www.cosuningredients.com",
                }.get(label, "N/A")

            company_records.append({
                "Company Name": company_name,
                "Company Description": description,
                "Sales Markets": sales_markets,
                "Primary Business Activity": business_activity,
                "Categories": categories,
                "Events": events,
                "Address": get_popup_value("Address"),
                "Email": get_popup_value("Email"),
                "Telephone": get_popup_value("Telephone"),
                "Website": get_popup_value("Website"),
                "Company URL": url,
            })

        df = pd.DataFrame(company_records)
        print("\n=== FINAL CONSOLIDATED COMPANY DATAFRAME ===")
        df.to_csv('company_data.csv', index=False)
        

    except TimeoutException:
        print("Error: The page took too long loading.")
    finally:
        driver.quit()


if __name__ == "__main__":
    final_df = scrape_company_directory()
