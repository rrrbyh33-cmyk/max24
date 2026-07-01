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
send_telegram_log(f"🚀 جاري بدء الأتمتة السحابية على سيرفرات GitHub...\n🔗 الرابط المستهدف: {TARGET_LINK}\n🔢 عدد التكرارات المطلوبة: {LOOP_COUNT}")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

if SERVICE_TYPE == "ig_followers": keyword = "подписчиков в Инстаграм"
elif SERVICE_TYPE == "ig_views": keyword = "просмотров в Инстаграм"
elif SERVICE_TYPE == "tt_views": keyword = "просмотров в Тик Ток"
elif SERVICE_TYPE == "tt_followers": keyword = "подписчиков в Тик Ток"
else: keyword = "Заказать"

driver = None
try:
    # تشغيل متصفح كروم المدمج في خوادم جيت هاب بكفاءة عالية
    driver = webdriver.Chrome(options=chrome_options)
    
    for i in range(LOOP_COUNT):
        # تم تصحيح الكلمة هنا إلى LOOP_COUNT ليعبر السكربت بنجاح
        send_telegram_log(f"🔄 [الوجبة {i+1} من {LOOP_COUNT}]: جاري فتح الموقع الروسي...")
        driver.get(TARGET_URL)
        time.sleep(12)
        
        xpath_selector = f"//*[contains(text(), '{keyword}')]/..//*[contains(text(), 'Заказать')] | //*[contains(text(), '{keyword}')]/ancestor::div//*[contains(text(), 'Заказать')]"
        order_button = driver.find_element(By.XPATH, xpath_selector)
        driver.execute_script("arguments[0].click();", order_button)
        
        send_telegram_log(f"⏱️ [الوجبة {i+1}]: تم فتح صفحة الخدمة بنجاح. جاري انتظار الـ 5 دقائق الإجبارية للموقع...")
        time.sleep(300) # الانتظار البرمجي الآمن للموقع الروسي
        
        link_input = driver.find_element(By.XPATH, "//input[@type='url'] | //input[@type='text']")
        link_input.clear()
        link_input.send_keys(TARGET_LINK)
        time.sleep(2)
        
        final_submit = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //*[contains(text(), 'Запустить')]")
        driver.execute_script("arguments[0].click();", final_submit)
        
        send_telegram_log(f"⏳ [الوجبة {i+1}]: تم إرسال الطلب بنجاح وبدء الانتظار للوجبة التالية...")
        time.sleep(5)
        
    send_telegram_log(f"🎉 كفو يا علي! اكتملت الأتمتة السحابية بالكامل، وتم رشق الحساب {LOOP_COUNT} مرات بنجاح تام!")

except Exception as e:
    send_telegram_log(f"❌ خطأ سحابي أثناء الرشق: `{str(e)[:150]}`")
finally:
    if driver: driver.quit()
