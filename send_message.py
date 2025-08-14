# Author: Ugo Fiasconaro
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List

import json
import asyncio
from re import A
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from threading import Thread
from markdownify import markdownify as md

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lock condiviso per garantire l'elaborazione sequenziale
processing_lock_request = asyncio.Lock()
processing_lock_sendfunc = asyncio.Lock()

SESSION_FILE = os.getenv("SESSION_FILE_PATH", "./data/session_data.json")
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "false")
METAAI_USERNAME = os.getenv("METAAI_USERNAME", "fiascojob")


class ModelData(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "user"

class ModelsResponse(BaseModel):
    data: List[ModelData]

def load_session_data():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}

def save_session_data(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def verify_selenium_instance(webdriver_url, session_data, driver):

    if driver == None:

        # Initialize driver once
        options = webdriver.ChromeOptions()
        if os.getenv("SELENIUM_HEADLESS", "true").lower() == "true":
            options.add_argument("--headless=new")
            options.add_experimental_option("detach", True)
        

        driver = webdriver.Remote(command_executor=webdriver_url, options=options)
        driver.set_page_load_timeout(120)
        driver.set_script_timeout(120)

        session_data = load_session_data()
        if 'cookies' in session_data and session_data['cookies']:
            driver.get("https://www.meta.ai/") # Navigate to a domain before adding cookies
            for cookie_name, cookie_value in session_data['cookies'].items():
                if cookie_value:
                    driver.add_cookie({'name': cookie_name, 'value': cookie_value, 'domain': '.meta.ai'})
            driver.refresh() # Refresh to apply cookies
            print("Loaded existing cookies into Selenium.")


        try:


            driver.get("https://www.meta.ai/")
            print("\nNavigazione su Meta AI. Attendo il primo caricamento della pagina...")

            try:
                WebDriverWait(driver, 60).until(
                    EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div/i""")) # Waiting for the main content area
                )
                
                if str(driver.page_source).__contains__(f'''"username":"{METAAI_USERNAME}"'''):
                    print("Pagina caricata correttamente e elemento principale trovato.")
                    return driver

            except Exception as e:
                print(f"Errore durante l'attesa del caricamento della pagina: {e}")
                print("Assicurati di aver effettuato il login e che la pagina sia completamente caricata.")
                return None


            

        finally:
            pass
    else:
        return driver
        #    driver.quit()




async def send_message_with_selenium (message, driver, previous_chatID=""):

    
    if driver != None:
        if previous_chatID != "":
            driver.get(f"https://www.meta.ai/prompt/{previous_chatID}")
            
            #if True:
            try:
                # WebDriverWait(driver, 120).until(
                #     EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']"""))
                # )
                WebDriverWait(driver, 40).until(
                    EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='textbox']"""))
                )

                if DEBUG_ENABLED.lower() == "true":
                    print("Check Visibility of Textbox to write message")


                input_field = WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='textbox']"""))
                )
                if DEBUG_ENABLED.lower() == "true":
                    print ("Elem in ChatID 1")
                numOfElements = input_field.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='textbox']""").__len__()
                if DEBUG_ENABLED.lower() == "true":
                    print ("Elem in ChatID 2")
                if numOfElements == 1:
                    numCheckBotMsgsBefore = driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']""").__len__()
                    if DEBUG_ENABLED.lower() == "true":
                        print ("Elem in ChatID 3")
                    numIcons = driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//span[contains(@class, 'html-span')]/div[@role='button' and @id != '']""").__len__()
                    if DEBUG_ENABLED.lower() == "true":
                        print ("Elem in ChatID 4")

                    input_field.send_keys(message)
                    input_field.send_keys(Keys.RETURN)

                    
                    wait = WebDriverWait(driver, 40)
                    alliconsBot = wait.until(
                             lambda driver: (
                                lambda els: els[numIcons] if len(els) >= numIcons + 1 and els[numIcons].is_displayed() else False
                                )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//span[contains(@class, 'html-span')]/div[@role='button' and @id != '']"""))
                            )
                    if DEBUG_ENABLED.lower() == "true":        
                        print ("Elem in ChatID 5")

           
                    #//*[starts-with(@id, 'mount_0_0_')]//div[@aria-disabled='true']
                    

                    WebDriverWait(driver, 40).until(
                            EC.presence_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@aria-disabled='true']"""))
                        )
                    if DEBUG_ENABLED.lower() == "true":    
                        print ("Elem in ChatID 6")


                    wait = WebDriverWait(driver, 10)
                    allBotMsg = wait.until(
                             lambda driver: (
                                lambda els: els[numCheckBotMsgsBefore] if len(els) >= numCheckBotMsgsBefore + 1 and els[numCheckBotMsgsBefore].is_displayed() else False
                                )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']"""))
                            )
                    if DEBUG_ENABLED.lower() == "true":
                        print ("Elem in ChatID 7")
                        

                    
                    return json.dumps({"message": md(allBotMsg.get_attribute('innerHTML'), strip=['style', 'script'], skip=['style', 'script'], wrap=False).replace("\t", "    "), "prevChatID": driver.current_url.split("prompt/")[-1]}, ensure_ascii=False)
                    #return {"message": json.dumps({md(allBotMsg.get_attribute('innerHTML'))},ensure_ascii=False), "prevChatID": driver.current_url.split("prompt/")[-1]}



                  
                    #return JSONResponse(content=jsonable_encoder({"message": md(allBotMsg.get_attribute('innerHTML')), "prevChatID": driver.current_url.split("prompt/")[-1]}))



                elif numOfElements > 1:
                    raise Exception("More than one input field found")
                else:
                    raise Exception("No input field found")

            finally:
                pass


            #except Exception as e:
            #    print(f"Errore durante l'attesa del caricamento della pagina: {e}")
            #    return None
        else:  #previous_chatID = ""
            if DEBUG_ENABLED.lower() == "true":
                print("Il Driver è stato trovato")
            try:
                verify_field = WebDriverWait(driver,40).until(
                    EC.presence_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='textbox']"""))
                )
                if DEBUG_ENABLED.lower() == "true":
                    print("Elemento 1 Ok")
                numOfElements = verify_field.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='textbox']""").__len__()
                if DEBUG_ENABLED.lower() == "true":
                    print("Elemento 2 Ok")
                if numOfElements == 1:                      

                    if str(driver.current_url).__contains__("prompt"):

                        verify_field.send_keys(Keys.LEFT_CONTROL, "k")

                        input_field = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@role='dialog']//div[@role='textbox']"""))
                        )
                        if DEBUG_ENABLED.lower() == "true":
                            print("Elemento 3 Ok")
                    else:
                        input_field = verify_field
                        if DEBUG_ENABLED.lower() == "true":
                            print("Elemento 4 Ok")


                    numCheckBotMsgsBefore = 0
                    numIcons = 0

                    input_field.send_keys(message)
                    input_field.send_keys(Keys.RETURN)

                    WebDriverWait(driver, 120).until(
                            EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']"""))
                        )
                    if DEBUG_ENABLED.lower() == "true":
                        print("Elemento before 5 Ok")

                    wait = WebDriverWait(driver, 40)
                    allBotMsg = wait.until(
                             lambda driver: (
                                lambda els: els[numCheckBotMsgsBefore] if len(els) >= numCheckBotMsgsBefore + 1 and els[numCheckBotMsgsBefore].is_displayed() else False
                                )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']"""))
                            )
                    if DEBUG_ENABLED.lower() == "true":
                        print("Elemento 5 Ok")
                    
                    #wait = WebDriverWait(driver, 40)
                    #alliconsBot = wait.until(
                    #         lambda driver: (
                    #            lambda els: els[numIcons] if len(els) >= numIcons + 1 and els[numIcons].is_displayed() else False
                    #            )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@aria-disabled='true']"""))
                    #        )

                    WebDriverWait(driver, 40).until(
                            EC.visibility_of_element_located((By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@aria-disabled='true']"""))
                        )
                    if DEBUG_ENABLED.lower() == "true":
                        print("Elemento 6 Ok")

                    
                    wait = WebDriverWait(driver, 40)
                    alliconsBot = wait.until(
                             lambda driver: (
                                lambda els: els[numIcons] if len(els) >= numIcons + 1 and els[numIcons].is_displayed() else False
                                )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//span[contains(@class, 'html-span')]/div[@role='button' and @id != '']"""))
                            )
                    if DEBUG_ENABLED.lower() == "true":
                        print("Elemento 7 Ok")

                    wait = WebDriverWait(driver, 10)
                    allBotMsg = wait.until(
                             lambda driver: (
                                lambda els: els[numCheckBotMsgsBefore] if len(els) >= numCheckBotMsgsBefore + 1 and els[numCheckBotMsgsBefore].is_displayed() else False
                                )(driver.find_elements(By.XPATH, """//*[starts-with(@id, 'mount_0_0_')]//div[@dir='auto']"""))
                            )
                    if DEBUG_ENABLED.lower() == "true":        
                        print("Elemento 8 Ok")

                    
                    return json.dumps({"message": md(allBotMsg.get_attribute('innerHTML'), strip=['style', 'script'], skip=['style', 'script'], wrap=False).replace("\t", "    "), "prevChatID": driver.current_url.split("prompt/")[-1]}, ensure_ascii=False)

                else:
                    raise Exception("No input field found")

                
            except Exception as e:
                print(f"Errore durante l'attesa del caricamento della pagina: {e}")
                return None

    else:
        print("Errore: driver non trovato. Esegui grab_cookies.py prima.")
        return None

