from threading import Thread, Lock
from telebot import TeleBot
from telebot.types import * 
from CryptoBot import Send
from config import *
from keyboards import *
from sqlite3 import connect
from time import time, sleep
from requests import post, get
from random import randint, choice
from string import ascii_letters



bot = TeleBot(BOT_TOKEN, "HTML")
lock = Lock()
headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': CRYPTO_TOKEN}
header = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': CRYPTO_TOKEN}
crypto = Send(CRYPTO_TOKEN, fiat="usd")
con = connect("db.db", check_same_thread=False, isolation_level="IMMEDIATE"); cursor = con.cursor()
def get_data(id: int, username: str = None, name: str = None):
    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    dt = cursor.fetchone()
    username = username if not username is None else dt[1]
    name = name if not name is None else dt[2]
    if dt is None:
        data = (id, username, name, 0.0, 0, 0, time(), None, None, "False")
        cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)", data)
    else:
        if dt[7] is None or not dt[7] < time() :
            data = (id, username, name, dt[3], dt[4], dt[5], dt[6], dt[7], dt[8], dt[9])
        else:
            data = (id, username, name, dt[3], dt[4], dt[5], dt[6], None, dt[8], dt[9])
        cursor.execute("UPDATE users SET username=?, name=? WHERE id=?", (data[1], data[2], data[0]))
    con.commit()
    return data
