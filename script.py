import os
import time
import threading
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BOT_TOKEN = "7331657801:AAHyHa5KHT8oPUD7GqZMx-g_S_bxNGchYWU"
ADMIN_ID = 6817750462
TARGET_URL = "https://smmnakrutka.ru/#bespli"

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}  # لحفظ روابط المستخدم مؤقتاً

def send_telegram_log(text):
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram error: {e}")

# ⏰ مؤقت التدمير الذاتي (30 دقيقة) لحماية دقائق جيت هاب المجانية
def self_destruct():
    time.sleep(1800)  # 30 دقيقة بالثواني
    send_telegram_log("⚠️ *انتهت الـ 30 دقيقة المخصصة للسيرفر السحابي.*\nتم إيقاف تشغيل البوت تلقائياً لحفظ دقائقك المجانية. يمكنك إعادة تشغيله من GitHub في أي وقت!")
    os._exit(0)

# رسالة ترحيبية عند الضغط على start
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "👋 *أهلاً بك يا علي في لوحة التحكم السحابية المباشرة!*\n\nقم بإرسال رابط الحساب أو المنشور (انستغرام أو تيك توك) هسة مباشرة لكي نبدأ الرشق السحابي المطور.")

# استقبال الرابط وتخزينه
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and (message.text.startswith('http') or 'tiktok.com' in message.text or 'instagram.com' in message.text))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
    
    # إنشاء أزرار اختيار الخدمة داخل التليغرام
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👥 متابعين انستغرام (Instagram Followers)", callback_data="ig_followers"),
        types.InlineKeyboardButton("👁️ مشاهدات انستغرام (Instagram Views)", callback_data="ig_views"),
        types.InlineKeyboardButton("👁️ مشاهدات تيك توك (TikTok Views)", callback_data="tt_views"),
        types.InlineKeyboardButton("👥 متابعين تيك توك (TikTok Followers)", callback_data="tt_followers")
    )
    bot.send_message(ADMIN_ID, "📥 *تم استلام الرابط بنجاح!*\nاختر الآن الخدمة المطلوبة من الأزرار أدناه:", reply_markup=markup)

# معالجة الضغط على أزرار الخدمات وبدء الرشق السحابي بالخلفية
@bot.callback_query_handler(func=lambda call: call.message.chat.id == ADMIN_ID)
def callback_inline(call):
    if ADMIN_ID not in user_states:
        bot.send_message(ADMIN_ID, "❌ حدث خطأ، يرجى إرسال الرابط من جديد.")
        return
    
    target_link = user_states[ADMIN_ID]['link']
    service_type = call.data
    
    # حذف الأزرار القديمة لإعلام المستخدم ببدء المعالجة
    bot.edit_message_reply_markup(chat_id=ADMIN_ID, message_id=call.message.message_id, reply_markup=None)
    
    # تشغيل عملية الرشق في Thread منفصل لكي يظل البوت مستيقظاً ويستقبل رسائل أخرى!
    threading.Thread(target=run_smm_automation, args=(target_link, service_type)).start()

def run_smm_automation(target_link, service_type):
    # 🛠️ قائمة ذكية بالصيغ المختلفة للتغلب على تحديثات الموقع وحساسية الحروف
    possible_texts = []
    if service_type == "ig_followers":
        possible_texts = ["подписчиков в Инстаграм", "Подписчики в Инстаграм", "Подписчиков в Инстаграм", "подписчики в инстаграм"]
    elif service_type == "ig_views":
        possible_texts = ["просмотров в Инстаграм", "Просмотры в Инстаграм", "Просмотров в Инстаграм", "просмотры в инстаграм"]
    elif service_type == "tt_views":
        possible_texts = ["просмотров в Тик Ток", "Просмотры в Тик Ток", "Просмотров в Тик Ток", "просмотры в тик ток", "Просмотры в ТТ"]
    elif service_type == "tt_followers":
        possible_texts = ["подписчиков в Тик Ток", "Подписчики в Тик Ток", "Подписчиков в Тик Ток", "подписчики в тик ток", "Подписчики в ТТ"]

    send_telegram_log(f"🔄 *جاري فتح المتصفح السحابي وضخ الهوية الحقيقية...*\n🔗 المستهدف: {target_link}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(TARGET_URL)
        time.sleep(15)
        
        # 🔄 حلقة ذكية لتجربة كافة صيغ النصوص المتاحة حتى نجد الزر الصحيح
        order_button = None
        for text_variant in possible_texts:
            try:
                xpath_selector = f"//*[contains(text(), '{text_variant}')]/..//*[contains(text(), 'Заказать')] | //*[contains(text(), '{text_variant}')]/ancestor::div//*[contains(text(), 'Заказать')]"
                order_button = driver.find_element(By.XPATH, xpath_selector)
                if order_button:
                    break
            except:
                continue
                
        if not order_button:
            raise Exception("لم يتم العثور على زر الخدمة؛ قد يكون الموقع غير الكلمات تماماً.")

        driver.execute_script("arguments[0].click();", order_button)
        
        send_telegram_log("⏱️ *تم العبور لصفحة الخدمة بنجاح.*\nجاري الآن انتظار الـ 5 دقائق الإجبارية للموقع... سأخبرك فور انتهائها.")
        time.sleep(300)
        
        # الحل الجذري لخطأ Element not interactable (الحقن المباشر عبر جافا سكربت)
        link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
        driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
        time.sleep(3)
        
        # الضغط على زر الإطلاق النهائي عبر جافا سكربت أيضاً لتجنب أي حجب
        final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
        driver.execute_script("arguments[0].click();", final_submit)
        
        send_telegram_log(f"🎉 *كفو يا علي! تم إرسال طلب الرشق بنجاح سحابي تام!*\n🎯 الرابط: {target_link}\n\n🤖 أنا جاهز الآن لاستقبال رابط آخر!")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي أثناء الرشق:* \n`{str(e)[:150]}`")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # تشغيل مؤقت التدمير الذاتي بالخلفية
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر السحابي الخارق مستيقظ الآن ويعمل بنجاح!*\nأرسل أي رابط في الشات وسأتولى الباقي.")
    bot.infinity_polling()
