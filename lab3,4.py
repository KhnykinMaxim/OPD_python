import requests
import time
from requests.adapters import HTTPAdapter
import urllib3
urllib3.disable_warnings()

session = requests.Session()
session.verify = False
requests.get = session.get
requests.post = session.post

TOKEN = "token"
URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = -1

print("Бот запущен...")

# хранение рецептов
user_meals = {}
user_last_recipe = {}

# --- отправка ---
def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url, caption, keyboard=None):
    data = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }

    if keyboard:
        data["reply_markup"] = keyboard

    requests.post(URL + "sendPhoto", json=data)

def send_long_message(chat_id, text):
    for i in range(0, len(text), 4000):
        send_message(chat_id, text[i:i+4000])

# --- перевод ---
def translate(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ru",
        "dt": "t",
        "q": text
    }

    try:
        res = requests.get(url, params=params).json()
        return "".join([i[0] for i in res[0]])
    except:
        return text

def translate_long(text):
    parts = [text[i:i+400] for i in range(0, len(text), 400)]
    result = ""

    for part in parts:
        result += translate(part) + " "

    return result

# --- поиск рецептов ---
def get_recipes(ingredients):
    all_meals = []

    for ing in ingredients:
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ing}"
        res = requests.get(url).json()
        meals = res.get("meals")

        if meals:
            ids = set([m["idMeal"] for m in meals])
            all_meals.append(ids)

    if not all_meals:
        return []

    return list(set.intersection(*all_meals))

def get_full_recipe(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    return requests.get(url).json()["meals"][0]


# --- основной цикл ---
while True:
    try:
        updates = requests.get(URL + "getUpdates", params={"offset": offset}).json()

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            # --- кнопки ---
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]

                # следующий рецепт
                if data == "next":
                    meals = user_meals.get(chat_id, [])

                    if not meals:
                        send_message(chat_id, "❌ No more recipes")
                        continue

                    meal_id = meals.pop(0)
                    meal = get_full_recipe(meal_id)

                # перевод
                elif data == "translate":
                    text = user_last_recipe.get(chat_id)

                    if not text:
                        send_message(chat_id, "❌ Nothing to translate")
                        continue

                    send_message(chat_id, "⏳ Translating...")
                    translated = translate_long(text)

                    send_long_message(chat_id, "🇷🇺 Перевод:\n" + translated)
                    continue

                else:
                    continue

            # --- обычные сообщения ---
            elif "message" in update:
                text = update["message"].get("text", "").lower()
                chat_id = update["message"]["chat"]["id"]

                if text == "/start":
                    send_message(chat_id,
                                 "👋 Recipe Bot\n\nSend ingredients:\nchicken rice\nor\ntomato, onion")
                    continue

                ingredients = text.replace(",", " ").split()
                meal_ids = get_recipes(ingredients)

                if not meal_ids:
                    send_message(chat_id, "❌ Nothing found")
                    continue

                user_meals[chat_id] = meal_ids.copy()
                meal_id = user_meals[chat_id].pop(0)
                meal = get_full_recipe(meal_id)

            else:
                continue

            # --- оформление ---
            name = meal["strMeal"]
            instructions = meal["strInstructions"]
            image = meal["strMealThumb"]

            # сохраняем для перевода
            user_last_recipe[chat_id] = instructions

            ingredients_list = []
            for i in range(1, 11):
                ing = meal.get(f"strIngredient{i}")
                meas = meal.get(f"strMeasure{i}")

                if ing and ing.strip():
                    ingredients_list.append(f"• {ing} ({meas})")

            ingredients_text = "\n".join(ingredients_list)

            caption = f"""🍽 *{name}*

🥕 *Ingredients:*
{ingredients_text}
"""

            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "➡️ Next", "callback_data": "next"},
                        {"text": "🇷🇺 Translate", "callback_data": "translate"}
                    ]
                ]
            }

            send_photo(chat_id, image, caption, keyboard)

            send_long_message(chat_id, f"📖 Recipe:\n{instructions}")

    except Exception as e:
        print("Ошибка:", e)

    time.sleep(2)