def timecount(tim: float) -> tuple:
    r = abs(time() - tim)
    days = int(r // (24 * 60 * 60))
    hours = int(r // (60 * 60) - days * 24)
    mins = int(r // (60) - hours * 60 - days * 24 * 60 )
    return days, hours, mins
def active_upgrades_filter(upgrades):
    ups = upgrades.copy()
    for upgrade in upgrades:
        if upgrade[2] < time():
            cursor.execute("DELETE FROM upgrades WHERE id=? AND name=? AND expires=?", upgrade)
            con.commit()
            try:
                bot.send_message(upgrade[0], f"<b>Улучшение {upgrade[1]} закончилось!\n\nКупите его снова в разделе улучшения</b>", reply_markup=start_kb())
            except: ...
            ups.remove(upgrade)
    return ups
def gen_random_string(length):
    return "".join([choice(ascii_letters) for _ in range(length)])
def validate_url(url: str) :
    content = get(url).text
    if "You are invited to a <strong>group chat</strong> on <strong>Telegram</strong>. Click to join:" in content:
        return False
    return True
def get_active_adv():
    cursor.execute("SELECT * FROM advertising")
    cnlss = cursor.fetchall()
    cnls = []
    for cnl in cnlss:
        if validate_url(cnl[1]):
            cnls.append(cnl)
        else:
            cursor.execute("DELETE FROM advertising WHERE channel_id=?", (cnl[0],))
    con.commit()
    return cnls
def is_all_bad(call):
    for cnl in get_active_adv():
        try:
            if bot.get_chat_member(cnl[0], call.from_user.id).status in ['creator', 'administrator', 'member']:
                return False
            else:
                return True
        except Exception as e:
            return False
def get_unsub_cnls(id):
    unsub = []
    for cnl in get_active_adv():
        try:
            if bot.get_chat_member(cnl[0], id).status in ['creator', 'administrator', 'member']:
                ...
            else:
                unsub.append((bot.get_chat(cnl[0]), cnl[1]))
        except Exception as e:
            ...
    return unsub


@bot.callback_query_handler(lambda call: call.data == "info")
def info(call):
    cursor.execute("SELECT id FROM users")
    bot.edit_message_text(INFO_TEXT.replace("???", str(len(cursor.fetchall()))), call.message.chat.id, call.message.id, reply_markup=info_kb())


@bot.callback_query_handler(is_all_bad)
@bot.message_handler(func=is_all_bad)
def penis(call):
    text = "<b>Вы не подписались на каналы!\n"
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[8] is None:
        try:
            ref = int(call.text.replace("/start ", ""))
            if data[9] == "True": 
                ref = data[8]
            if ref == call.from_user.id: raise Exception 
            cursor.execute("SELECT * FROM users WHERE id=?", (ref,))
            data = cursor.fetchone()
            if not data is None:
                cursor.execute("UPDATE users SET ref=?, sss=? WHERE id=?", (ref, "True", call.from_user.id))
                con.commit()
        except Exception as e:
            ...
    for cnl in get_unsub_cnls(call.from_user.id):
        text += f'\n\t<a href="{cnl[1]}">{cnl[0].title.replace("<", "").replace(">", "")}</a>'
    text += "</b>"
    if type(call) is Message:
        bot.send_message(call.chat.id, text)
    else:
        bot.edit_message_text(text, call.message.chat.id, call.message.id)


@bot.message_handler(['send'])
def sendad(message):
    if message.from_user.id != OWNER_ID: return
    try:
        msg = "\n".join(message.text.split("\n")[1:])
        users = cursor.execute("SELECT * FROM users")
        good = 0
        bad = 0
        for user in users:
            try:
                formatted_msg = msg.replace("%ID%", str(user[0])).replace("%USERNAME%", user[1]).replace("%NAME%", user[2]).replace("%BALANCE%", str(user[3])).replace(r"%EXL%", str(user[4]))
                bot.send_message(user[0], formatted_msg)
                good += 1
            except Exception as e:
                bad += 1
        bot.send_message(message.from_user.id, f"<b>Ваше сообщение было успешно отправлено!\n\n{good} пользователей получили сообщение, {bad} не получили</b>")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
    con.commit()


@bot.message_handler(['add_ms'])
def add_ms(message: Message):
    if message.from_user.id != OWNER_ID: return None
    try:
        channel_id = int(message.text.split()[1])
        subs_count = abs(int(message.text.split()[2]))
        if subs_count == 0:
            raise Exception
    except:
        bot.reply_to(message, "<b>динаху йопта чота нетак ввёл, надо <code>/add_ms [id] [count]</code></b>"); return 
    msg = bot.reply_to(message, "<b>Параметры введены верно</b>")
    try:
        chat = bot.get_chat(channel_id)
    except:
        bot.edit_message_text("<b>Бот не был добавлен в канал</b>", msg.chat.id, msg.id); return 
    msg = bot.edit_message_text(msg.text + f"\n<b>Бот добавлен в канал {chat.title}, создаём пригласительную ссылку</b>", msg.chat.id, msg.id)
    try:
        link = bot.create_chat_invite_link(channel_id, "ExlossiveCoin", member_limit=subs_count).invite_link
    except Exception as e:
        bot.edit_message_text(f"<b>Не удалось создать ссылку\n<pre>python\n{e}</pre></b>", msg.chat.id, msg.id); return 
    msg = bot.edit_message_text(msg.text + f"\n<b>Пригласительная ссылка была успешно создана!\n<code>{link}</code></b>", msg.chat.id, msg.id)
    try:
        cursor.execute("DELETE FROM advertising WHERE channel_id=?", (channel_id,))
    except Exception as e: ...
    cursor.execute("INSERT INTO advertising VALUES(?,?)", (channel_id, link))
    con.commit()


@bot.message_handler(['start'])
@bot.callback_query_handler(lambda call: call.data == "start")
def start(call: CallbackQuery):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[8] is None:
        try:
            ref = int(call.text.replace("/start ", ""))
            if data[9] == "True": 
                ref = data[8]
            if ref == call.from_user.id: raise Exception 
            cursor.execute("SELECT * FROM users WHERE id=?", (ref,))
            data = cursor.fetchone()
            if not data is None:
                try:
                    bot.send_message(ref, f'<b>По вашей реферальной ссылке зашёл новый пользователь {call.from_user.first_name.replace(">", "").replace("<", "")}. Вам зачислено 2000 $EXL</b>')
                    cursor.execute("UPDATE users SET quicoins=quicoins+? WHERE id=?", (2000, ref))
                    cursor.execute("UPDATE users SET ref=?, sss=? WHERE id=?", (ref, "False", call.from_user.id))
                    con.commit()
                except Exception as e:
                    ...
        except Exception as e:
            ...
    elif data[9] == "True":
        ref = data[8]
        cursor.execute("SELECT * FROM users WHERE id=?", (ref,))
        data = cursor.fetchone()
        if not data is None:
            try:
                bot.send_message(ref, f'<b>По вашей реферальной ссылке зашёл новый пользователь {call.from_user.first_name.replace(">", "").replace("<", "")}. Вам зачислено 2000 $EXL</b>')
                cursor.execute("UPDATE users SET quicoins=quicoins+? WHERE id=?", (2000, ref))
                cursor.execute("UPDATE users SET ref=?, sss=? WHERE id=?", (ref, "False", call.from_user.id))
                con.commit()
            except Exception as e:
                ...
    text = start_text
    keyboard = start_kb()
    if type(call) is CallbackQuery:
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)
    else:
        bot.send_message(call.chat.id, text, reply_markup=keyboard)



@bot.callback_query_handler(lambda call: call.data == "profile")
def profile(call: CallbackQuery):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    days, hours, mins = timecount(float(data[6]))
    if data[7] is None:
        tap_text = 'Вы можете получить $EXL!'
    else:
        *_ ,can_tap_m = timecount(data[7])
        tap_text = f"Вы сможете получить $EXL через {can_tap_m} минут!"
    upgrades_text = ""
    cursor.execute("SELECT * FROM upgrades WHERE id=?", (call.from_user.id,))
    for upgrade in active_upgrades_filter(cursor.fetchall()):
        if upgrades_text == "":
            upgrades_text += "Активные улучшения"
        _, uhours, umins = timecount(upgrade[2])
        upgrades_text += f"\t\n<code>Улучшение {upgrade[1]} {uhours:02}:{umins:02}</code>"
    text = f'''<b>Добро пожаловать в ваш профиль!
    
$USDT: {data[3]}
$EXL: {data[4]}

Выведено: {data[5]}$
Вы зарегистрированы уже {days:02}:{hours:02}:{mins:02}

{upgrades_text}

{tap_text}</b>'''
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=profile_kb())



@bot.callback_query_handler(lambda call: call.data == "ref")
def ref(call: CallbackQuery):
    cursor.execute("SELECT * FROM users WHERE ref=?", (call.from_user.id,))
    c = len(cursor.fetchall())
    text = f'''<b>Приглашайте друзей и получайте $EXL!
    
Ваша реферальная ссылка - <code>https://t.me/ExlossiveCoinBot?start={call.from_user.id}</code>
На данный момент у вас {c} рефералов

Поделитесь ей с другом и получите 2000 $EXL</b>'''
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Поделиться", switch_inline_query=f'**Зарабатывай $EXL вместе со мной!\n\nhttps://t.me/ExlossiveCoinBot?start={call.from_user.id}**'))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="profile"))
    bot.edit_message_text(text, call.message.chat.id, call.message.id ,reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data == "notqui")
def notqui(call):
    bot.answer_callback_query(call.id, "Не угадали! Попробуйте снова")
    quigame(call)


@bot.callback_query_handler(lambda call: call.data == "quigame")
def quigame(call):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[7] is None:
        bot.edit_message_text("<b>Попытайте удачу и получите $EXL прямо сейчас!\n\nНажмите на одну из кнопок ниже</b>", call.message.chat.id, call.message.id, reply_markup=quigame_kb())
    else:
        *_ ,can_tap_m = timecount(data[7])
        bot.answer_callback_query(call.id, f"Вы можете получить $EXL только через {can_tap_m} мин.\n\nКупите улучшение чтобы автоматически получать $EXL", True)


@bot.message_handler(['db'])
def __da(message: Message):
    if message.from_user.id == OWNER_ID:
        file = open("db.db", "rb")
        bot.send_document(message.from_user.id, file.read())
        file.close()


@bot.callback_query_handler(lambda call: call.data.startswith("top"))
def teops(call: CallbackQuery):
    data = get_data(call.from_user.id, call.from_user.username, call.from_user.first_name)
    match call.data:
        case "top":
            text = "Выберите интересующий вас топ пользователей"
            keyboard = tops_kb()
        case "topqui":
            cursor.execute("SELECT name, username, quicoins from users ORDER BY quicoins ASC")
            tops = cursor.fetchall()
            text = "<b>Топ пользователей по балансу $EXL\n"
            for toper in tops[::-1][:11]:
                text += f'<blockquote><a href="https://t.me/{toper[1]}">{toper[0].replace(">", "").replace("<", "")}</a> - {toper[2]} $EXL</blockquote>'
            text += "</b>"
            keyboard = top_kb()
        case "topbal":
            cursor.execute("SELECT name, username, balance from users ORDER BY quicoins ASC")
            tops = cursor.fetchall()
            text = "<b>Топ пользователей по балансу $USD\n"
            for toper in tops[::-1][:11]:
                text += f'<blockquote><a href="https://t.me/{toper[1]}">{toper[0].replace(">", "").replace("<", "")}</a> - {toper[2]} $</blockquote>'
            text += "</b>"
            keyboard = top_kb()
        case "topwit":
            cursor.execute("SELECT name, username, withdrowed from users ORDER BY quicoins ASC")
            tops = cursor.fetchall()
            text = "<b>Топ пользователей по выведенным из бота $USD\n"
            for toper in tops[::-1][:11]:
                text += f'<blockquote><a href="https://t.me/{toper[1]}">{toper[0].replace(">", "").replace("<", "")}</a> - {toper[2]} $</blockquote>'
            text += "</b>"
            keyboard = top_kb()
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard, disable_web_page_preview=True)
    



