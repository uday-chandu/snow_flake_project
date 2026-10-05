import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import pandas as pd



def scrape_disney_selenium():
# 1. Configure Chrome options to reduce anti-bot flags
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment if you want to run without opening a UI window
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize the WebDriver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    url = "https://disneycruise.disney.go.com/en-in/"
    print(f"Opening target site: {url}")
    driver.get(url)

    # Set a robust timeout threshold for dynamic structures
    wait = WebDriverWait(driver, 15)
    driver.find_element(By.XPATH, "//div/span[text()='Departing from']").click()
    driver.find_element(By.XPATH, "//button[contains(., 'Port Canaveral, Florida')]").click()
    driver.find_element(By.XPATH,"//button[contains(., 'View Dates')]").click()
        
    # 1. Get initial scroll height
    def scroll_page(sleep_time):
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new cards to load asynchronously
            time.sleep(sleep_time) 
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # If heights are the same, the bottom of the page was reached
            if new_height == last_height:
                break
                
            last_height = new_height
    scroll_page(sleep_time=10.0)



    scraped_data=[]
    # Fetch all the parent product cards first
    all_cards = driver.find_elements(By.XPATH, "//dcl-product-card")

    for index, card in enumerate(all_cards, start=1):
        print(f"\n--- Processing Card {index}/{len(all_cards)} ---")
        
        # 1. Fetch Title (Relative to the current card)
        title = card.find_element(By.XPATH, ".//div/div[1]/div[2]/div[2]/div[2]/h2").text
        print('Title: ', title)
        
        # 2. Click to reveal hidden cards
        try:
            show_hidden_btn = card.find_element(By.XPATH, ".//div/div[1]/div[2]/div[2]/div[3]/div/div[3]/a/span")
            show_hidden_btn.click()
            scroll_page(sleep_time=2.5)  # Your custom scroll function
        except NoSuchElementException:
            pass # Button might not exist if all items are already visible
            
        # 3. Fetch all child sailing cards inside this specific product card
        sailing_cards = card.find_elements(By.XPATH, ".//div/div[2]/div/div[2]/dcl-sailing-card")
        print('TOTAL sailing cards: ', len(sailing_cards))
        
        # 4. Loop through each sub-sailing card directly
        for s_card in sailing_cards:
            # Relative paths inside the sailing card container
            date_range = s_card.find_element(By.XPATH, ".//div/div[1]/dcl-sailing-card-date//span[1]").text
            week_range = s_card.find_element(By.XPATH, ".//div/div[1]/dcl-sailing-card-date//span[2]").text
            # print(f"Date: {date_range} ({week_range})")
            
            # Helper function to prevent script crashes if a certain room tier is sold out
            def get_price(li_index):
                try:
                    xpath = f".//div/div[2]/div[1]/dcl-sailing-card-pricing/div/ul/li[{li_index}]/a/div/div[1]/div/div/wdpr-price"
                    return s_card.find_element(By.XPATH, xpath).text
                except NoSuchElementException:
                    return "N/A"

            interior = get_price(1)
            ocean_view = get_price(2)
            balcony = get_price(3)
            suite = get_price(4) # Fixed index bug (original script had 3 for both balcony and suite)
            
            # print(f"  - Interior: {interior}")
            # print(f"  - Ocean View: {ocean_view}")
            # print(f"  - Balcony: {balcony}")
            # print(f"  - Suite: {suite}")
            
            # 5. Extract URL (Assuming it's the anchor tag wrapping the price buttons)
            try:
                url = s_card.find_element(By.XPATH, ".//div/div[2]/div[1]/dcl-sailing-card-pricing/div/ul/li[1]/a").get_attribute("href")
                # print(f"  - URL: {url}")
            except NoSuchElementException:
                pass
                # print("  - URL: Not found")

            scraped_data.append({
                "Title": title,
                "Date Range": date_range,
                "Week Range": week_range,
                "Interior Price": interior,
                "Ocean View Price": ocean_view,
                "Balcony Price": balcony,
                "Suite Price": suite,
                "URL": url
            })
    df=pd.DataFrame(scraped_data).drop_duplicates()
    df.to_csv('disney_data.csv',index=False)


if __name__ == "__main__":
    scrape_disney_selenium()
