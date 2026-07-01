import os
import time
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# سحب البيانات البرمجية تلقائياً من السيرفر
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TARGET_LINK = os.getenv("TARGET_LINK")
SERVICE_TYPE = os.getenv("SERVICE_TYPE")
LOOP_COUNT = int(os.getenv("LOOP_COUNT", 1))

TARGET_URL = "https://smmnakrutka.ru/#bespli"
bot = telebot.TeleBot(BOT_TOKEN)

def send_telegram_log(text):
    try:
        bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print(f"Telegram error: {e}")

# إشعار بدء التشغيل السحابي
send_telegram_log(f"🚀 جاري بدء الأتمتة السحابية الذكية...\n🔗 المستهدف: {TARGET_LINK}\n🔢 الوجبات: {LOOP_COUNT}")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 🛠️ تحديثات ذهبية لتخطي الحماية وأبعاد الشاشة الكاملة
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

if SERVICE_TYPE == "ig_followers": keyword = "подписчиков в Инстаграм"
elif SERVICE_TYPE == "ig_views": keyword = "просмотров в Инстаграм"
elif SERVICE_TYPE == "tt_views": keyword = "просмотров в Тик Ток"
elif SERVICE_TYPE == "tt_followers": keyword = "подписчиков в Тик Ток"
else: keyword = "Заказать"

driver = None
try:
    driver = webdriver.Chrome(options=chrome_options)
    
    for i in range(LOOP_COUNT):
        send_telegram_log(f"🔄 [الوجبة {i+1} من {LOOP_COUNT}]: جاري فتح الموقع وضخ الهوية الحقيقية...")
        driver.get(TARGET_URL)
        time.sleep(15)  # زيادة وقت الانتظار لتحميل الصفحة بالكامل
        
        # محاولة البحث عن الزر بمرونة أعلى
        xpath_selector = f"//*[contains(text(), '{keyword}')]/..//*[contains(text(), 'Заказать')] | //*[contains(text(), '{keyword}')]/ancestor::div//*[contains(text(), 'Заказать')]"
        order_button = driver.find_element(By.XPATH, xpath_selector)
        driver.execute_script("arguments[0].click();", order_button)
        
        send_telegram_log(f"⏱️ [الوجبة {i+1}]: تم العبور لصفحة الخدمة بنجاح. جاري انتظار الـ 5 دقائق الإجبارية...")
        time.sleep(300)
        
        link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
        link_input.clear()
        link_input.send_keys(TARGET_LINK)
        time.sleep(3)
        
        final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
        driver.execute_script("arguments[0].click();", final_submit)
        
        send_telegram_log(f"⏳ [الوجبة {i+1}]: تم إرسال الطلب بنجاح والانتقال للوجبة التالية...")
        time.sleep(5)
        
    send_telegram_log(f"🎉 كفو يا علي! اكتملت الأتمتة السحابية بالكامل وتم الرشق {LOOP_COUNT} مرات بنجاح!")

except Exception as e:
    # إرسال تفاصيل أدق للتأكد إذا كان السبب حظر Cloudflare
    error_msg = str(e)[:150]
    send_telegram_log(f"❌ خطأ في العثور على العناصر السحابية:\n`{error_msg}`\n💡 إذا تكرر الخطأ، فهذا يعني أن جدار حماية الموقع حظر الآيبي الخاص بسيرفر GitHub.")
finally:
    if driver: driver.quit()