@bot.callback_query_handler(lambda call: call.data == "qui")
def qui(call: CallbackQuery):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[7] is None:
        amount = randint(150, 400)
        TAP_COOLDOWN = randint(300, 600)
        cursor.execute("SELECT * FROM upgrades WHERE id=?", (call.from_user.id, ))
        x = False
        for upgrade in active_upgrades_filter(cursor.fetchall()):
            if "x" in upgrade[1]:
                x = int(upgrade[1][1])
        if x:
            amount *= x
        cursor.execute("UPDATE users SET quicoins=quicoins+?, next_tap=? WHERE id=?", (amount, time() + TAP_COOLDOWN, call.from_user.id))
        con.commit()
        bot.answer_callback_query(call.id, f"На ваш баланс было зачислено {amount} $EXL\n\nВ следующий раз вы сможете получить $EXL через {TAP_COOLDOWN // 60} минут\n\nКупите улучшение чтобы $EXL автоматически собирались", True)
        start(call)
    else:
        *_ ,can_tap_m = timecount(data[7])
        bot.answer_callback_query(call.id, f"Вы можете получить $EXL только через {can_tap_m} мин.\n\nКупите улучшение чтобы автоматически получать $EXL", True)



@bot.callback_query_handler(lambda call: call.data == "change")
def change(call: CallbackQuery):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[4] < 10000:
        bot.answer_callback_query(call.id, f"Чтобы обменять $EXL на USDT вам нужно ещё {10000 - data[4]}", True)
    else:
        usdts = round(data[4] / TOKEN_CHANGE_RATE, 5)
        cursor.execute("UPDATE users SET quicoins=0, balance=balance+? WHERE id=?", (usdts, call.from_user.id))
        con.commit()
        bot.answer_callback_query(call.id, f"Успешно!\n\nВы получили {usdts}$ на баланс!\n\nВы можете вывести их в профиле", True)
        profile(call)



