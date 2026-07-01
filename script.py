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

def retry_with_timeout(func, driver, timeout=TIMEOUT_CONFIG['element_primary'], max_attempts=TIMEOUT_CONFIG['retry_attempts']):
    for attempt in range(max_attempts):
        try:
            result = func(driver, timeout=timeout)
            if result:
                return result
        except TimeoutException:
            if attempt == max_attempts - 1:
                raise
            continue
        except Exception:
            if attempt == max_attempts - 1:
                raise
            continue
    return None

def self_destruct():
    time.sleep(2400) 
    send_telegram_log("⚠️ *انتهت المدة المخصصة للسيرفر السحابي تلقائياً.*")
    os._exit(0)

# ==================== دوال البحث عن الخدمة (مُعدَّلة للخدمة الصحيحة) ====================

def find_tiktok_followers_service(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن خدمة TikTok متابعين المجانية بالضبط
    """
    # النص الدقيق للخدمة المطلوبة
    service_texts = [
        "10 бесплатных подписчиков Тик Ток",
        "бесплатных подписчиков Тик Ток",
        "подписчиков Тик Ток",
        "10 подписчиков Тик Ток",
        "бесплатных подписчиков",
        "подписчиков Тик Ток"
    ]
    
    try:
        # انتظار تحميل الصفحة
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item')]"))
        )
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة تحميل الصفحة*")
    
    # البحث عن جميع البطاقات
    service_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item') or contains(@class, 'block')]")
    
    # إذا لم نجد بطاقات، نبحث عن أي div يحتوي على النص المطلوب
    if not service_cards:
        service_cards = driver.find_elements(By.XPATH, "//div[contains(., 'подписчиков Тик Ток') or contains(., 'Тик Ток')]")
    
    send_telegram_log(f"🔍 *تم العثور على {len(service_cards)} بطاقة خدمة*")
    
    for idx, card in enumerate(service_cards):
        try:
            card_text = card.text.lower()
            
            # عرض النص للتشخيص
            if idx < 5:
                send_telegram_log(f"📋 *بطاقة {idx+1}:* `{card_text[:100]}...`")
            
            # التحقق من وجود النص المطلوب
            is_target_service = False
            for text in service_texts:
                if text.lower() in card_text:
                    is_target_service = True
                    break
            
            # تحقق إضافي: وجود كلمات مفتاحية
            has_followers = "подписчик" in card_text or "متابع" in card_text
            has_tiktok = "тик ток" in card_text or "tiktok" in card_text or "тт" in card_text
            has_free = "бесплат" in card_text or "مجاني" in card_text
            
            # إذا تطابق النص أو توفرت الكلمات المفتاحية
            if is_target_service or (has_followers and has_tiktok and has_free):
                send_telegram_log(f"✅ *تم العثور على الخدمة المطلوبة في البطاقة {idx+1}*")
                send_telegram_log(f"📋 *نص الخدمة:* `{card_text[:150]}...`")
                
                # البحث عن زر "Заказать"
                try:
                    order_button = card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать') or contains(text(), 'طلب')]")
                    return order_button
                except:
                    # البحث عن أي زر في البطاقة
                    try:
                        buttons = card.find_elements(By.TAG_NAME, "button")
                        if buttons:
                            return buttons[0]
                    except:
                        pass
                    
                    # البحث عن عنصر قابل للنقر
                    try:
                        clickable = card.find_element(By.XPATH, ".//a | .//div[contains(@class, 'btn')] | .//span[contains(@class, 'btn')]")
                        return clickable
                    except:
                        pass
        except Exception as e:
            continue
    
    return None

def find_service_by_text(driver, search_text, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن خدمة بنص محدد
    """
    try:
        # البحث المباشر عن النص
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{search_text}')]")
        
        for element in elements:
            try:
                # العثور على البطاقة الأب
                parent_card = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'service') or contains(@class, 'card') or contains(@class, 'item')]")
                if parent_card:
                    # البحث عن زر الطلب
                    try:
                        order_button = parent_card.find_element(By.XPATH, ".//*[contains(text(), 'Заказать') or contains(text(), 'طلب')]")
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

def find_any_service_with_order(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث عن أي خدمة تحتوي على زر طلب (كحل أخير)
    """
    try:
        # البحث عن أي زر "Заказать"
        order_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать') or contains(text(), 'طلب')]")
        
        for button in order_buttons:
            try:
                if button.is_displayed() and button.is_enabled():
                    return button
            except:
                continue
    except:
        pass
    
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
    
    # إذا فشل كل شيء، نأخذ جميع الحقول النصية
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
    
    # البحث عن أي زر يحتوي على كلمات طلب
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
            
            # انتظار تحميل الصفحة
            time.sleep(5)
            
            # 🎯 البحث عن خدمة TikTok متابعين المجانية
            order_button = None
            
            # محاولة 1: البحث عن الخدمة المطلوبة بالضبط
            try:
                send_telegram_log("🔍 *جاري البحث عن خدمة '10 бесплатных подписчиков Тик Ток'...*")
                order_button = retry_with_timeout(
                    find_tiktok_followers_service,
                    driver,
                    timeout=TIMEOUT_CONFIG['element_primary'],
                    max_attempts=2
                )
            except TimeoutException:
                send_telegram_log("⚠️ *انتهت مهلة البحث عن الخدمة المطلوبة*")
                order_button = None
            
            # محاولة 2: البحث بالنص المباشر
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث المباشر عن النص...*")
                    order_button = find_service_by_text(driver, "подписчиков Тик Ток")
                except:
                    order_button = None
            
            # محاولة 3: البحث عن أي خدمة بها زر طلب
            if not order_button:
                try:
                    send_telegram_log("🔍 *جاري البحث عن أي خدمة متاحة...*")
                    order_button = retry_with_timeout(
                        find_any_service_with_order,
                        driver,
                        timeout=TIMEOUT_CONFIG['element_secondary'],
                        max_attempts=2
                    )
                except:
                    order_button = None
            
            if not order_button:
                # حفظ صورة للخطأ
                error_screenshot = f"error_no_service_{i+1}.png"
                try:
                    driver.save_screenshot(error_screenshot)
                    with open(error_screenshot, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption="❌ *فشل العثور على الخدمة!*\nالخدمة المطلوبة: `10 бесплатных подписчиков Тик Ток`")
                    os.remove(error_screenshot)
                except:
                    pass
                raise Exception("لم يتم العثور على خدمة '10 бесплатных подписчиков Тик Тوك'")

            # النقر على الخدمة المختارة
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", order_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", order_button)
                send_telegram_log("✅ *تم النقر على الخدمة المختارة*")
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في النقر على الخدمة:* {str(e)[:50]}")
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
                        bot.send_photo(ADMIN_ID, photo, caption="❌ *فشل العثور على حقل إدخال الرابط!*")
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
                send_telegram_log(f"⚠️ *[الوجبة {i+1}]: لم نرى علامة النجاح ولكن تم الإرسال.*")
            
            # لقطة شاشة للنجاح
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
