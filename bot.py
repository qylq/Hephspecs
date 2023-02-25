import telebot
from telebot import types
from bs4 import BeautifulSoup
import requests
from fuzzywuzzy import fuzz, process

bot = telebot.TeleBot('token')
allowed = [ids]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋")
    bot.send_message(message.chat.id, "Пропиши /help для получения информации.")
@bot.message_handler(commands=['help'])
def help(message):
	bot.reply_to(message, "Я - бот для получения подробной информации о наушниках. Просто присылаешь мне названия наушников, о которых ты хочешь узнать подробную информацию, а я тебе её присылаю.")
@bot.message_handler(func=lambda message: message.from_user.id not in allowed)
def restrict_access(message):
    bot.send_message(message.chat.id, f"❌ Запрещено к использованию\nID: <code>{message.from_user.id}</code>", parse_mode="html")
    print(f"{message.chat.username} (ID: {message.from_user.id}) пытается использовать бота. Запрос: {message.text}")

@bot.message_handler(func=lambda message: True)
def hephspecs(message):
    print(f"{message.chat.username} ({message.from_user.id}), запрос: {message.text}")
    # afr
    headphones = message.text
    url = f"https://crinacle.com/?s={headphones.replace(' ', '+')}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    graphic = []
    matches = []

    all_cards = soup.find_all("div", class_="elementor-widget-container")
    for card in all_cards:
        card_urls = card.find_all("a", class_="elementor-post__thumbnail__link")
        card_texts = card.find_all("h2", class_="elementor-post__title")
        for url, text in zip(card_urls, card_texts):
            card_url = url.get("href")
            card_text = text.text.strip()
            matches.append(card_text)
            if card_url.startswith("https://crinacle.com/graphs/"):
                best_match = process.extractOne(headphones.lower(), matches, scorer=fuzz.partial_ratio)
                if headphones.lower().replace(" ", "") in best_match[0].lower().replace(" ", ""):
                    graphic.append(card_url)

    if graphic:
        page = requests.get(graphic[0])
        soup = BeautifulSoup(page.text, "html.parser")
        graph_pic = soup.find_all('img', class_=["attachment-large", "size-large"]) 
        for graph_png in graph_pic:
            graphic[0] = graph_png.get("src")
        print(f"{message.chat.username} ({message.from_user.id}), ссылка на Crinacle: {graphic[0]}")
    else: pass

    # best for
    url = f"https://www.rtings.com/api/v1/pages?query={headphones}&admin=false&highlights=false&partial=true&count=5&silo=null"
    page = requests.get(url).json()
    bf = []

    try:
        url = f"https://www.rtings.com{page['data'][0]['url']}"
        page = requests.get(url)

        soup = BeautifulSoup(page.text, "html.parser")

        scorecard_table = soup.find('div', class_="scorecard-table")
        scorecard_rows = scorecard_table.find_all('div', class_="scorecard-row is-showing-details")

        for bestfor in scorecard_rows:
            name = bestfor.find('div', class_="scorecard-row-name").text.strip()
            bf.append(name)
        if url.startswith("https://www.rtings.com/headphones/reviews/"):
            print(f"{message.chat.username} ({message.from_user.id}), ссылка на Rtings: {url}")
        else: pass
    except: pass
    
    bf_translation = {"Neutral Sound": "Нейтральный звук",
                      "Commute/Travel": "Поездка/Путешествие",
                      "Sports/Fitness": "Спорт/Фитнес",
                      "Office": "Работа в офисе",
                      "Wireless Gaming": "Игра по беспроводной связи",
                      "Wired Gaming": "Игра по проводной связи",
                      "Phone Calls": "Телефонные звонки"}

    if bf and bf[0] in bf_translation:
        bf[0] = bf_translation[bf[0]]
    else: pass

    # headphones name
    try:
        headphones_name = []
        soup = BeautifulSoup(page.text, "html.parser")
        banner = soup.find('div', class_="product_page-banner")

        banner_primary_title = banner.find('span', class_="e-page_title-primary").text
        headphones_name.append(banner_primary_title)
    except: pass

    # worst for
    scores = {}
    wf = []
    wf_b = soup.find_all('div', class_="scorecard-table")

    try:
        for worstfor in wf_b:
            wf_rows = worstfor.find_all('div', class_="scorecard-row")
            for row in wf_rows:
                score = row.find('span', class_="e-score_box-value").text
                name = row.find('div', class_="scorecard-row-name").text.strip()
                scores[name] = float(score)
            wf_score = min(scores.values())
            wf_name = min(scores, key=scores.get)
            wf.append(wf_name)
    except: pass

    wf_translation = {"Neutral Sound": "Нейтральный звук",
                      "Commute/Travel": "Поездка/Путешествие",
                      "Sports/Fitness": "Спорт/Фитнес",
                      "Office": "Работа в офисе",
                      "Wireless Gaming": "Игра по беспроводной связи",
                      "Wired Gaming": "Игра по проводной связи",
                      "Phone Calls": "Телефонные звонки"}

    if wf:
        if "Truly Wireless" in headphones_name[0] and wf[0] == "Wired Gaming":
            scores.pop("Wired Gaming")
            wf_score = min(scores.values())
            wf_name = min(scores, key=scores.get)
            wf[0] = wf_name
        if wf[0] in wf_translation:
            wf[0] = wf_translation[wf[0]]

    # headphones photo
    try:
        headphones_png = []
        soup = BeautifulSoup(page.text, "html.parser")

        banner = soup.find('div', class_="product_page-banner")
        banner_photo = banner.find('div', class_="product_page-banner-image")
        headphones_url = banner_photo.find('img').get("src")
        headphones_png.append(headphones_url)
    except: pass

    # features
    try:
        func_char = {}
        soup = BeautifulSoup(page.text, "html.parser")
        features_block = soup.find_all('div', class_='featured_items-block-featured')

        for features in features_block:
            func = features.find('span', class_='featured_items-block-featured-label').text.strip()
            char = features.find_all('span')[1].text.strip()
            func_char[func] = char
    except: pass

    if func_char:
        func_translation = {"Type": "Тип",
                            "Enclosure": "Корпус",
                            "Wireless": "Беспроводная связь",
                            "Transducer": "Преобразователь",
                            "Noise Cancelling": "Шумоподавление",
                            "Mic": "Микрофон"}
        func_char_translated = {}
        for key in func_char:
            if key in func_translation:
                new_key = func_translation[key]
                func_char_translated[new_key] = func_char[key]
        func_char = func_char_translated

        char_translation = {"In-ear": "Внутриканальные",
                            "Over-ear": "Охватывающие",
                            "On-ear": "Накладные",
                            "Earbuds": "Вкладыши",
                            
                            "Closed-Back": "Закрытый",
                            "Open-Back": "Открытый",
                            
                            "Truly Wireless": "Полностью беспроводные",
                            
                            "Dynamic": "Динамический",
                            "Planar Magnetic": "Плоский магнитный",
                            "Electrostatic": "Электростатический",
                            
                            "Yes": "Да",
                            "No": "Нет"}
        for key, value in func_char.items():
            if value in char_translation:
                func_char[key] = char_translation[value]

    # final message
    try:
        bf_msg = f"👍 Лучше всего для: {bf[0]}"
        wf_msg = f"👎 Хуже всего для: {wf[0]}"
        features_msg = "📄 Характеристики\n" + f"\n".join(f"{func}: {char}" for func, char in func_char.items())
        msg_txt = f"<code>{headphones_name[0]}</code>\n\n{bf_msg}\n{wf_msg}\n\n{features_msg}\n\n{url}"
    except: pass

    mf = False
    pressed_users = set()

    wrong = telebot.types.InlineKeyboardButton(text="❌ Не то", callback_data="wrong")
    correct = telebot.types.InlineKeyboardButton(text="✅ Всё то", callback_data="correct")
    keyboard = telebot.types.InlineKeyboardMarkup().add(wrong, correct)

    if graphic:
        bot.send_photo(message.chat.id, graphic[0])
    else:
        bot.send_message(message.chat.id, f"☹️ Я не нашел <code>{headphones}</code> на Crinacle", parse_mode="html")
    
    if url.startswith("https://www.rtings.com/headphones/reviews/"):
        if headphones.lower().replace(" ", "") in headphones_name[0].lower().replace(" ", ""):
            mf = True
    if mf == True:
        bot.send_photo(message.chat.id, headphones_png[0])
        bot.send_message(message.chat.id, msg_txt, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)
        @bot.callback_query_handler(func=lambda call: True)
        def callback(call):
            if call.data == "wrong":
                if call.from_user.id in pressed_users:
                    bot.answer_callback_query(callback_query_id=call.id, text="👌 Уже знаем о вашей проблеме")
                else:
                    pressed_users.add(call.from_user.id)
                    with open("wrong_results.txt", "w") as f:
                        f.write(f"{message.chat.username} ({message.from_user.id}): error in result \"{headphones}\"\n{graphic[0]}\n{url}")
                    bot.answer_callback_query(call.id, text="👌 Спасибо, что сообщили! Мы постараемся улучшить точность результатов")
                    print(f"{message.chat.username} ({message.from_user.id}): ошибка в результате, просмотрите файл")
            if call.data == "correct":
                if call.from_user.id in pressed_users:
                    bot.answer_callback_query(callback_query_id=call.id, text="😃 Спасибо!")
                else:
                    cnt = open("correct_results.txt", "r", encoding="utf-8")
                    with cnt as f:
                        cnt = int(f.read())
                    cnt += 1
                    with open("correct_results.txt", "w") as f:
                        f.write(str(cnt))
                    bot.answer_callback_query(callback_query_id=call.id, text="😃 Спасибо!")
    else:
        bot.send_message(message.chat.id, f"☹️ Я не нашел <code>{headphones}</code> на Rtings", parse_mode="html")

bot.infinity_polling()
