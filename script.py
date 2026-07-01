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

# ==================== إعدادات المهلات المركزية ====================
TIMEOUT_CONFIG = {
    'page_load': 60,           # زيادة المهلة إلى 60 ثانية
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

# ==================== دوال البحث عن الخدمات (مُعاد تصميمها) ====================

def wait_for_page_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    """
    انتظار تحميل الصفحة بشكل كامل
    """
    try:
        send_telegram_log("⏳ *جاري انتظار تحميل الصفحة...*")
        
        # انتظار تحميل الجسم
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # انتظار تحميل أي عنصر يحتوي على نص
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'бесплатных') or contains(text(), 'подписчиков')]"))
        )
        
        # وقت إضافي
        time.sleep(TIMEOUT_CONFIG['page_load_extra'])
        
        send_telegram_log("✅ *تم تحميل الصفحة بنجاح*")
        return True
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة تحميل الصفحة*")
        return False

def find_all_services_simple(driver):
    """
    طريقة بسيطة للبحث عن الخدمات باستخدام نصوص محددة
    """
    services = []
    
    # البحث عن أي عنصر يحتوي على كلمات مفتاحية
    keywords = [
        "бесплатных подписчиков",
        "бесплатных лайков",
        "бесплатных просмотров",
        "бесплатных комментариев",
        "подписчиков Тик Ток",
        "подписчиков Ток",
        "лайков в Ютубе"
    ]
    
    for keyword in keywords:
        try:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
            for element in elements:
                try:
                    # العثور على البطاقة الأب
                    parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item') or contains(@class, 'block')]")
                    if parent:
                        services.append(parent)
                except:
                    # إذا لم نجد بطاقة، نأخذ العنصر نفسه
                    services.append(element)
        except:
            continue
    
    # إزالة التكرارات
    unique_services = []
    seen = set()
    for service in services:
        try:
            service_id = id(service)
            if service_id not in seen:
                seen.add(service_id)
                unique_services.append(service)
        except:
            continue
    
    return unique_services

def find_services_by_xpath(driver):
    """
    البحث عن الخدمات باستخدام XPath مختلف
    """
    services = []
    
    xpath_patterns = [
        "//div[contains(@class, 'service')]",
        "//div[contains(@class, 'card')]",
        "//div[contains(@class, 'item')]",
        "//div[contains(@class, 'block')]",
        "//div[contains(@class, 'service-item')]",
        "//div[contains(@class, 'service-card')]",
        "//div[contains(@class, 'offer')]",
        "//div[contains(@class, 'product')]",
        "//div[contains(@style, 'service')]",
        "//li[contains(@class, 'service')]"
    ]
    
    for pattern in xpath_patterns:
        try:
            elements = driver.find_elements(By.XPATH, pattern)
            for element in elements:
                try:
                    # التحقق من أن العنصر يحتوي على نص
                    if element.text and len(element.text) > 10:
                        services.append(element)
                except:
                    continue
        except:
            continue
    
    # إزالة التكرارات
    unique_services = []
    seen = set()
    for service in services:
        try:
            service_id = id(service)
            if service_id not in seen:
                seen.add(service_id)
                unique_services.append(service)
        except:
            continue
    
    return unique_services

def find_tiktok_service_final(driver):
    """
    الطريقة النهائية للبحث عن خدمة TikTok متابعين
    """
    # أولاً: البحث عن النص الدقيق
    target_texts = [
        "100 бесплатных подписчиков Ток",
        "10 бесплатных подписчиков Тик Ток",
        "бесплатных подписчиков Тик Ток",
        "подписчиков Тик Ток",
        "подписчиков Ток"
    ]
    
    for text in target_texts:
        try:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            for element in elements:
                try:
                    # البحث عن زر الطلب
                    try:
                        # البحث عن زر في نفس المستوى أو الأعلى
                        parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card')]")
                        if parent:
                            try:
                                button = parent.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                                return button
                            except:
                                buttons = parent.find_elements(By.TAG_NAME, "button")
                                if buttons:
                                    return buttons[0]
                    except:
                        # إذا لم نجد بطاقة، نبحث عن زر قريب
                        try:
                            button = element.find_element(By.XPATH, "./following::*[contains(text(), 'Заказать')][1]")
                            return button
                        except:
                            pass
                except:
                    continue
        except:
            continue
    
    # ثانياً: البحث عن أي خدمة TikTok
    try:
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Тик Ток') or contains(text(), 'Ток')]")
        for element in elements:
            try:
                parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card')]")
                if parent:
                    card_text = parent.text.lower()
                    if "подписчиков" in card_text:
                        try:
                            button = parent.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                            return button
                        except:
                            buttons = parent.find_elements(By.TAG_NAME, "button")
                            if buttons:
                                return buttons[0]
            except:
                continue
    except:
        pass
    
    # ثالثاً: البحث عن أي زر "Заказать"
    try:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать')]")
        for button in buttons:
            try:
                if button.is_displayed() and button.is_enabled():
                    # التحقق من أن الزر ليس في Instagram
                    parent_text = ""
                    try:
                        parent = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card')]")
                        if parent:
                            parent_text = parent.text.lower()
                    except:
                        pass
                    
                    if "инстаграм" not in parent_text and "instagram" not in parent_text:
                        return button
            except:
                continue
    except:
        pass
    
    return None

