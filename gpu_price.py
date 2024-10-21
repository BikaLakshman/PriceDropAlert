import requests
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import os
import time

# URL of the product page (replace with actual product URL)
URL = 'https://www.bestbuy.com/site/searchpage.jsp?st=4090+rtx&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys'

# Headers (for requests)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.bestbuy.com",
    "Connection": "keep-alive"
}

# Desired price threshold (you can change this)
TARGET_PRICE = 800.00

# Email credentials
SENDER_EMAIL = os.getenv("vanbro34@gmail.com")
RECEIVER_EMAIL = os.getenv("lakshmansingh908@gmail.com")
EMAIL_PASSWORD = os.getenv("Ashok505")

# Path to the Edge WebDriver executable
EDGEDRIVER_PATH = r'C:\\Users\\laksh\\Downloads\\edgedriver_win32\\msedgedriver.exe'

def get_gpu_price_requests():
    """Fetches the current GPU price using requests and BeautifulSoup."""
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the price (modify the class or id as per the website structure)
    price_element = soup.find("span", {"class": "priceView-hero-price"})
    
    if price_element:
        price = float(price_element.text.replace("$", "").replace(",", ""))
        return price
    else:
        print("Failed to find the price using requests.")
        return None


def get_gpu_price_selenium():
    """Fetches the current GPU price using Selenium."""
    service = Service(EDGEDRIVER_PATH)
    options = webdriver.EdgeOptions()
    #options.add_argument('--headless')  # Run Edge in headless mode (no GUI)
    options.add_argument("--use-gl-angle")
    options.add_argument("--disable-gpu-process-for-dx12-vulkan-info-collection")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    options.add_argument("--use-gl=swiftshader")
    options.add_argument('--log-level=3')  # Reduces log output verbosity


    driver = webdriver.Edge(service=service, options=options)
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 10)
        price_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "priceView-hero-price")))
        price_text = price_element.find_element(By.TAG_NAME, "span").text

        # Find the price element using Selenium (adjust the selector as needed)
        price_element = driver.find_element(By.CLASS_NAME, "priceView-hero-price")
        price_text = price_element.find_element(By.TAG_NAME, "span").text
        price = float(price_text.replace("$", "").replace(",", ""))
        return price

    except Exception as e:
        print(f"Error while scraping with Selenium: {e}")
        return None

    finally:
        driver.quit()


def send_email(price):
    """Sends an email notification if the price drops below the target."""
    subject = "Price Drop Alert: GPU Available Below Target Price!"
    body = f"The GPU price has dropped to ${price}! Check the product here: {URL}"

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)


def check_price(use_selenium=True):
    """Check the current price using either Selenium or requests and send an email if it's below the target."""
    if use_selenium:
        current_price = get_gpu_price_selenium()
    else:
        current_price = get_gpu_price_requests()
    
    if current_price is not None:
        print(f"Current price: ${current_price}")
        if current_price < TARGET_PRICE:
            print("Sending email alert...")
            send_email(current_price)
        else:
            print(f"The GPU price is above your target of ${TARGET_PRICE}.")
    else:
        print("Failed to retrieve the GPU price.")


# Main function to check the price
if __name__ == '__main__':
    # Set to True if you want to use Selenium, or False for using requests
    check_price(use_selenium=True)
