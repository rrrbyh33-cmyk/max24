import time
import os
import threading
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

print("[1] جاري بدء تشغيل النظام وتحميل مكتبات الأتمتة...")

# بياناتك الجاهزة والمحمية
BOT_TOKEN = "7331657801:AAHyHa5KHT8oPUD7GqZMx-g_S_bxNGchYWU"
ADMIN_ID = 6817750462
TARGET_URL = "https://smmnakrutka.ru/#bespli"

bot = telebot.TeleBot(BOT_TOKEN, num_threads=30)
user_sessions = {}

def is_admin(chat_id):
    return chat_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_services(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.reply_to(message, "❌ عذراً، هذا البوت خاص ومحمي لمالكه فقط.")
        return
    
    bot.clear_step_handlers_by_chat_id(chat_id=chat_id)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("👥 10 متابعين مجانيين - انستغرام", callback_data="ig_followers")
    btn2 = types.InlineKeyboardButton("👁️ 100 مشاهدة مجانية - انستغرام", callback_data="ig_views")
    btn3 = types.InlineKeyboardButton("🎵 100 مشاهدة مجانية - تيك توك", callback_data="tt_views")
    btn4 = types.InlineKeyboardButton("👤 10 متابعين مجانيين - تيك توك", callback_data="tt_followers")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, "👋 مرحباً بك يا مالك البوت! اختر الخدمة المُراد أتمتتها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if not is_admin(call.message.chat.id): return
    bot.answer_callback_query(call.id)
    user_sessions[call.message.chat.id] = {'service': call.data}
    msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔗 أرسل الآن رابط الحساب أو المنشور المستهدف:")
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    chat_id = message.chat.id
    text = message.text
    if text and text.startswith('/'):
        bot.clear_step_handlers_by_chat_id(chat_id=chat_id)
        if text == '/start': send_services(message)
        return
    if not text or not text.startswith("http"):
        msg = bot.reply_to(message, "❌ عذراً، الرابط غير صحيح. أرسل رابطاً يبدأ بـ http:")
        bot.register_next_step_handler(msg, process_link)
        return
    user_sessions[chat_id]['link'] = text
    msg = bot.send_message(chat_id, "🔢 كم مرة تريد من البوت أن يعيد تكرار هذا الطلب؟ (مثال: 3)")
    bot.register_next_step_handler(msg, process_count_and_start)

def process_count_and_start(message):
    chat_id = message.chat.id
    text = message.text
    if text and text.startswith('/'):
        bot.clear_step_handlers_by_chat_id(chat_id=chat_id)
        if text == '/start': send_services(message)
        return
    try:
        loop_count = int(text)
    except (ValueError, TypeError):
        msg = bot.reply_to(message, "❌ يرجى إدخال رقم صحيح:")
        bot.register_next_step_handler(msg, process_count_and_start)
        return
    link = user_sessions[chat_id]['link']
    service_type = user_sessions[chat_id]['service']
    bot.send_message(chat_id, f"🚀 تم جدولة طلبك للتكرار {loop_count} مرات بنجاح وجاري تشغيل المتصفح السحابي...")
    threading.Thread(target=run_loop_automation, args=(link, service_type, loop_count, chat_id)).start()

def run_loop_automation(target_link, service_type, loop_count, chat_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    
    if service_type == "ig_followers": keyword = "подписчиков в Инстаграм"
    elif service_type == "ig_views": keyword = "просмотров в Инстаграм"
    elif service_type == "tt_views": keyword = "просмотров в Тик Ток"
    elif service_type == "tt_followers": keyword = "подписчиков в Тик Ток"
    else: keyword = "Заказать"

    try:
        # المحرك سيتعرف تلقائياً على حزمة selenium المثبتة بسيرفر Discloud
        driver = webdriver.Chrome(options=chrome_options)
        for i in range(loop_count):
            bot.send_message(chat_id, f"🔄 [الدورة {i+1} من {loop_count}]: جاري فتح موقع الرشق الروسي...")
            driver.get(TARGET_URL)
            time.sleep(12)
            
            xpath_selector = f"//*[contains(text(), '{keyword}')]/..//*[contains(text(), 'Заказать')] | //*[contains(text(), '{keyword}')]/ancestor::div//*[contains(text(), 'Заказать')]"
            order_button = driver.find_element(By.XPATH, xpath_selector)
            driver.execute_script("arguments[0].click();", order_button)
            
            bot.send_message(chat_id, f"⏱️ [الدورة {i+1}]: تم فتح صفحة الخدمة. جاري انتظار الـ 5 دقائق التلقائية للموقع...")
            time.sleep(300)
            
            link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
            link_input.clear()
            link_input.send_keys(target_link)
            time.sleep(2)
            
            final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
            driver.execute_script("arguments[0].click();", final_submit)
            
            bot.send_message(chat_id, f"⏳ [الدورة {i+1}]: تم إرسال الرابط بنجاح! جاري الانتظار مبرمجاً...")
            time.sleep(5)
        bot.send_message(chat_id, f"🎉 كفو يا علي! اكتملت العملية بالكامل وتم تكرار رشق طلبك {loop_count} مرات بنجاح تام!")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ بالمتصفح السحابي: `{str(e)[:120]}`")
    finally:
        if driver: driver.quit()

print("[2] البوت في وضع الاستماع اللانهائي والمستقر الآن...")
bot.polling(none_stop=True)
