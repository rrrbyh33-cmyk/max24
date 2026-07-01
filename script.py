import os
import time
import threading
import random
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# ==================== قائمة بروكسيات ====================
PROXY_LIST = [
    "http://103.152.112.157:80",
    "http://103.152.112.158:80",
    "http://103.152.112.159:80",
    "http://103.152.112.160:80",
    "http://103.152.112.161:80",
    "http://103.152.112.162:80",
]

# ==================== إعدادات البروكسي ====================
USE_PROXY = True
CURRENT_PROXY = None
PROXY_INDEX = 0

# ==================== إعدادات المهلات المركزية ====================
TIMEOUT_CONFIG = {
    'page_load': 60,
    'element_primary': 30,
    'element_secondary': 15,
    'element_short': 8,
    'window_switch': 20,
    'success_check': 15,
    'retry_attempts': 5,
    'page_load_extra': 15,
    'after_click_service': 5,
    'after_window_switch': 5,
    'after_submit': 10,          # زيادة من 8 إلى 10 ثوان
    'between_orders': 8,          # زيادة من 5 إلى 8 ثوان
    'before_link_input': 5,       # زيادة من 3 إلى 5 ثوان
    'after_link_input': 5,        # زيادة من 3 إلى 5 ثوان
    'counter_wait': 5,            # زيادة من 3 إلى 5 ثوان
    'after_confirmation': 5,      # وقت إضافي بعد التأكيد
    'wait_for_success_page': 12,  # وقت انتظار صفحة النجاح
}

# ==================== التوكنات والإعدادات ====================
BOT_TOKEN = "7331657801:AAHyHa5KHT8oPUD7GqZMx-g_S_bxNGchYWU"
ADMIN_ID = 6817750462
TARGET_URL = "https://smmnakrutka.ru/#bespli"

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# ==================== دوال المساعدة العامة ====================

def send_telegram_log(text):
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram error: {e}")

def self_destruct():
    time.sleep(2400) 
    send_telegram_log("⚠️ *انتهت المدة المخصصة للسيرفر السحابي تلقائياً.*")
    os._exit(0)

def get_current_proxy():
    global CURRENT_PROXY, PROXY_INDEX, PROXY_LIST
    if not USE_PROXY:
        return None
    if PROXY_LIST and PROXY_INDEX < len(PROXY_LIST):
        CURRENT_PROXY = PROXY_LIST[PROXY_INDEX]
        return CURRENT_PROXY
    return None

def get_next_proxy():
    global PROXY_INDEX, PROXY_LIST, CURRENT_PROXY
    if not PROXY_LIST:
        return None
    PROXY_INDEX = (PROXY_INDEX + 1) % len(PROXY_LIST)
    CURRENT_PROXY = PROXY_LIST[PROXY_INDEX]
    return CURRENT_PROXY

def get_previous_proxy():
    global PROXY_INDEX, PROXY_LIST, CURRENT_PROXY
    if not PROXY_LIST:
        return None
    PROXY_INDEX = (PROXY_INDEX - 1) % len(PROXY_LIST)
    CURRENT_PROXY = PROXY_LIST[PROXY_INDEX]
    return CURRENT_PROXY

def validate_tiktok_link(link):
    link = link.strip()
    if not link.startswith("https://"):
        link = "https://" + link
    if "tiktok.com" not in link:
        return None
    if "@" not in link and "vm." not in link and "vt." not in link:
        return None
    return link

