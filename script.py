import os
import time
import threading
import telebot
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

# مؤقت التدمير الذاتي لحماية دقائق جيت هاب المجانية (30 دقيقة)
def self_destruct():
    time.sleep(1800)
    send_telegram_log("⚠️ *انتهت الـ 30 دقيقة المخصصة للسيرفر السحابي.*")
    os._exit(0)

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك يا علي في السيرفر المقفل (متابعين تيك توك فقط)!*\n\nقم بإرسال رابط الحساب هسة لكي نطلق الرشق المباشر:")

# 1️⃣ استقبال الرابط والانتقال فوراً لطلب التكرار
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text.startswith('http'))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
    
    msg = bot.send_message(ADMIN_ID, "📥 *تم استلام رابط التيك توك بنجاح!*\n🔢 كم وجبة رشق تريد تكرارها؟ أرسل الرقم هسة:")
    bot.register_next_step_handler(msg, handle_loop_count)

# 2️⃣ استلام التكرار والتشغيل
def handle_loop_count(message):
    try:
        loop_count = int(message.text.strip())
        if loop_count < 1: loop_count = 1
    except:
        loop_count = 1
        
    target_link = user_states[ADMIN_ID]['link']
    threading.Thread(target=run_smm_automation, args=(target_link, loop_count)).start()

def run_smm_automation(target_link, loop_count):
    send_telegram_log(f"🚀 *تم إطلاق رشق متابعين التيك توك المباشر!*\n🔗 الحساب: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}")
    
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
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح الموقع واستهداف قسم التيك توك مباشرة...")
            driver.get(TARGET_URL)
            time.sleep(15)
            
            cards = driver.find_elements(By.XPATH, "//div[contains(., 'Заказать')]")
            order_button = None
            
            for card in cards:
                try: card_text = card.text.lower()
                except: continue
                
                if ("тик" in card_text or "tiktok" in card_text or "тт" in card_text) and "подписч" in card_text:
                    try:
                        order_button = card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать') or contains(., 'Заказать')]")
                        break
                    except: continue
            
            if not order_button:
                raise Exception("لم يتم العثور على زر متابعين تيك توك.")

            driver.execute_script("arguments[0].click();", order_button)
            
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]:* تم الدخول لخدمة المتابعين بنجاح.\nجاري انتظار الـ 5 دقائق الإجبارية...")
            time.sleep(300)
            
            # حقن الرابط الآمن عبر JavaScript
            link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            
            # 🛠️ تعديل ذكي ومضمون لتفادي خطأ الحروف الكبيرة تماماً في المتصفح
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: !0 }));", link_input)
            time.sleep(3)
            
            # النقر النهائي على زر التشغيل الروسي
            final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
            driver.execute_script("arguments[0].click();", final_submit)
            
            send_telegram_log(f"⏳ *[الوجبة {i+1}]:* تم إرسال طلب المتابعين بنجاح إلى النظام!")
            time.sleep(5)
            
        send_telegram_log(f"🎉 *كفو يا علي! اكتملت كافة الوجبات لمتابعين التيك توك بنجاح تام وعاش يدك!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي في سيرفر المتابعين:* \n`{str(e)[:150]}`")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *سيرفر متابعين التيك توك المقفل مستيقظ وجاهز الآن في تليغرام!*")
    bot.infinity_polling()
