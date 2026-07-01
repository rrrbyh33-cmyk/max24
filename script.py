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
    time.sleep(2400) 
    send_telegram_log("⚠️ *انتهت المدة المخصصة للسيرفر السحابي تلقائياً.*")
    os._exit(0)

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك يا علي في سيرفر التبويبات الذكية والمصححة الحين!*\n\nأرسل رابط الحساب هسة لكي ننطلق بدون خداع:")

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
    send_telegram_log(f"🚀 *تم بدء نظام الأتمتة وكشف التبويبات المخفية!*\n🔗 المستهدف: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        for i in range(loop_count):
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح الصفحة الرئيسية وتوليد الصلاحية...")
            driver.get(TARGET_URL)
            time.sleep(15)
            
            # العثور على كرت الخدمة
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
                raise Exception("فشل العثور على كرت الخدمة بالرئيسية.")

            # النقر للانتقال
            driver.execute_script("arguments[0].click();", order_button)
            time.sleep(8)
            
            # 🎯 التعديل الجوهري: الانتقال فوراً للتبويب الجديد إذا فتح الموقع نافذة ثانية!
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                
            # إرسال تقرير بالرابط الحالي للتأكد من العبور لصفحة العداد
            current_url = driver.current_url
            send_telegram_log(f"🔗 *المتصفح متواجد الآن في الرابط التالي للتحقق:* \n`{current_url}`")
            
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: بدأ العداد الكبير الحين بالصفحة الصحيحة...*\nجاري انتظار الـ 5 دقائق الإلزامية...")
            
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *مؤقت حي للوجبة {i+1}:* متبقي {minutes_left} دقائق ويفتح حقل الطلب...")
            time.sleep(60) 
            
            # الانتظار الـ 10 ثوانٍ الإضافية للأمان واستقرار الحقول
            send_telegram_log(f"⏱️ *انتهى وقت العداد للوجبة {i+1}!* جاري الانتظار 10 ثوانٍ للأمان الكامل...")
            time.sleep(10)
            
            # محاولة قراءة حقل الرابط داخل صفحة الخدمة حصراً وبشكل دقيق
            link_input = None
            selectors = [
                "//div[contains(@class, 'free')]//input", # حقل داخل حاوية الخدمة المجانية
                "//input[@type='url']", 
                "//input[contains(@placeholder, 'رابط')]", 
                "//input[@type='text' and not(contains(@placeholder, 'Поиск'))]" # استبعاد حقل البحث
            ]
            for selector in selectors:
                try:
                    link_input = driver.find_element(By.XPATH, selector)
                    if link_input: break
                except: continue
                
            if not link_input:
                # إذا فشل، نأخذ الحقل الأخير بالصفحة كخيار بديل
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                if all_inputs: link_input = all_inputs[-1]
            
            if not link_input:
                try:
                    fail_path = f"fail_{i+1}.png"
                    driver.save_screenshot(fail_path)
                    with open(fail_path, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption="❌ فشل رصد الحقل؛ شاهد شاشة المتصفح الحالية!")
                    os.remove(fail_path)
                except: pass
                raise Exception("لم يتم العثور على حقل إدخال الرابط.")

            # حقن الرابط
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: !0 }));", link_input)
            time.sleep(3)
            
            # الضغط على زر الطلب الأزرق بداخل الخدمة
            final_submit = None
            submit_selectors = [
                "//div[contains(@class, 'free')]//button", 
                "//button[@type='submit']", 
                "//*[contains(text(), 'طلب')]", 
                "//*[contains(text(), 'Заказать')]"
            ]
            for s_selector in submit_selectors:
                try:
                    final_submit = driver.find_element(By.XPATH, s_selector)
                    if final_submit: break
                except: continue
            if not final_submit: raise Exception("فشل العثور على زر الإطلاق النهائي.")
                
            driver.execute_script("arguments[0].click();", final_submit)
            time.sleep(6) # انتظار ظهور الصح الخضراء
            
            # لقطة شاشة للنجاح الحقيقي
            try:
                screenshot_path = f"final_success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[نجاح الوجبة {i+1}]:* شاهد إشعار قبول الطلب الأخضر الحقيقي الحين!")
                os.remove(screenshot_path)
            except Exception as e_img: print(f"Screenshot error: {e_img}")
                
            send_telegram_log(f"⏳ *[الوجبة {i+1}]:* اكتملت بنجاح وتثبتت.")
            time.sleep(5)
            
        send_telegram_log(f"🎉 *عاشت إيدك يا علي! اكتملت كافة الوجبات بنجاح ساحق وبدون أي خديعة من المتصفح!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي:* \n`{str(e)[:150]}`")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر السحابي المصحح بالتبويبات الحية مستيقظ الآن وجاهز!*")
    bot.infinity_polling()
