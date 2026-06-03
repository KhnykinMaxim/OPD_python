import requests
from bs4 import BeautifulSoup
import json
import re


print("=== Пример работы BeautifulSoup ===")

url_bs = "https://pypi.org/project/bs4/"

response_bs = requests.get(url_bs)
soup = BeautifulSoup(response_bs.text, "html.parser")

title = soup.find("h1").get_text()

print("Заголовок страницы:", title)



print("\n=== Парсинг товаров LEGO ===")

url = "https://api.detmir.ru/v4/products"

params = {
    "filter": "autoFilter:true;categories[].alias:lego;platform:web;site:detmir;withregion:RU-MOW",
    "limit": 50
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, params=params)
items = response.json()

print("Товаров:", len(items))

print("\nТовары со скидкой > 30%:\n")

count = 0

for item in items:
    name = item.get("title")
    discount = item.get("discount_percentage")

    price = (item.get("price") or {}).get("price")
    old_price = (item.get("old_price") or {}).get("price")

    if discount and discount > 30:
        count += 1

        print(name)
        print(f"Цена: {price} ₽ | Старая цена: {old_price} ₽ | Скидка: {discount}%\n")

print(f"Количество товаров со скидкой > 30%: {count}")


print("\n=== Парсинг LEGO через BeautifulSoup ===")

url = "https://www.detmir.ru/catalog/index/name/lego/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# ищем script с данными
scripts = soup.find_all("script")

data_json = None

for script in scripts:
    if script.string and "products" in script.string:
        try:
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\})', script.string)
            if match:
                data_json = json.loads(match.group(1))
                break
        except:
            continue

if not data_json:
    print("Не удалось найти данные")
    exit()

# ищем товары внутри JSON
products = data_json.get("products", {}).get("items", [])

count = 0

print("\nТовары со скидкой > 30%:\n")

for item in products:
    try:
        name = item.get("title")

        discount = item.get("discount_percentage", 0)

        price = item.get("price", {}).get("price")
        old_price = item.get("old_price", {}).get("price")

        if discount > 30:
            count += 1

            print(name)
            print(f"Цена: {price} ₽ | Старая: {old_price} ₽ | Скидка: {discount}%\n")
    except:
        continue
print(f"Количество: {count}")


##print(json.dumps(items[1], indent=2, ensure_ascii=False))