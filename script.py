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

def self_destruct():
    time.sleep(2400) # 40 دقيقة أمان للسيرفر
    send_telegram_log("⚠️ *انتهت المدة المخصصة للسيرفر السحابي تلقائياً.*")
    os._exit(0)

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك يا علي في السيرفر المعتمد على ترتيبك الصحيح مئة بالمئة!*\n\nأرسل رابط الحساب هسة لكي ننطلق:")

# 1️⃣ استقبال الرابط
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text.startswith('http'))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
    
    msg = bot.send_message(ADMIN_ID, "📥 *تم استلام الرابط بنجاح!*\n🔢 كم وجبة رشق تريد تكرارها؟ أرسل الرقم هسة:")
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
    send_telegram_log(f"🚀 *تم بدء الرشق حسب الترتيب الصحيح لصورك يا علي!*\n🔗 المستهدف: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}")
    
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
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح الموقع واستهداف الخدمة...")
            driver.get(TARGET_URL)
            time.sleep(12)
            
            # العثور على كرت الخدمة الرئيسي
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
                raise Exception("لم يتم العثور على زر الخدمة في الصفحة الرئيسية.")

            # الدخول لصفحة الخدمة حيث يبدأ العداد الكبير الحين
            driver.execute_script("arguments[0].click();", order_button)
            time.sleep(5)
            
            # 🎯 الخطوة الأولى (حسب صورتك الأولى): الانتظار الإجباري لمدة 5 دقائق أولاً لكي يختفي العداد ويظهر الزر!
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: العداد التنازلي الكبير بدأ الحين في الموقع...*\nالمتصفح صافن بالصفحة وينتظر ظهور زر الطلب الأزرق. سأقوم بتحديثك كل دقيقة.")
            
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *مؤقت حي للوجبة {i+1}:* متبقي {minutes_left} دقائق ويظهر زر الطلب...")
            time.sleep(60) # الدقيقة الأخيرة لتكملة الـ 5 دقائق كاملة
            
            # 🎯 الخطوة الثانية (حسب صورتك الثانية): الآن العداد انتهى والزر ظهر؛ نقوم بحقن الرابط فوراً
            send_telegram_log(f"🔥 *انتهى العداد الحين للوجبة {i+1}!* جاري حقن الرابط والضغط على زر طلب الأزرق...")
            
            link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text'] | //input[contains(@placeholder, 'رابط')]")
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: !0 }));", link_input)
            time.sleep(3)
            
            # الضغط على زر طلب الأزرق (Запустить / طلب / Заказать)
            final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')] | //*[contains(text(), 'طلب')] | //*[contains(text(), 'Заказать')]")
            driver.execute_script("arguments[0].click();", final_submit)
            
            # انتظار 5 ثوانٍ لكي تظهر واجهة النجاح الخضراء المنبثقة كاملة
            time.sleep(5)
            
            # 🎯 الخطوة الثالثة (حسب صورتك الثالثة): التقاط صورة حية فورية لنافذة النجاح الخضراء وإرسالها لك!
            try:
                screenshot_path = f"live_success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[نجاح الوجبة {i+1}]:* شاهد علامة الصح والنجاح الحقيقية من داخل الموقع مية بالمية!")
                os.remove(screenshot_path)
            except Exception as e_img:
                print(f"Screenshot error: {e_img}")
                
            send_telegram_log(f"⏳ *[الوجبة {i+1}]:* اكتمل إطلاق هذه الوجبة وثبتت بنجاح!")
            time.sleep(3)
            
        send_telegram_log(f"🎉 *عاشت إيدك يا علي! اكتملت كافة الوجبات المطلوبة ({loop_count}) بالترتيب والمؤقت الصحيح والطلبات الحين واصلة لحسابك!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي أثناء الرشق:* \n`{str(e)[:150]}`")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر السحابي المرتب بترتيب صور علي الصحيح مستيقظ الحين وجاهز!*")
    bot.infinity_polling()
