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
    'page_load': 30,
    'element_primary': 20,
    'element_secondary': 10,
    'element_short': 5,
    'window_switch': 15,
    'success_check': 10,
    'retry_attempts': 3,
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

# ==================== دوال البحث عن الخدمة ====================

def wait_for_services_to_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    """
    انتظار تحميل الخدمات بشكل صحيح
    """
    try:
        # انتظار ظهور عنصر الخدمات
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'service') or contains(@class, 'card')]"))
        )
        time.sleep(3)  # انتظار إضافي للتأكد من التحميل الكامل
        return True
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة تحميل الخدمات*")
        return False

def find_real_services(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن الخدمات الحقيقية فقط (تجاهل العناصر الوهمية)
    """
    # النصوص المطلوبة للخدمات الحقيقية
    valid_keywords = [
        "подписчиков", "лайков", "просмотров", "комментариев",
        "подписчик", "лайк", "просмотр", "комментарий"
    ]
    
    # البحث عن جميع البطاقات
    all_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item')]")
    
    real_services = []
    for card in all_cards:
        try:
            card_text = card.text
            # التحقق من أن البطاقة تحتوي على نص حقيقي
            has_valid_text = any(keyword in card_text for keyword in valid_keywords)
            # التحقق من وجود زر "Заказать"
            has_order_button = False
            try:
                button = card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                has_order_button = True
            except:
                pass
            
            if has_valid_text and has_order_button:
                real_services.append(card)
        except:
            continue
    
    return real_services

def find_service_by_position_enhanced(driver, position=6, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن الخدمة حسب ترتيبها في القائمة (فقط الخدمات الحقيقية)
    """
    # انتظار تحميل الصفحة
    wait_for_services_to_load(driver, timeout)
    
    # الحصول على الخدمات الحقيقية فقط
    real_services = find_real_services(driver)
    
    send_telegram_log(f"🔍 *تم العثور على {len(real_services)} خدمة حقيقية*")
    
    # عرض أول 10 خدمات للتشخيص
    for idx, card in enumerate(real_services[:10]):
        try:
            card_text = card.text.replace('\n', ' ').strip()
            send_telegram_log(f"📋 *الخدمة {idx+1}:* `{card_text[:60]}...`")
        except:
            pass
    
    # اختيار الخدمة حسب الموقع
    if len(real_services) >= position:
        target_card = real_services[position - 1]  # 0-indexed
        card_text = target_card.text.replace('\n', ' ').strip()
        send_telegram_log(f"✅ *تم اختيار الخدمة رقم {position}:* `{card_text[:80]}...`")
        
        # البحث عن زر الطلب في البطاقة
        try:
            order_button = target_card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
            return order_button
        except:
            buttons = target_card.find_elements(By.TAG_NAME, "button")
            if buttons:
                return buttons[0]
    
    return None

def find_service_by_exact_text(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن الخدمة بالنص الدقيق
    """
    # النصوص المطلوبة
    target_texts = [
        "100 бесплатных подписчиков Ток",
        "10 бесплатных лайков в Ютубе",
        "10 бесплатных комментариев Ток"
    ]
    
    try:
        for text in target_texts:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            for element in elements:
                try:
                    parent_card = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item')]")
                    if parent_card:
                        send_telegram_log(f"✅ *تم العثور على الخدمة:* `{text}`")
                        try:
                            order_button = parent_card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
                            return order_button
                        except:
                            buttons = parent_card.find_elements(By.TAG_NAME, "button")
                            if buttons:
                                return buttons[0]
                except:
                    continue
    except:
        pass
    
    return None

def find_any_real_service(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن أي خدمة حقيقية (كحل أخير)
    """
    real_services = find_real_services(driver)
    
    if real_services:
        send_telegram_log(f"✅ *تم العثور على {len(real_services)} خدمة حقيقية*")
        target_card = real_services[0]  # أول خدمة
        try:
            order_button = target_card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать')]")
            return order_button
        except:
            buttons = target_card.find_elements(By.TAG_NAME, "button")
            if buttons:
                return buttons[0]
    
    return None

def find_link_input_enhanced(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث المحسّن عن حقل إدخال الرابط
    """
    selectors = [
        "//input[@type='url']",
        "//input[contains(@placeholder, 'رابط')]",
        "//input[contains(@placeholder, 'Ссылка')]",
        "//input[contains(@placeholder, 'Link')]",
        "//input[contains(@placeholder, 'https')]",
        "//input[contains(@id, 'link') or contains(@id, 'url')]",
        "//input[contains(@name, 'link') or contains(@name, 'url')]",
        "//input[@type='text' and not(contains(@placeholder, 'Поиск')) and not(contains(@placeholder, 'بحث'))]",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    return element
        except:
            continue
    
    try:
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in all_inputs:
            try:
                if inp.is_displayed() and inp.is_enabled():
                    input_type = inp.get_attribute("type")
                    if input_type in ["text", "url", None]:
                        return inp
            except:
                continue
    except:
        pass
    
    return None

def find_submit_button_enhanced(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث المحسّن عن زر الإرسال النهائي
    """
    selectors = [
        "//button[@type='submit']",
        "//*[contains(text(), 'Заказать') and not(contains(@class, 'disabled'))]",
        "//*[contains(text(), 'طلب') and not(contains(@class, 'disabled'))]",
        "//button[contains(@class, 'btn-primary') or contains(@class, 'btn-success')]",
        "//button[contains(@class, 'order') or contains(@class, 'submit')]",
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
    
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                btn_text = btn.text.lower()
                if any(word in btn_text for word in ["заказать", "طلب", "order", "submit"]):
                    if btn.is_displayed() and btn.is_enabled():
                        return btn
            except:
                continue
    except:
        pass
    
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
            
            # انتظار تحميل الصفحة بشكل كامل
            if not wait_for_services_to_load(driver):
                send_telegram_log("⚠️ *الخدمات لم تتحمل بالكامل، جاري المحاولة مرة أخرى...*")
                time.sleep(5)
            
            # 🎯 البحث عن الخدمة
            order_button = None
            
            # محاولة 1: البحث عن الخدمة حسب الترتيب (الخدمة رقم 5 أو 6)
            try:
                send_telegram_log("🔍 *جاري البحث عن الخدمة رقم 5 (TikTok متابعين)...*")
                order_button = find_service_by_position_enhanced(driver, position=5)
                if order_button:
                    send_telegram_log("✅ *تم اختيار الخدمة رقم 5 (TikTok متابعين)!*")
            except:
                order_button = None
            
            # محاولة 2: البحث عن الخدمة رقم 6 (YouTube Likes)
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن الخدمة رقم 6...*")
                    order_button = find_service_by_position_enhanced(driver, position=6)
                    if order_button:
                        send_telegram_log("✅ *تم اختيار الخدمة رقم 6!*")
                except:
                    order_button = None
            
            # محاولة 3: البحث بالنص الدقيق
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن الخدمة بالنص الدقيق...*")
                    order_button = find_service_by_exact_text(driver)
                except:
                    order_button = None
            
            # محاولة 4: البحث عن أي خدمة حقيقية (كحل أخير)
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن أي خدمة حقيقية...*")
                    order_button = find_any_real_service(driver)
                except:
                    order_button = None
            
            if not order_button:
                send_telegram_log("❌ *لم يتم العثور على أي خدمة حقيقية!*")
                error_screenshot = f"error_no_service_{i+1}.png"
                try:
                    driver.save_screenshot(error_screenshot)
                    with open(error_screenshot, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption="❌ *لم نجد أي خدمة حقيقية!*")
                    os.remove(error_screenshot)
                except:
                    pass
                raise Exception("لم يتم العثور على أي خدمة")
            
            # النقر على الخدمة المختارة
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", order_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", order_button)
                send_telegram_log("✅ *تم النقر على الخدمة المختارة*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في النقر:* {str(e)[:50]}")
                try:
                    order_button.click()
                except:
                    raise Exception("فشل النقر على الخدمة")
            
            # انتظار فتح النافذة الجديدة
            time.sleep(5)
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
            link_input = find_link_input_enhanced(driver)
            
            if not link_input:
                error_screenshot = f"error_no_input_{i+1}.png"
                try:
                    driver.save_screenshot(error_screenshot)
                    with open(error_screenshot, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption="❌ *فشل العثور على حقل الرابط!*")
                    os.remove(error_screenshot)
                except:
                    pass
                raise Exception("لم يتم العثور على حقل إدخال الرابط.")
            
            # حقن الرابط
            try:
                driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
                send_telegram_log("✅ *تم إدخال الرابط بنجاح*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في إدخال الرابط:* {str(e)[:50]}")
                link_input.send_keys(target_link)
            
            time.sleep(3)
            
            # ✅ البحث عن زر الإرسال
            final_submit = find_submit_button_enhanced(driver)
            
            if not final_submit:
                raise Exception("فشل العثور على زر الإرسال.")
            
            # النقر على زر الإرسال
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_submit)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", final_submit)
                send_telegram_log("✅ *تم النقر على زر الإرسال*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في النقر على زر الإرسال:* {str(e)[:50]}")
                try:
                    final_submit.click()
                except:
                    raise Exception("فشل النقر على زر الإرسال")
            
            time.sleep(6)
            
            # ✅ التأكد من نجاح الطلب
            try:
                WebDriverWait(driver, TIMEOUT_CONFIG['success_check']).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'success') or contains(text(), 'успешно') or contains(text(), 'تم')]"))
                )
                send_telegram_log(f"✅ *[الوجبة {i+1}]: تم تأكيد نجاح الطلب!*")
            except TimeoutException:
                send_telegram_log(f"⚠️ *[الوجبة {i+1}]: تم الإرسال.*")
            
            # لقطة شاشة
            try:
                screenshot_path = f"success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[نجاح الوجبة {i+1}]*")
                os.remove(screenshot_path)
            except:
                pass
            
            send_telegram_log(f"✅ *[الوجبة {i+1}]: اكتملت بنجاح*")
            time.sleep(5)
            
        send_telegram_log(f"🎉 *اكتملت جميع الوجبات بنجاح!*")
        
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
