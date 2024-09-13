import aiohttp
import asyncio
from bs4 import BeautifulSoup
from scraper.number_graber import get_phone_number
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Название", "Телефон", "Ссылка"])



async def fetch_phone_number(session, link):
    loop = asyncio.get_event_loop()
    
    # Запускаем get_phone_number через loop.run_in_executor
    phone_number = await loop.run_in_executor(None, get_phone_number, link)
    
    return phone_number

async def parse_ad(ad, session):
    link_element = ad.find('a', class_='unlink white')
    if link_element is None:
        return None  # Если нет ссылки, пропускаем это объявление
    link = link_element['href']

    async with session.get(link) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        title_element = soup.find('h1', class_='head')
        title = title_element.text.strip() if title_element else "Заголовок не найден"

    # Получаем ID объявления для запроса номера телефона
    ad_id = link.split('/')[-1].removesuffix('.html')
    ready_id = ad_id.split("_")[-1]

    # Запрашиваем номер телефона для этого объявления
    phone_number = await fetch_phone_number(session, link)

    return (title, phone_number, link)

async def parse_page(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0",
    }
    
    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        ads = soup.find_all('section', class_='ticket-item')

        page_data = []
        for ad in ads:
            ad_data = await parse_ad(ad, session)  # Обрабатываем каждое объявление по одному
            if ad_data:
                page_data.append(ad_data)
                await asyncio.sleep(1)  # Ждем 1 секунду перед обработкой следующего объявления
                
        return page_data

async def main():
    base_url = "https://auto.ria.com/uk/legkovie/?page="
    page = 1

    async with aiohttp.ClientSession() as session:
        while True:
            current_url = f"{base_url}{page}"
            print(f"Парсинг страницы {page}: {current_url}")

            page_data = await parse_page(session, current_url)
            print(f"Page data: {page_data}")

            if not page_data:
                break

            for title, phone_number, link in page_data:
                ws.append([title, phone_number, link])

            wb.save(f"cars_data{page}.xlsx")

            page += 1

    

asyncio.run(main())
    