async def main():
    ###
    # main() definition usata solo per il troubleshooting del codice al momento dello sviluppo
    # al momento dell'avvio del presente script come mostrato nell'  if __name__ == "__main__":
    # è possibile utilizzare la funzione main() per testare il codice
    # senza dover eseguire il server FastAPI
    # in questo caso è necessario commentare la parte del codice che si occupa di avviare il server
    # in particolare le righe:
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # in questo modo il codice verrà eseguito senza avviare il server
    # e verrà utilizzato il driver per testare il codice
    # in questo caso è necessario commentare la parte del codice che si occupa di avviare il server
    # in particolare le righe:
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    session_data = load_session_data()
    if not session_data:
        print("Errore: session_data.json non trovato o vuoto. Esegui grab_cookies.py prima.")
        return

    webdriver_url = os.getenv("WEBDRIVER_URL", "http://127.0.0.1:4444") # Selenium Grid/WebDriver URL
    driver = None
    try:
        driver = await verify_selenium_instance(webdriver_url, session_data,driver)  

        message = "Scrivi una pagina hello word in python"
        prevChatID = ""
        
        response = send_message_with_selenium(message, driver, previous_chatID=f"{prevChatID}")
        print(response)
            

    finally:
        if driver:
            driver.close()





@app.post("/send-message")
async def send_message(request: Request):
    global driver
    global webdriver_url
    global session_data


    data = await request.json()
    async with processing_lock_request:

        message = str(data.get("message")).strip()
        prevChatID = str(data.get("prevChatID", "")).strip()
        response = None


        if prevChatID == "":
            idx = 1
            while response == None and idx <= 3:
                async with processing_lock_sendfunc:
                    response = await send_message_with_selenium(message="/new", driver=driver, previous_chatID=prevChatID)
                idx += 1

        
            prevChatID = json.decoder.JSONDecoder().decode(response)['prevChatID']
            if DEBUG_ENABLED.lower() == "true":
                print("questo è il chat ID ricavato: ",prevChatID)
            
            response = None
            idx = 1
            while response == None and idx <=3:
                async with processing_lock_sendfunc:
                    response = await send_message_with_selenium(message=message, driver=driver, previous_chatID=prevChatID)
                idx += 1

        else:
            response = None
            idx = 1
            while response == None and idx <=3:
                async with processing_lock_sendfunc:
                    response = await send_message_with_selenium(message=message, driver=driver, previous_chatID=prevChatID)
                idx += 1

        return json.decoder.JSONDecoder().decode(response)


