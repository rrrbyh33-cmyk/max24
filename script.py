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
user_states = {}

def send_telegram_log(text):
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram error: {e}")

# مؤقت التدمير الذاتي (30 دقيقة) لحماية دقائق جيت هاب
def self_destruct():
    time.sleep(1800)
    send_telegram_log("⚠️ *انتهت الـ 30 دقيقة المخصصة للسيرفر السحابي.*\nتم إيقاف تشغيل البوت تلقائياً لحفظ دقائقك المجانية.")
    os._exit(0)

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "👋 *أهلاً بك يا علي في لوحة التحكم السحابية المباشرة!*\n\nقم بإرسال رابط الحساب أو المنشور هسة لكي نبدأ:")

# 1️⃣ استقبال الرابط
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and (message.text.startswith('http') or 'tiktok.com' in message.text or 'instagram.com' in message.text))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👥 متابعين انستغرام (Instagram Followers)", callback_data="ig_followers"),
        types.InlineKeyboardButton("👁️ مشاهدات انستغرام (Instagram Views)", callback_data="ig_views"),
        types.InlineKeyboardButton("👁️ مشاهدات تيك توك (TikTok Views)", callback_data="tt_views"),
        types.InlineKeyboardButton("👥 متابعين تيك توك (TikTok Followers)", callback_data="tt_followers")
    )
    bot.send_message(ADMIN_ID, "📥 *تم استلام الرابط!*\nاختر الآن الخدمة المطلوبة من الأزرار أدناه:", reply_markup=markup)

# 2️⃣ طلب التكرار
@bot.callback_query_handler(func=lambda call: call.message.chat.id == ADMIN_ID)
def callback_inline(call):
    if ADMIN_ID not in user_states:
        bot.send_message(ADMIN_ID, "❌ حدث خطأ، يرجى إرسال الرابط من جديد.")
        return
    
    user_states[ADMIN_ID]['service'] = call.data
    bot.edit_message_reply_markup(chat_id=ADMIN_ID, message_id=call.message.message_id, reply_markup=None)
    
    msg = bot.send_message(ADMIN_ID, "🔢 *كم وجبة رشق تريد تكرارها لهذا الرابط؟*\nأرسل الرقم هسة مباشرة (مثلاً: `1` أو `3`):")
    bot.register_next_step_handler(msg, handle_loop_count)

# 3️⃣ استلام التكرار والتشغيل بالخلفية
def handle_loop_count(message):
    try:
        loop_count = int(message.text.strip())
        if loop_count < 1: loop_count = 1
    except:
        bot.send_message(ADMIN_ID, "⚠️ تم تعيين التكرار تلقائياً إلى وجبة واحدة `1`.")
        loop_count = 1
        
    user_states[ADMIN_ID]['loops'] = loop_count
    target_link = user_states[ADMIN_ID]['link']
    service_type = user_states[ADMIN_ID]['service']
    
    threading.Thread(target=run_smm_automation, args=(target_link, service_type, loop_count)).start()

def run_smm_automation(target_link, service_type, loop_count):
    send_telegram_log(f"🚀 *تم بدء الرشق السحابي المتكرر!*\n🔗 المستهدف: {target_link}\n🔢 إجمالي الوجبات المطلوبة: {loop_count}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        for i in range(loop_count):
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فحص الصفحة والتسلق البرمجي للزر...")
            driver.get(TARGET_URL)
            time.sleep(15)
            
            # جلب كل أزرار الطلب في الصفحة
            all_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать') or contains(., 'Заказать')]")
            order_button = None
            
            for btn in all_buttons:
                current = btn
                context_text = ""
                # التسلق لـ 4 مستويات لأعلى لجمع نصوص الكرت بالكامل وتجنب حيل التحديثات
                for _ in range(4):
                    try:
                        current = current.find_element(By.XPATH, "..")
                        context_text += " " + current.text.lower()
                    except:
                        break
                
                # مطابقة الكلمات المفتاحية بمرونة تامة (عربي، روسي، إنجليزي)
                is_match = False
                if service_type == "ig_followers" and "инст" in context_text and "подпис" in context_text:
                    is_match = True
                elif service_type == "ig_views" and "инст" in context_text and ("просмотр" in context_text or "лайк" in context_text):
                    is_match = True
                elif service_type == "tt_views" and ("тик" in context_text or "tiktok" in context_text) and "просмотр" in context_text:
                    is_match = True
                elif service_type == "tt_followers" and ("тик" in context_text or "tiktok" in context_text) and "подпис" in context_text:
                    is_match = True
                    
                if is_match:
                    order_button = btn
                    break
                    
            if not order_button:
                raise Exception("واجهة الموقع تغيرت أو لم يتم العثور على القسم؛ تأكد من الخدمة المحددة.")

            driver.execute_script("arguments[0].click();", order_button)
            
            send_telegram_log(f"⏱️ *[الوجبة {i+1} من {loop_count}]:* تم العبور للخدمة.\nجاري انتظار الـ 5 دقائق الإجبارية للموقع...")
            time.sleep(300)
            
            # حقن الرابط الآمن عبر جافا سكربت
            link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
            time.sleep(3)
            
            # النقر النهائي الخفي
            final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
            driver.execute_script("arguments[0].click();", final_submit)
            
            send_telegram_log(f"⏳ *[الوجبة {i+1} من {loop_count}]:* تم إرسال طلب الرشق بنجاح سحابياً وعبر السيرفر!")
            time.sleep(5)
            
        send_telegram_log(f"🎉 *كفو يا علي! اكتملت كافة الوجبات المطلوبة ({loop_count}) بنجاح تام وعاش يدك!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي أثناء الرشق:* \n`{str(e)[:150]}`")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر السحابي الخارق مستيقظ الآن للتحكم الكامل المتكرر!*\nأرسل أي رابط في الشات وسأتولى الباقي.")
    bot.infinity_polling()