@bot.callback_query_handler(lambda call: call.data == "cancel")
def cancel(call: CallbackQuery):
    try:
        bot.clear_step_handler(call.message)
    except:
        ...
    profile(call)



def deposit_check(message, old_id):
    if "/start" in message.text:
        start(message)
        return
    try:
        amount = float(message.text.strip())
        if amount < 0.1:
            msg = bot.edit_message_text("<b>Введите сумму на которую хотите пополнить баланс в $USDT\n\nВы должны ввести число</b>", message.chat.id, old_id)
            bot.register_next_step_handler(msg, deposit_check, msg.id)
        else:
            invoice = crypto.create_invoice(amount, "usdt")
            text = f"""<b>ID: {invoice['invoice_id']}
            
Оплатите счёт и нажмите кнопку проверить оплату</b>"""
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("Оплатить", invoice['pay_url']))
            keyboard.row(InlineKeyboardButton("Проверить оплату", callback_data="check_pay"))
            bot.edit_message_text(text, message.chat.id, old_id, reply_markup=keyboard)
    except:
        msg = bot.edit_message_text("<b>Введите сумму на которую хотите пополнить баланс в $USDT\n\nВы должны ввести число</b>", message.chat.id, old_id)
        bot.register_next_step_handler(msg, deposit_check, msg.id)
    try:
        bot.delete_message(message.chat.id,message.id, timeout=10)
    except: ...