# Endpoint: GET /v1/models
@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    models = [
        ModelData(
            id=model_name,
            created=int(time.time()),  # timestamp corrente
        )
        for model_name in AVAILABLE_MODELS
    ]
    return ModelsResponse(data=models)

@app.post("/v1/chat/completions")
@app.post("/chat/completions")  # Aggiunto!
async def chat_completions(request: Request):

    data = await request.json()
    async with processing_lock_request:
        user_message = data["messages"][-1]["content"]
        model = data.get("model", "meta-ai-openai-proxy")  # fallback

        # Estrai risposta dalla Web UI
        try:

            global driver
            global webdriver_url
            global session_data

            response = None

            prevChatID_from_request = data.get("prevChatID", "")

            if prevChatID_from_request == "":
                # This is a new conversation or the client didn't provide a previous chat ID
                # Initiate a new chat session if needed by sending "/new"
                idx = 1
                while response is None and idx <= 3:
                    async with processing_lock_sendfunc:
                        response = await send_message_with_selenium(message="/new", driver=driver, previous_chatID="")
                    idx += 1
                
                if response:
                    prevChatID_from_request = json.decoder.JSONDecoder().decode(response)['prevChatID']
                    print("New chat ID obtained: ", prevChatID_from_request)
                else:
                    raise Exception("Failed to initiate new chat session.")

                # Now send the actual user message
                response = None
                idx = 1
                while response is None and idx <= 3:
                    async with processing_lock_sendfunc:
                        response = await send_message_with_selenium(message=user_message, driver=driver, previous_chatID=prevChatID_from_request)
                    idx += 1
            else:
                # Continue existing conversation
                response = None
                idx = 1
                while response is None and idx <= 3:
                    async with processing_lock_sendfunc:
                        response = await send_message_with_selenium(message=user_message, driver=driver, previous_chatID=prevChatID_from_request)
                    idx += 1


            assistant_content = json.decoder.JSONDecoder().decode(response)['message'] 
            chat_id = json.decoder.JSONDecoder().decode(response)['prevChatID']
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

        # Costruisci risposta OpenAI-compatible
        response = {
            "id": f"{chat_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "system_fingerprint": None,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": assistant_content
                    },
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(assistant_content.split()),
                "total_tokens": len(user_message.split()) + len(assistant_content.split())
            }
        }

        return JSONResponse(content=response)


