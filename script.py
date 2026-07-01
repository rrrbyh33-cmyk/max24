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

# ==================== دوال البحث عن الخدمات ====================

def wait_for_page_full_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    """
    انتظار تحميل الصفحة بشكل كامل مع جميع العناصر
    """
    try:
        send_telegram_log("⏳ *جاري انتظار تحميل الصفحة...*")
        
        # انتظار تحميل الصفحة
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # التمرير للأسفل لتحميل المحتوى الديناميكي
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

def find_services_by_all_methods(driver):
    """
    البحث عن الخدمات باستخدام جميع الطرق الممكنة
    """
    services = []
    
    # الطريقة 1: البحث عن النصوص المحددة
    try:
        send_telegram_log("🔍 *البحث عن النصوص المحددة...*")
        keywords = [
            "бесплатных подписчиков",
            "бесплатных лайков",
            "бесплатных просмотров",
            "бесплатных комментариев"
        ]
        
        for keyword in keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
            for element in elements:
                if element.is_displayed():
                    services.append(element)
    except:
        pass
    
    # الطريقة 2: البحث عن أي عنصر يحتوي على "Заказать"
    try:
        send_telegram_log("🔍 *البحث عن أزرار 'Заказать'...*")
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать')]")
        for button in buttons:
            if button.is_displayed() and button.is_enabled():
                services.append(button)
    except:
        pass
    
    # الطريقة 3: البحث عن البطاقات
    try:
        send_telegram_log("🔍 *البحث عن البطاقات...*")
        xpath_patterns = [
            "//div[contains(@class, 'service')]",
            "//div[contains(@class, 'card')]",
            "//div[contains(@class, 'item')]",
            "//div[contains(@class, 'block')]",
            "//div[contains(@class, 'offer')]",
            "//div[contains(@class, 'product')]",
            "//div[contains(@style, 'service')]",
        ]
        
        for pattern in xpath_patterns:
            elements = driver.find_elements(By.XPATH, pattern)
            for element in elements:
                if element.is_displayed() and element.text and len(element.text) > 20:
                    services.append(element)
    except:
        pass
    
    # إزالة التكرارات
    unique_services = []
    seen = set()
    for service in services:
        try:
            service_text = service.text[:50] if service.text else ""
            if service_text and service_text not in seen:
                seen.add(service_text)
                unique_services.append(service)
        except:
            continue
    
    send_telegram_log(f"📊 *تم العثور على {len(unique_services)} عنصر خدمة*")
    return unique_services

def find_tiktok_followers_ultimate(driver):
    """
    الطريقة النهائية للبحث عن TikTok متابعين
    """
    # 1. البحث عن النص الدقيق
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
                if element.is_displayed():
                    send_telegram_log(f"✅ *تم العثور على النص: {text[:30]}...*")
                    
                    # البحث عن زر الطلب في نفس البطاقة
                    try:
                        # البحث عن البطاقة الأب
                        parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item')]")
                        if parent:
                            try:
                                button = parent.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                                return button
                            except:
                                buttons = parent.find_elements(By.TAG_NAME, "button")
                                if buttons:
                                    return buttons[0]
                    except:
                        # البحث عن زر قريب
                        try:
                            button = element.find_element(By.XPATH, "./following::*[contains(text(), 'Заказать')][1]")
                            return button
                        except:
                            pass
        except:
            continue
    
    # 2. البحث عن أي TikTok
    try:
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Тик Ток') or contains(text(), 'Ток')]")
        for element in elements:
            if element.is_displayed():
                parent_text = ""
                try:
                    parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card')]")
                    if parent:
                        parent_text = parent.text.lower()
                except:
                    pass
                
                if "подписчиков" in parent_text or "подписчик" in parent_text:
                    try:
                        parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card')]")
                        button = parent.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                        return button
                    except:
                        pass
    except:
        pass
    
    # 3. البحث عن أي زر "Заказать" (كحل أخير)
    try:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать')]")
        for button in buttons:
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
        pass
    
    return None

def find_link_input_final(driver):
    """
    البحث عن حقل الرابط
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
    البحث عن زر الإرسال
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
            
            # انتظار تحميل الصفحة مع التمرير
            wait_for_page_full_load(driver)
            
            # عرض محتوى الصفحة للتشخيص
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text[:500]
                send_telegram_log(f"📄 *محتوى الصفحة:* `{page_text[:200]}...`")
            except:
                pass
            
            # 🎯 البحث عن خدمة TikTok متابعين
            order_button = None
            
            # محاولة 1: البحث المباشر
            try:
                send_telegram_log("🔍 *جاري البحث عن خدمة TikTok متابعين...*")
                order_button = find_tiktok_followers_ultimate(driver)
                if order_button:
                    send_telegram_log("✅ *تم العثور على الخدمة المطلوبة!*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في البحث: {str(e)[:50]}*")
            
            # محاولة 2: البحث عن جميع الخدمات واختيار الأولى
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن جميع الخدمات...*")
                    services = find_services_by_all_methods(driver)
                    if services:
                        # البحث عن أول خدمة تحتوي على "Тик Ток" أو "Ток"
                        for service in services:
                            try:
                                service_text = service.text.lower()
                                if "тик ток" in service_text or "ток" in service_text:
                                    if "подписчиков" in service_text:
                                        try:
                                            button = service.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                                            order_button = button
                                            send_telegram_log("✅ *تم العثور على خدمة TikTok!*")
                                            break
                                        except:
                                            pass
                            except:
                                continue
                except:
                    pass
            
            # محاولة 3: البحث عن أي زر "Заказать"
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
                    pass
            
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