def find_link_input_final(driver):
    """
    الطريقة النهائية للبحث عن حقل الرابط
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
                try:
                    if element.is_displayed() and element.is_enabled():
                        # التحقق من أن الحقل ليس حقل بحث
                        placeholder = element.get_attribute("placeholder") or ""
                        if "поиск" not in placeholder.lower() and "بحث" not in placeholder.lower():
                            return element
                except:
                    continue
        except:
            continue
    
    return None

def find_submit_button_final(driver):
    """
    الطريقة النهائية للبحث عن زر الإرسال
    """
    selectors = [
        "//button[@type='submit']",
        "//*[contains(text(), 'Заказать')]",
        "//*[contains(text(), 'طلب')]",
        "//button[contains(@class, 'btn')]",
        "//input[@type='submit']",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                try:
                    if element.is_displayed() and element.is_enabled():
                        return element
                except:
                    continue
        except:
            continue
    
    return None

# ==================== الوظيفة الأساسية للأتمتة ====================

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
            if not wait_for_page_load(driver):
                send_telegram_log("⚠️ *الصفحة لم تتحمل بالكامل، جاري المحاولة...*")
                time.sleep(10)
            
            # 🎯 البحث عن خدمة TikTok متابعين
            order_button = None
            
            # محاولة 1: البحث المباشر عن الخدمة
            try:
                send_telegram_log("🔍 *جاري البحث عن خدمة TikTok متابعين...*")
                order_button = find_tiktok_service_final(driver)
                if order_button:
                    send_telegram_log("✅ *تم العثور على الخدمة المطلوبة!*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في البحث: {str(e)[:50]}*")
                order_button = None
            
            # محاولة 2: البحث عن أي زر "Заказать" (كحل أخير)
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن أي زر طلب...*")
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать')]")
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            order_button = btn
                            send_telegram_log("✅ *تم العثور على زر طلب*")
                            break
                except:
                    order_button = None
            
            if not order_button:
                send_telegram_log("❌ *لم يتم العثور على أي خدمة!*")
                
                # حفظ صورة للخطأ
                try:
                    error_screenshot = f"error_{i+1}.png"
                    driver.save_screenshot(error_screenshot)
                    with open(error_screenshot, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption="❌ *لم نجد أي خدمة في الصفحة!*")
                    os.remove(error_screenshot)
                except:
                    pass
                
                raise Exception("لم يتم العثور على أي خدمة")
            
            # النقر على الخدمة
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", order_button)
                time.sleep(2)
                driver.execute_script("arguments[0].click();", order_button)
                send_telegram_log("✅ *تم النقر على الخدمة*")
            except:
                try:
                    order_button.click()
                except:
                    raise Exception("فشل النقر على الخدمة")
            
            # انتظار فتح النافذة الجديدة
            time.sleep(8)
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    send_telegram_log("🔀 *تم التبديل إلى النافذة الجديدة*")
            except:
                pass
            
            current_url = driver.current_url
            send_telegram_log(f"🔗 *الصفحة الحالية:* `{current_url}`")
            
            # انتظار 5 دقائق
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: جاري انتظار 5 دقائق...*")
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *متبقي {minutes_left} دقائق...*")
            time.sleep(60)
            
            send_telegram_log(f"⏱️ *انتهى وقت الانتظار للوجبة {i+1}!*")
            time.sleep(10)
            
            # ✅ البحث عن حقل الرابط
            link_input = find_link_input_final(driver)
            
            if not link_input:
                send_telegram_log("❌ *لم نجد حقل الرابط!*")
                raise Exception("لم يتم العثور على حقل إدخال الرابط")
            
            # إدخال الرابط
            try:
                driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
                send_telegram_log("✅ *تم إدخال الرابط*")
            except:
                link_input.send_keys(target_link)
            
            time.sleep(3)
            
            # ✅ البحث عن زر الإرسال
            final_submit = find_submit_button_final(driver)
            
            if not final_submit:
                raise Exception("فشل العثور على زر الإرسال")
            
            # النقر على زر الإرسال
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_submit)
                time.sleep(2)
                driver.execute_script("arguments[0].click();", final_submit)
                send_telegram_log("✅ *تم النقر على زر الإرسال*")
            except:
                try:
                    final_submit.click()
                except:
                    raise Exception("فشل النقر على زر الإرسال")
            
            time.sleep(8)
            
            # ✅ التأكد من نجاح الطلب
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
