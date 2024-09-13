from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_phone_number(link):
    # Инициализация WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Открываем страницу
    driver.get(link)

    try:
        # Ожидаем, пока элемент станет кликабельным
        wait = WebDriverWait(driver, 10)  # Устанавливаем тайм-аут в 10 секунд
        phone_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#phonesBlock > div > span > a')))
        driver.execute_script("arguments[0].scrollIntoView(true);", phone_element)
        phone_element.click()

        # Ожидаем появления номера телефона
        phone_number_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#openCallMeBack > div.item-field.list-phone > div.popup-successful-call-desk.size24.bold.green.mhide.green")))
        phone_number = phone_number_element.text
    except Exception as e:
        print(f"Ошибка получения номера телефона: {e}")
        phone_number = None
    finally:
        driver.quit()  # Закрываем браузер

    return phone_number