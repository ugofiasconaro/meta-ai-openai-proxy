# Author: Ugo Fiasconaro
# grab_cookies.py

import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

SESSION_FILE = os.getenv("SESSION_FILE_PATH", "./data/session_data.json")
METAAI_USERNAME = os.getenv("METAAI_USERNAME", "fiascojob")


def load_session_data():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}

def save_session_data(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_selenium_cookies(webdriver_url):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode if needed
    driver = webdriver.Remote(command_executor=webdriver_url, options=options)

    try:
        # Load existing cookies if available
        session_data = load_session_data()
        if 'cookies' in session_data and session_data['cookies']:
            driver.get("https://www.meta.ai/") # Navigate to a domain before adding cookies
            for cookie_name, cookie_value in session_data['cookies'].items():
                if cookie_value:
                    driver.add_cookie({'name': cookie_name, 'value': cookie_value, 'domain': '.meta.ai'})
            driver.refresh() # Refresh to apply cookies
            print("Loaded existing cookies into Selenium.")

        driver.get("https://www.meta.ai/")
        print("\n🚀 Browser aperto. Effettua il login su Meta AI se richiesto. Attendo il caricamento della pagina...")

        # Wait for the page to load after manual login or initial load
        # We'll wait for an element that is typically present after a successful login on Meta AI.
        # A common element could be a specific chat input field or a main content area.
        # For now, let's assume a common element like a div with a specific role or class.
        # If this fails, it might need to be adjusted based on the actual Meta AI page structure.
        utenteLoggato = False
        need2SaveCookie = False
        try:
            
            element_to_click = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//a[not(contains(., "Ctrl"))]""")) # Example: waiting for the main content area
            )
            print("Pagina caricata e elemento principale trovato e cliccato.")
            element_to_click.click()
            
            input("Premi INVIO quando hai concluso di effettuare il login.")
            need2SaveCookie = True

            

        except Exception as e:
            if str(driver.page_source).__contains__(f'''"username":"{METAAI_USERNAME}"'''):
                print("L'utente già loggato. Tutto OK")
                utenteLoggato = True
                need2SaveCookie = False
            else:
                print(f"Errore durante l'attesa del caricamento della pagina: {e}")
            
        
        

        # Extract cookies
        cookies = driver.get_cookies()
        extracted_cookies = {}
        for cookie in cookies:
            extracted_cookies[cookie['name']] = cookie['value']

        # Extract fb_dtsg and User-Agent (assuming they are available after login)
        # This might require more specific logic depending on how Meta AI loads these
        # For now, we'll try to get them from the network requests if possible, or prompt the user.
        # A more robust solution would involve intercepting network requests.
        user_agent = driver.execute_script("return navigator.userAgent")
        fb_dtsg = extracted_cookies.get('fb_dtsg', '') # Try to get from cookies first

        # If fb_dtsg is not in cookies, it's likely in the page source or a network request.
        # A more robust solution would involve intercepting network requests or parsing specific script tags.
        # For now, we rely on it being present in the extracted cookies.

        return user_agent, fb_dtsg, extracted_cookies, utenteLoggato, need2SaveCookie


    finally:
        driver.quit()

def main():
    print("🔧 Configurazione sessione Meta AI con Selenium\n")

    webdriver_url = os.getenv("WEBDRIVER_URL", "http://127.0.0.1:4444") # Selenium Grid/WebDriver URL
    print(f"Connessione a Selenium WebDriver su {webdriver_url}")

    user_agent, fb_dtsg, collected_cookies, utenteLoggato, need2SaveCookie = get_selenium_cookies(webdriver_url)


    session_data = {
        "user_agent": user_agent,
        "fb_dtsg": fb_dtsg,
        "cookies": collected_cookies,
    }
    if need2SaveCookie == True:
        save_session_data(session_data)
        print("\n✅ Dati sessione salvati in session_data.json")
    elif utenteLoggato == True:
        print("\n✅ Dati sessione validi già presenti in session_data.json")
    else :
        print("\n❌ Non è stato possibile salvare i dati sessione.")




if __name__ == "__main__":
    main()