def keep_alive(driver):
    while True:
        try:
            # Esegui un'azione innocua per mantenere viva la sessione
            driver.execute_script("return document.readyState;")
        except:
            print("Sessione terminata o driver chiuso.")
            break
        time.sleep(120)  # Ogni 2 minuti





driver = None
webdriver_url = os.getenv("WEBDRIVER_URL", "http://127.0.0.1:4444")
#webdriver_url = "http://127.0.0.1:4444" # Selenium Grid/WebDriver URL   
session_data = load_session_data()

# Simuliamo una lista di modelli disponibili
AVAILABLE_MODELS = ["meta-ai-openai-proxy"]



if __name__ == "__main__":

    
    if not session_data:
        print("Errore: session_data.json non trovato o vuoto. Esegui grab_cookies.py prima.")
        quit()
    
    try:
        if driver is None:
            driver = verify_selenium_instance(webdriver_url, session_data, driver)
            #driver = asyncio.run(verify_selenium_instance(webdriver_url, session_data, driver))

        # Avvia il thread che mantiene viva la sessione
        keep_alive_thread = Thread(target=keep_alive, args=(driver,), daemon=True)
        keep_alive_thread.start()

        uvicorn.run(app, host="0.0.0.0", port=8000)


    finally:
        if driver:
            driver.close()