def click_element_safely(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        try:
            element.click()
            return True
        except:
            try:
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                return True
            except:
                return False

def wait_for_stable_page(driver, timeout=10):
    try:
        old_html = driver.page_source
        time.sleep(2)
        new_html = driver.page_source
        return True
    except:
        return True

# ==================== دوال البحث عن الخدمة ====================

def wait_for_page_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    try:
        send_telegram_log("⏳ *جاري انتظار تحميل الصفحة...*")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        send_telegram_log("📜 *جاري التمرير لتحميل المحتوى...*")
        for scroll in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        wait_for_stable_page(driver)
        time.sleep(5)
        send_telegram_log("✅ *تم تحميل الصفحة بنجاح*")
        return True
    except Exception as e:
        send_telegram_log(f"⚠️ *خطأ في تحميل الصفحة: {str(e)[:50]}*")
        return False

def find_and_click_tiktok_service(driver):
    service_names = [
        "бесплатных подписчиков Тик Ток",
        "бесплатных подписчиков TikTok",
        "подписчиков Тик Ток",
        "подписчиков TikTok",
        "бесплатных просмотров Тик Ток",
        "бесплатных лайков Тик Ток"
    ]
    
    for name in service_names:
        try:
            send_telegram_log(f"🔍 *جاري البحث عن: {name}...*")
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{name}')]")
            for element in elements:
                if element.is_displayed():
                    send_telegram_log(f"✅ *تم العثور على الخدمة: {name[:30]}...*")
                    if click_element_safely(driver, element):
                        send_telegram_log("✅ *تم النقر على اسم الخدمة - جاري الانتقال إلى صفحة العداد...*")
                        time.sleep(TIMEOUT_CONFIG['after_click_service'])
                        return True
        except Exception as e:
            send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            continue
    return False

def wait_for_counter_page(driver, timeout=30):
    try:
        send_telegram_log("⏳ *جاري انتظار ظهور صفحة العداد...*")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'минут') or contains(text(), ':')]"))
        )
        time.sleep(TIMEOUT_CONFIG['after_window_switch'])
        wait_for_stable_page(driver)
        send_telegram_log("✅ *تم الانتقال إلى صفحة العداد بنجاح*")
        return True
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة انتظار صفحة العداد*")
        return False