@bot.callback_query_handler(lambda call: call.data == "deposit")
def deposit(call: CallbackQuery):
    msg = bot.edit_message_text("<b>Введите сумму на которую хотите пополнить баланс в $USDT</b>", call.message.chat.id, call.message.id, reply_markup=cancel_kb())
    bot.register_next_step_handler(msg, deposit_check, msg.id)



@bot.callback_query_handler(lambda call: call.data == "check_pay")
def check_pay(call: CallbackQuery):
    invoice_id = call.message.text.split("\n")[0].replace("ID: ", "")
    invoice = crypto.get_invoice(invoice_id)
    if "status" not in invoice:
        bot.answer_callback_query(call.id, "Счёт истёк!", True)
    elif invoice['status'] == "active":
        bot.answer_callback_query(call.id, "Счёт не был оплачен\n\nПроверьте ещё раз, или обратитесь в поддержку", True)
    else:
        amount = invoice['amount']
        cursor.execute("UPDATE users SET balance=balance+? WHERE id=?", (amount, call.from_user.id))
        con.commit()
        bot.answer_callback_query(call.id, "Спасибо за пополнение баланса!", True)
        profile(call)



def withdraw_callback(message, old_id):
    if "/start" in message.text:
        start(message)
        return
    try:
        amount = float(message.text.strip())
        if amount < 0.1:
            msg = bot.edit_message_text("<b>Введите сумму которую хотите вывести\n\nВы должны ввести число</b>", message.chat.id, old_id)
            bot.register_next_step_handler(msg, withdraw_callback, msg.id)
        else:
            try:
                cheque = crypto.create_cheque(amount * 0.95, "usdt")
            except:
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton("Поддержка", url=f"tg://user?id={OWNER_ID}"))
                bot.edit_message_text("<b>К сожалению на данный момент мы не можем вывести ваши средства!\n\nПопробуйте снова позже или обратитесь в поддержку</b>", message.chat.id, old_id, reply_markup=keyboard)
                return
            text = f"""<b>Средства были успешно выведены!

Заберите их по ссылке ниже!</b>"""
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(f"Забрать {amount}$", cheque['bot_check_url']))
            cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, message.from_user.id,))
            con.commit()
            bot.edit_message_text(text, message.chat.id, old_id, reply_markup=keyboard)
    except:
        msg = bot.edit_message_text("<b>Введите сумму которую хотите вывести\n\nВы должны ввести число</b>", message.chat.id, old_id)
        bot.register_next_step_handler(msg, withdraw_callback, msg.id)
    try:
        bot.delete_message(message.chat.id,message.id, timeout=10)
    except: ...


@bot.message_handler(['c'])
def get_money(message):
    if message.from_user.id != OWNER_ID: return 
    checks = post('https://pay.crypt.bot/api/getChecks', json={'asset': 'usdt', 'status': 'active'}, headers=headers).json()['result']['items']
    text = "<b>Вот все доступные чеки от бота:\n\n"
    for check in checks:
        url = check['bot_check_url']
        amount = float(check["amount"])
        text += f'\t<a href="{url}">{round(amount, 4)}$</a>\n'
    text += '</b>'
    bot.reply_to(message, text)


