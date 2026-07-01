import os
import time
import threading
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BOT_TOKEN = "7331657801:AAHyHa5KHT8oPUD7GqZMx-g_S_bxNGchYWU"
ADMIN_ID = 6817750462

# 🎯 الرابط الصحيح والمباشر مية بالمية من داخل متصفحك لخدمة التيك توك
TARGET_URL = "https://smmnakrutka.ru/free-tik"

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
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك يا علي في السيرفر المقفل بالرابط الصحيح المباشر!*\n\nأرسل رابط الحساب هسة لكي نبدأ:")

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
    send_telegram_log(f"🚀 *تم بدء الرشق المباشر والمضمون الحين!*\n🔗 المستهدف: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}")
    
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
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح صفحة الخدمة المستهدفة...")
            driver.get(TARGET_URL)
            time.sleep(10)
            
            # ⏱️ الانتظار الإجباري للعداد الكبير بداخل صفحة الخدمة المباشرة
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: العداد الكبير يعمل الآن بالصفحة...*\nالمتصفح صافن وينتظر انتهاء الـ 5 دقائق لظهور حقل الرابط والزر الأزرق.")
            
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *مؤقت حي للوجبة {i+1}:* متبقي {minutes_left} دقائق ويظهر حقل الطلب...")
            time.sleep(60) # الدقيقة الأخيرة
            
            # 🔥 الآن انطلق وحقن الرابط فوراً بعد انتهاء المؤقت وظهور الحقل
            send_telegram_log(f"🔥 *انتهى الانتظار للوجبة {i+1}!* جاري كتابة الرابط والضغط على زر طلب الأزرق...")
            
            link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text'] | //input[contains(@placeholder, 'رابط')]")
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: !0 }));", link_input)
            time.sleep(3)
            
            # الضغط المباشر على زر طلب الأزرق
            final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'طلب')] | //*[contains(text(), 'Заказать')]")
            driver.execute_script("arguments[0].click();", final_submit)
            time.sleep(5) # انتظار ظهور المربع الأخضر
            
            # 📸 التقاط الصورة وإرسالها لك لكي تشاهد المربع الأخضر بنفسك!
            try:
                screenshot_path = f"final_success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[نجاح الوجبة {i+1}]:* شاهد إشعار قبول الطلب الحقيقي من داخل صفحة الخدمة!")
                os.remove(screenshot_path)
            except Exception as e_img:
                print(f"Screenshot error: {e_img}")
                
            send_telegram_log(f"⏳ *[الوجبة {i+1}]:* اكتملت وجبتك بنجاح تام.")
            time.sleep(3)
            
        send_telegram_log(f"🎉 *عاشت إيدك يا علي! اكتملت كافة الوجبات بنجاح ساحق واستقرار 100% عبر الرابط الصحيح!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي في السيرفر المباشر:* \n`{str(e)[:150]}`")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر السحابي المقفل بالرابط المباشر الصحيح مستيقظ الآن وجاهز!*")
    bot.infinity_polling()