def find_link_input_advanced(driver):
    selectors = [
        "//input[contains(@placeholder, 'Ссылка')]",
        "//input[contains(@placeholder, 'Link')]",
        "//input[contains(@placeholder, 'https')]",
        "//input[contains(@placeholder, 'tiktok')]",
        "//input[contains(@placeholder, 'аккаунт')]",
        "//input[@type='url']",
        "//input[@type='text']",
        "//input[contains(@name, 'link')]",
        "//input[contains(@name, 'url')]",
        "//input[contains(@id, 'link')]",
        "//input[contains(@id, 'url')]",
        "//input",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    placeholder = element.get_attribute("placeholder") or ""
                    element_type = element.get_attribute("type") or ""
                    if "поиск" in placeholder.lower() or "بحث" in placeholder.lower():
                        continue
                    if "email" in placeholder.lower() or "почта" in placeholder.lower():
                        continue
                    if "password" in element_type.lower():
                        continue
                    if element.get_attribute("hidden") == "true":
                        continue
                    return element
        except:
            continue
    return None

def find_submit_button(driver):
    selectors = [
        "//button[@type='submit']",
        "//*[contains(text(), 'Заказать')]",
        "//*[contains(text(), 'заказать')]",
        "//*[contains(text(), 'Отправить')]",
        "//*[contains(text(), 'Задать')]",
        "//button[contains(@class, 'btn')]",
        "//input[@type='submit']",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    return element
        except:
            continue
    return None

# ==================== دوال الأزرار ====================

def proxy_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_toggle = types.InlineKeyboardButton("🔄 تشغيل/إيقاف", callback_data="proxy_toggle")
    btn_next = types.InlineKeyboardButton("⏭️ بروكسي تالي", callback_data="proxy_next")
    btn_prev = types.InlineKeyboardButton("⏮️ بروكسي سابق", callback_data="proxy_prev")
    btn_status = types.InlineKeyboardButton("📊 الحالة", callback_data="proxy_status")
    btn_refresh = types.InlineKeyboardButton("🔄 تحديث القائمة", callback_data="proxy_refresh")
    btn_close = types.InlineKeyboardButton("❌ إغلاق", callback_data="proxy_close")
    keyboard.add(btn_toggle, btn_status)
    keyboard.add(btn_next, btn_prev)
    keyboard.add(btn_refresh)
    keyboard.add(btn_close)
    return keyboard

def show_proxy_menu():
    global USE_PROXY, CURRENT_PROXY, PROXY_INDEX, PROXY_LIST
    status = "🟢 مفعل" if USE_PROXY else "🔴 معطل"
    current = CURRENT_PROXY if CURRENT_PROXY else "لا يوجد"
    total = len(PROXY_LIST)
    index = PROXY_INDEX + 1 if PROXY_LIST else 0
    text = f"""
📡 *التحكم بالبروكسي*

📊 *الحالة:* {status}
🌐 *البروكسي الحالي:* `{current}`
📌 *الترتيب:* {index}/{total}
📋 *عدد البروكسيات:* {total}
"""
    return text

# ==================== معالج الأزرار ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global USE_PROXY, PROXY_INDEX, PROXY_LIST, CURRENT_PROXY
    
    if call.data == "proxy_toggle":
        USE_PROXY = not USE_PROXY
        if USE_PROXY and not CURRENT_PROXY and PROXY_LIST:
            CURRENT_PROXY = PROXY_LIST[0]
        bot.answer_callback_query(call.id, f"تم {'تفعيل' if USE_PROXY else 'تعطيل'} البروكسي")
        bot.edit_message_text(
            show_proxy_menu(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=proxy_menu_keyboard()
        )
    elif call.data == "proxy_next":
        if PROXY_LIST:
            PROXY_INDEX = (PROXY_INDEX + 1) % len(PROXY_LIST)
            CURRENT_PROXY = PROXY_LIST[PROXY_INDEX]
            bot.answer_callback_query(call.id, f"تم التبديل إلى: {CURRENT_PROXY}")
            bot.edit_message_text(
                show_proxy_menu(),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=proxy_menu_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, "لا يوجد بروكسيات!")
    elif call.data == "proxy_prev":
        if PROXY_LIST:
            PROXY_INDEX = (PROXY_INDEX - 1) % len(PROXY_LIST)
            CURRENT_PROXY = PROXY_LIST[PROXY_INDEX]
            bot.answer_callback_query(call.id, f"تم التبديل إلى: {CURRENT_PROXY}")
            bot.edit_message_text(
                show_proxy_menu(),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=proxy_menu_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, "لا يوجد بروكسيات!")
    elif call.data == "proxy_status":
        bot.answer_callback_query(call.id, "تم تحديث الحالة")
        bot.edit_message_text(
            show_proxy_menu(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=proxy_menu_keyboard()
        )
    elif call.data == "proxy_refresh":
        bot.answer_callback_query(call.id, "تم تحديث القائمة!")
        bot.edit_message_text(
            show_proxy_menu(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=proxy_menu_keyboard()
        )
    elif call.data == "proxy_close":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم إغلاق القائمة")
    elif call.data == "proxy_menu":
        bot.edit_message_text(
            show_proxy_menu(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=proxy_menu_keyboard()
        )
        bot.answer_callback_query(call.id)
    elif call.data == "start_work":
        bot.edit_message_text(
            "📝 *أرسل رابط الحساب:*\nمثال: `https://www.tiktok.com/@username`",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)

# ==================== دوال معالج البوت ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        keyboard = types.InlineKeyboardMarkup()
        btn_proxy = types.InlineKeyboardButton("📡 إعدادات البروكسي", callback_data="proxy_menu")
        btn_start = types.InlineKeyboardButton("🚀 بدء العمل", callback_data="start_work")
        keyboard.add(btn_proxy, btn_start)
        bot.send_message(
            ADMIN_ID,
            "🔒 *أهلاً بك في سيرفر التبويبات الذكية!*\n\n"
            "📝 *للبدء أرسل رابط الحساب:*\n"
            "مثال: `https://www.tiktok.com/@username`\n\n"
            "🔧 *للتحكم بالبروكسي اضغط على الزر أدناه*",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text.startswith('http'))
def handle_link(message):
    url = message.text.strip()
    validated_url = validate_tiktok_link(url)
    if not validated_url:
        bot.send_message(
            ADMIN_ID,
            "❌ *الرابط غير صحيح!*\n"
            "أرسل رابط TikTok صحيح مثل:\n"
            "`https://www.tiktok.com/@username`\n"
            "أو\n"
            "`https://vm.tiktok.com/xxxxx/`",
            parse_mode="Markdown"
        )
        return
    user_states[ADMIN_ID] = {'link': validated_url}
    msg = bot.send_message(ADMIN_ID, "📥 *تم استلام الرابط!*\n🔢 كم وجبة تريد؟")
    bot.register_next_step_handler(msg, handle_loop_count)

def handle_loop_count(message):
    try:
        loop_count = int(message.text.strip())
        if loop_count < 1:
            loop_count = 1
    except:
        loop_count = 1
    target_link = user_states[ADMIN_ID]['link']
    proxy_info = f"🌐 *البروكسي:* {'مفعل' if USE_PROXY else 'معطل'}"
    if USE_PROXY and CURRENT_PROXY:
        proxy_info += f"\n📡 *IP:* `{CURRENT_PROXY}`"
    bot.send_message(
        ADMIN_ID,
        f"⏳ *جاري تنفيذ {loop_count} وجبة...*\n\n{proxy_info}",
        parse_mode="Markdown"
    )
    threading.Thread(target=run_smm_automation, args=(target_link, loop_count)).start()

# ==================== الوظيفة الأساسية ====================

def run_smm_automation(target_link, loop_count):
    global USE_PROXY, CURRENT_PROXY
    
    proxy_status = "مع بروكسي" if USE_PROXY and CURRENT_PROXY else "بدون بروكسي"
    proxy_info = f" (IP: {CURRENT_PROXY})" if USE_PROXY and CURRENT_PROXY else ""
    
    send_telegram_log(f"🚀 *تم بدء نظام الأتمتة*\n🔗 المستهدف: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}\n🌐 *الحالة:* {proxy_status}{proxy_info}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if USE_PROXY and CURRENT_PROXY:
        chrome_options.add_argument(f'--proxy-server={CURRENT_PROXY}')
        send_telegram_log(f"🌐 *تم استخدام البروكسي:* `{CURRENT_PROXY}`")
    else:
        send_telegram_log("ℹ️ *تم التشغيل بدون بروكسي (IP مباشر)*")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        for i in range(loop_count):
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح الصفحة الرئيسية...")
            
            driver.set_page_load_timeout(TIMEOUT_CONFIG['page_load'])
            driver.get(TARGET_URL)
            
            wait_for_page_load(driver)
            
            # الخطوة 1: البحث عن خدمة TikTok
            service_clicked = False
            try:
                send_telegram_log("🎯 *الخطوة 1: البحث عن خدمة TikTok والنقر عليها...*")
                service_clicked = find_and_click_tiktok_service(driver)
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            
            if not service_clicked:
                send_telegram_log("❌ *لم يتم العثور على خدمة TikTok!*")
                raise Exception("لم يتم العثور على خدمة TikTok")
            
            time.sleep(TIMEOUT_CONFIG['after_click_service'])
            
            # الخطوة 2: التبديل إلى النافذة الجديدة
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    send_telegram_log("🔀 *تم التبديل إلى النافذة الجديدة*")
                    time.sleep(TIMEOUT_CONFIG['after_window_switch'])
                    wait_for_stable_page(driver)
            except:
                pass
            
            if not wait_for_counter_page(driver):
                send_telegram_log("⚠️ *لم تظهر صفحة العداد، جاري المحاولة...*")
                time.sleep(5)
            
            current_url = driver.current_url
            send_telegram_log(f"🔗 *الصفحة الحالية:* `{current_url}`")
            
            # الخطوة 3: انتظار 5 دقائق
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: جاري انتظار 5 دقائق...*")
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *متبقي {minutes_left} دقائق...*")
            time.sleep(60)
            
            send_telegram_log(f"⏱️ *انتهى وقت الانتظار للوجبة {i+1}!*")
            
            time.sleep(TIMEOUT_CONFIG['before_link_input'])
            wait_for_stable_page(driver)
            
            # الخطوة 4: البحث عن حقل الرابط
            send_telegram_log("🔍 *جاري البحث عن حقل الرابط...*")
            
            link_input = find_link_input_advanced(driver)
            if not link_input:
                try:
                    all_inputs = driver.find_elements(By.TAG_NAME, "input")
                    for inp in all_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            value = inp.get_attribute("value") or ""
                            if not value:
                                placeholder = inp.get_attribute("placeholder") or ""
                                if "поиск" not in placeholder.lower() and "بحث" not in placeholder.lower():
                                    if "email" not in placeholder.lower() and "почта" not in placeholder.lower():
                                        link_input = inp
                                        break
                except:
                    pass
            
            if not link_input:
                send_telegram_log("❌ *لم نجد حقل الرابط!*")
                raise Exception("لم يتم العثور على حقل إدخال الرابط")
            
            try:
                link_input.clear()
                time.sleep(1)
                driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
                send_telegram_log(f"✅ *تم إدخال الرابط: {target_link[:40]}...*")
            except:
                try:
                    link_input.clear()
                    link_input.send_keys(target_link)
                    send_telegram_log(f"✅ *تم إدخال الرابط: {target_link[:40]}...*")
                except Exception as e:
                    send_telegram_log(f"⚠️ *خطأ في إدخال الرابط: {str(e)[:50]}*")
                    raise Exception("فشل إدخال الرابط")
            
            time.sleep(TIMEOUT_CONFIG['after_link_input'])
            wait_for_stable_page(driver)
            
            # الخطوة 5: البحث عن زر الإرسال والنقر عليه
            send_telegram_log("🔍 *جاري البحث عن زر 'Заказать'...*")
            
            submit_button = None
            
            try:
                submit_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Заказать') or contains(text(), 'заказать') or contains(text(), 'Задать') or contains(text(), 'Отправить')]"))
                )
                send_telegram_log("✅ *تم العثور على زر 'Заказать'!*")
            except:
                pass
            
            if not submit_button:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if "заказать" in btn_text or "задать" in btn_text or "отправить" in btn_text:
                            if btn.is_displayed() and btn.is_enabled():
                                submit_button = btn
                                send_telegram_log(f"✅ *تم العثور على زر: {btn.text[:20]}*")
                                break
                except:
                    pass
            
            if not submit_button:
                send_telegram_log("❌ *لم نجد زر الإرسال!*")
                raise Exception("فشل العثور على زر الإرسال")
            
            if click_element_safely(driver, submit_button):
                send_telegram_log("✅ *تم النقر على زر 'Заказать'!*")
            else:
                raise Exception("فشل النقر على زر الإرسال")
            
            # ⏳ انتظار 10 ثوانٍ لظهور صفحة النجاح (زيادة من 8 إلى 10)
            send_telegram_log(f"⏳ *جاري انتظار ظهور صفحة التأكيد ({TIMEOUT_CONFIG['after_submit']} ثوان)...*")
            time.sleep(TIMEOUT_CONFIG['after_submit'])
            
            # 🎯 انتظار ظهور رسالة "Спасибо за доверие!"
            confirmation_received = False
            
            try:
                send_telegram_log("🔍 *جاري البحث عن رسالة 'Спасибо за доверие!'...*")
                
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Спасибо за доверие!') or contains(text(), 'спасибо')]"))
                )
                send_telegram_log("✅ *تم تأكيد الطلب! ظهور رسالة النجاح*")
                confirmation_received = True
                
                # انتظار إضافي بعد التأكيد
                time.sleep(TIMEOUT_CONFIG['after_confirmation'])
                
            except TimeoutException:
                send_telegram_log("⚠️ *لم نرى رسالة التأكيد، ولكن تم الإرسال*")
                confirmation_received = False
            
            # 📸 الخطوة 1: تصوير صفحة التأكيد
            try:
                # انتظار ثانية إضافية للتأكد من استقرار الصفحة
                time.sleep(2)
                
                screenshot_path = f"confirmation_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                
                status_text = "تم تأكيد الطلب ✅" if confirmation_received else "تم الإرسال ⚠️"
                caption = f"{'✅' if confirmation_received else '⚠️'} *[الوجبة {i+1}]: {status_text}*\n\n"
                caption += f"📋 *الرابط:* `{target_link}`\n"
                caption += f"⏱️ *الوقت:* {time.strftime('%H:%M:%S')}\n"
                caption += f"📊 *الحالة:* {'نجاح ✅' if confirmation_received else 'معلق ⚠️'}"
                
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=caption)
                os.remove(screenshot_path)
                send_telegram_log("📸 *تم إرسال صورة التأكيد*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في تصوير التأكيد: {str(e)[:50]}*")
            
            # ⏳ انتظار انتهاء العداد (5 ثوانٍ)
            try:
                send_telegram_log(f"⏳ *جاري انتظار انتهاء العداد ({TIMEOUT_CONFIG['counter_wait']} ثوان)...*")
                time.sleep(TIMEOUT_CONFIG['counter_wait'])
                send_telegram_log("✅ *انتهى العداد!*")
            except:
                pass
            
            # 📸 الخطوة 2: تصوير الصفحة النهائية بعد انتهاء العداد
            try:
                time.sleep(2)  # انتظار إضافي للتأكد من استقرار الصفحة
                
                screenshot_path = f"final_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                
                caption = f"✅ *[الوجبة {i+1}]: اكتملت العملية*\n\n"
                caption += f"📋 *الرابط:* `{target_link}`\n"
                caption += f"⏱️ *الوقت:* {time.strftime('%H:%M:%S')}\n"
                caption += f"📊 *الحالة النهائية:* {'نجاح كامل ✅' if confirmation_received else 'تم الإرسال ⚠️'}"
                
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=caption)
                os.remove(screenshot_path)
                send_telegram_log("📸 *تم إرسال صورة النتيجة النهائية*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في تصوير النتيجة النهائية: {str(e)[:50]}*")
            
            send_telegram_log(f"✅ *[الوجبة {i+1}]: اكتملت*")
            
            if i < loop_count - 1:
                send_telegram_log(f"⏳ *جاري الانتظار {TIMEOUT_CONFIG['between_orders']} ثوان قبل الوجبة التالية...*")
                time.sleep(TIMEOUT_CONFIG['between_orders'])
        
        send_telegram_log(f"🎉 *اكتملت جميع الوجبات!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ:* \n`{str(e)[:200]}`")
        try:
            error_screenshot = "final_error.png"
            driver.save_screenshot(error_screenshot)
            with open(error_screenshot, "rb") as photo:
                bot.send_photo(ADMIN_ID, photo, caption="❌ *حدث خطأ غير متوقع!*")
            os.remove(error_screenshot)
        except:
            pass
    finally:
        if driver:
            driver.quit()

# ==================== نقطة الدخول ====================

if __name__ == "__main__":
    if PROXY_LIST:
        CURRENT_PROXY = PROXY_LIST[0]
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر جاهز!*")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        send_telegram_log("🛑 *تم إيقاف السيرفر*")
        os._exit(0)
