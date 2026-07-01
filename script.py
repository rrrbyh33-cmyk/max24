import os
import time
import threading
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

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

def click_element_safely(driver, element):
    """
    النقر على العنصر بأمان
    """
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

# ==================== دوال البحث عن الخدمة ====================

def wait_for_page_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    """
    انتظار تحميل الصفحة
    """
    try:
        send_telegram_log("⏳ *جاري انتظار تحميل الصفحة...*")
        
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # التمرير لتحميل المحتوى
        send_telegram_log("📜 *جاري التمرير لتحميل المحتوى...*")
        for scroll in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        
        time.sleep(5)
        send_telegram_log("✅ *تم تحميل الصفحة بنجاح*")
        return True
    except Exception as e:
        send_telegram_log(f"⚠️ *خطأ في تحميل الصفحة: {str(e)[:50]}*")
        return False

def find_and_click_tiktok_service(driver):
    """
    البحث عن خدمة TikTok والنقر عليها (مرة واحدة فقط)
    """
    # أسماء الخدمات المطلوبة
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
            
            # البحث عن العنصر الذي يحتوي على النص
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{name}')]")
            
            for element in elements:
                if element.is_displayed():
                    send_telegram_log(f"✅ *تم العثور على الخدمة: {name[:30]}...*")
                    
                    # النقر على اسم الخدمة (مرة واحدة)
                    if click_element_safely(driver, element):
                        send_telegram_log("✅ *تم النقر على اسم الخدمة - جاري الانتقال إلى صفحة العداد...*")
                        return True
        except Exception as e:
            send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            continue
    
    return False

def wait_for_counter_page(driver, timeout=30):
    """
    انتظار ظهور صفحة العداد
    """
    try:
        send_telegram_log("⏳ *جاري انتظار ظهور صفحة العداد...*")
        
        # انتظار ظهور العداد
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'минут') or contains(text(), ':')]"))
        )
        
        time.sleep(3)
        send_telegram_log("✅ *تم الانتقال إلى صفحة العداد بنجاح*")
        return True
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة انتظار صفحة العداد*")
        return False

def find_link_input(driver):
    """
    البحث عن حقل إدخال الرابط
    """
    selectors = [
        "//input[@type='url']",
        "//input[contains(@placeholder, 'Ссылка')]",
        "//input[contains(@placeholder, 'Link')]",
        "//input[contains(@placeholder, 'https')]",
        "//input[@type='text']",
        "//input",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    placeholder = element.get_attribute("placeholder") or ""
                    if "поиск" not in placeholder.lower() and "بحث" not in placeholder.lower():
                        return element
        except:
            continue
    
    return None

def find_submit_button(driver):
    """
    البحث عن زر الإرسال
    """
    selectors = [
        "//button[@type='submit']",
        "//*[contains(text(), 'Заказать')]",
        "//*[contains(text(), 'заказать')]",
        "//*[contains(text(), 'Отправить')]",
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

# ==================== الوظيفة الأساسية ====================

def run_smm_automation(target_link, loop_count):
    send_telegram_log(f"🚀 *تم بدء نظام الأتمتة*\n🔗 المستهدف: {target_link}\n🔢 الوجبات المطلوبة: {loop_count}")
    
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
            send_telegram_log(f"🔄 *[الوجبة {i+1} من {loop_count}]:* جاري فتح الصفحة الرئيسية...")
            
            driver.set_page_load_timeout(TIMEOUT_CONFIG['page_load'])
            driver.get(TARGET_URL)
            
            # انتظار تحميل الصفحة
            wait_for_page_load(driver)
            
            # 🎯 الخطوة 1: البحث عن خدمة TikTok والنقر عليها (مرة واحدة)
            service_clicked = False
            
            try:
                send_telegram_log("🎯 *الخطوة 1: البحث عن خدمة TikTok والنقر عليها...*")
                service_clicked = find_and_click_tiktok_service(driver)
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            
            if not service_clicked:
                send_telegram_log("❌ *لم يتم العثور على خدمة TikTok!*")
                raise Exception("لم يتم العثور على خدمة TikTok")
            
            # 🎯 الخطوة 2: انتظار الانتقال إلى صفحة العداد
            time.sleep(5)
            
            # التبديل إلى النافذة الجديدة إذا فتحت
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    send_telegram_log("🔀 *تم التبديل إلى النافذة الجديدة*")
            except:
                pass
            
            # انتظار ظهور صفحة العداد
            if not wait_for_counter_page(driver):
                send_telegram_log("⚠️ *لم تظهر صفحة العداد، جاري المحاولة...*")
                time.sleep(5)
            
            current_url = driver.current_url
            send_telegram_log(f"🔗 *الصفحة الحالية:* `{current_url}`")
            
            # 🎯 الخطوة 3: انتظار 5 دقائق
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: جاري انتظار 5 دقائق...*")
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *متبقي {minutes_left} دقائق...*")
            time.sleep(60)
            
            send_telegram_log(f"⏱️ *انتهى وقت الانتظار للوجبة {i+1}!*")
            time.sleep(5)
            
            # 🎯 الخطوة 4: إدخال الرابط
            link_input = find_link_input(driver)
            
            if not link_input:
                send_telegram_log("❌ *لم نجد حقل الرابط!*")
                raise Exception("لم يتم العثور على حقل إدخال الرابط")
            
            try:
                driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
                send_telegram_log("✅ *تم إدخال الرابط*")
            except:
                link_input.send_keys(target_link)
                send_telegram_log("✅ *تم إدخال الرابط*")
            
            time.sleep(3)
            
            # 🎯 الخطوة 5: البحث عن زر الإرسال والنقر عليه
            submit_button = find_submit_button(driver)
            
            if not submit_button:
                send_telegram_log("❌ *لم نجد زر الإرسال!*")
                raise Exception("فشل العثور على زر الإرسال")
            
            if click_element_safely(driver, submit_button):
                send_telegram_log("✅ *تم النقر على زر الإرسال*")
            else:
                raise Exception("فشل النقر على زر الإرسال")
            
            time.sleep(8)
            
            # 🎯 الخطوة 6: التأكد من نجاح الطلب
            try:
                WebDriverWait(driver, TIMEOUT_CONFIG['success_check']).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'success') or contains(text(), 'успешно') or contains(text(), 'تم')]"))
                )
                send_telegram_log(f"✅ *[الوجبة {i+1}]: نجاح!*")
            except:
                send_telegram_log(f"⚠️ *[الوجبة {i+1}]: تم الإرسال*")
            
            # لقطة شاشة
            try:
                screenshot_path = f"success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[نجاح الوجبة {i+1}]*")
                os.remove(screenshot_path)
            except:
                pass
            
            send_telegram_log(f"✅ *[الوجبة {i+1}]: اكتملت*")
            time.sleep(5)
            
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

# ==================== دوال معالج البوت ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك في سيرفر التبويبات الذكية!*\n\nأرسل رابط الحساب:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text.startswith('http'))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
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
    threading.Thread(target=run_smm_automation, args=(target_link, loop_count)).start()
    bot.send_message(ADMIN_ID, f"⏳ *جاري تنفيذ {loop_count} وجبة...*")

# ==================== نقطة الدخول ====================

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    send_telegram_log("🚀 *السيرفر جاهز!*")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        send_telegram_log("🛑 *تم إيقاف السيرفر*")
        os._exit(0)