@bot.callback_query_handler(lambda call: call.data == "withdraw")
def withdraw(call: CallbackQuery):
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[3] < 0.1:
        bot.answer_callback_query(call.id, "Чтобы вывести USDT нужно как минимум 0.1$ на балансе", True)
    else:
        msg = bot.edit_message_text(f"<b>Введите сумму которую хотите вывести</b>", call.message.chat.id, call.message.id, reply_markup=cancel_kb())
        bot.register_next_step_handler(msg, withdraw_callback, msg.id)



@bot.callback_query_handler(lambda call: call.data == "upgrades")
def upgrades_(call: CallbackQuery):
    bot.edit_message_text("<b>Для более быстрого получения $EXL вы можете приобрести улучшения!\n\nПополните баланс и выбирайте улучшения</b>", call.message.chat.id, call.message.id, reply_markup=upgrades_kb())



@bot.callback_query_handler(lambda call: call.data.startswith("ppp"))
def ppp(call: CallbackQuery):
    upgrade = call.data.replace("ppp", "")
    desc = UPGRADES_TEXTS[upgrade][0]
    price = UPGRADES_TEXTS[upgrade][1]
    text = f"""<b>Улучшение: {upgrade}
Цена: {price}$

<blockquote>{desc}</blockquote>
</b>"""
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=ppp_kb())



@bot.callback_query_handler(lambda call: call.data == "upgrade_buy")
def upgrade_buy(call: CallbackQuery):
    upgrade = call.message.text.split("\n")[0].replace("Улучшение: ", "")
    price = UPGRADES_TEXTS[upgrade][1]
    username = call.from_user.username
    name = call.from_user.first_name
    data = get_data(call.from_user.id, username, name)
    if data[3] < price:
        bot.answer_callback_query(call.id, "Недостаточно средств. Пополните баланс и попробуйте снова!", True)
    else:
        cursor.execute("SELECT * FROM upgrades WHERE id=?", (call.from_user.id,))
        upgrades = cursor.fetchall()
        if len(active_upgrades_filter(upgrades)) > 1:
            bot.answer_callback_query(call.id, "К сожалению вы не можете приобрести третье усиление пока действуют ещё два. Дождитесь окончания усилений и попробуйте снова!", True)
        else:
            cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (price, call.from_user.id))
            cursor.execute("INSERT INTO upgrades VALUES (?,?,?)", (call.from_user.id, upgrade, time() + 24 * 60 * 60))
            con.commit()
            bot.answer_callback_query(call.id, f"Успешная покупка!\n\nПоздравляю с покупкой усиления {upgrade}", True)
            profile(call)



def deferredEarn(id, timeout, amount):
    if not timeout is None:
        sleep(timeout)
    TAP_COOLDOWN = randint(300, 600)
    yo = (time() + TAP_COOLDOWN, amount, id)
    cursor.execute("UPDATE users SET next_tap=?, quicoins=quicoins+? WHERE id=?", yo)
    try:
        bot.send_message(id, f"<b>Вы получили {amount} $EXL!</b>")
    except: ...


Thread(target=bot.infinity_polling).start()
while True:
    cursor.execute("SELECT * FROM upgrades WHERE name=?", ("auto",))
    autoearns = cursor.fetchall()
    for upgr in active_upgrades_filter(autoearns):
        while True:
            try:
                cursor.execute("SELECT * FROM users WHERE id=?", (upgr[0],))
                dt = cursor.fetchone()
                username = dt[1]
                name = dt[2]
                data = get_data(dt[0], username, name)
                break
            except:
                continue
        if data[7] is None or data[7] - time() < DEFER_COOLDOWN:
            cursor.execute("SELECT * FROM upgrades WHERE id=?", (upgr[0],))
            ups = cursor.fetchall()
            ups.remove(upgr)
            x = 1
            for d in ups:
                if "x" in d[1]:
                    x = int(d[1].replace("x", ""))
            amount = randint(150, 400) * x
            if data[7] is None:
                Thread(target=deferredEarn, args=(upgr[0], None, amount)).start()
            else:
                Thread(target=deferredEarn, args=(upgr[0], data[7] - time() - 0.5, amount)).start()
    sleep(DEFER_COOLDOWN - 10)
