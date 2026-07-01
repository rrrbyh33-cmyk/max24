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
    'page_load': 30,        # تحميل الصفحة
    'element_primary': 20,  # البحث الرئيسي عن العناصر
    'element_secondary': 10,# البحث الثانوي عن العناصر
    'element_short': 5,    # البحث السريع
    'window_switch': 15,   # تبديل النوافذ
    'success_check': 10,   # التحقق من النجاح
    'retry_attempts': 3,   # عدد محاولات إعادة البحث
}

# ==================== التوكنات والإعدادات ====================
BOT_TOKEN = "7331657801:AAHyHa5KHT8oPUD7GqZMx-g_S_bxNGchYWU"
ADMIN_ID = 6817750462
TARGET_URL = "https://smmnakrutka.ru/#bespli"

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# ==================== دوال المساعدة العامة ====================

def send_telegram_log(text):
    """إرسال رسالة سجل إلى المشرف"""
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram error: {e}")

def retry_with_timeout(func, driver, timeout=TIMEOUT_CONFIG['element_primary'], max_attempts=TIMEOUT_CONFIG['retry_attempts']):
    """تنفيذ دالة مع إعادة المحاولة في حال فشلت"""
    for attempt in range(max_attempts):
        try:
            result = func(driver, timeout=timeout)
            if result:
                return result
        except TimeoutException:
            if attempt == max_attempts - 1: raise
            continue
        except Exception:
            if attempt == max_attempts - 1: raise
            continue
    return None

def self_destruct():
    """إنهاء السيرفر بعد 40 دقيقة لحفظ الدقائق"""
    time.sleep(2400) 
    send_telegram_log("⚠️ *انتهت المدة المخصصة للسيرفر السحابي تلقائياً.*")
    os._exit(0)

# ==================== دوال البحث المطورة والمرنة ====================

def find_tiktok_service(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """
    البحث الدقيق والمطور عن خدمة TikTok متابعين بدون التقيد بكلاسات أو تاغات محددة
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Заказать') or contains(text(), 'طلب')]"))
        )
    except TimeoutException:
        raise TimeoutException("انتهت مهلة انتظار تحميل عناصر الصفحة")
    
    # استهداف عام وشامل لأي عنصر يحتوي على كلمات التيك توك والمتابعين معاً
    keywords_xpath = "//*[(contains(., 'тик') or contains(., 'tiktok') or contains(., 'тт')) and (contains(., 'подписч') or contains(., 'متابع'))]"
    elements = driver.find_elements(By.XPATH, keywords_xpath)
    
    for el in elements:
        try:
            # التسلق لأقرب حاوية كرت محيطة تمثل القسم
            parent = el.find_element(By.XPATH, "./ancestor::div[1] | ./ancestor::a[1]")
            
            # البحث عن الهدف القابل للنقر بمرونة تامة داخل الكرت
            click_targets = parent.find_elements(By.XPATH, ".//*[contains(text(), 'Заказать') or contains(text(), 'طلب') or @href or name()='button' or name()='a']")
            if click_targets:
                return click_targets[0]
                
            return parent
        except:
            continue
    return None

def find_tiktok_service_alternative(driver, timeout=TIMEOUT_CONFIG['element_secondary']):
    """طرق بديلة وعامية جداً للوصول لزر المتابعين عند فشل الطريقة الأولى"""
    xpath_patterns = [
        "//*[contains(., 'тик') and contains(., 'подписч')]//*[contains(text(), 'Заказать') or contains(text(), 'طلب')]",
        "//a[contains(., 'тик') and contains(., 'подписч')]",
        "//a[contains(., 'tiktok') and contains(., 'follower')]",
        "//*[contains(., 'тик') and contains(., 'подписч')]"
    ]
    for xpath in xpath_patterns:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if element and element.is_displayed():
                return element
        except:
            continue
    raise TimeoutException("انتهت مهلة البحث البديل الشامل عن الخدمة")

def find_link_input(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """البحث عن حقل إدخال الرابط مع مهلة محددة"""
    selectors = [
        "//div[contains(@class, 'free')]//input",
        "//input[@type='url']",
        "//input[contains(@placeholder, 'رابط')]",
        "//input[contains(@placeholder, 'Ссылка')]",
        "//input[contains(@placeholder, 'Link')]",
        "//input[@type='text' and not(contains(@placeholder, 'Поиск'))]",
        "//input[@type='text'][last()]"
    ]
    for selector in selectors:
        try:
            element = WebDriverWait(driver, min(timeout/3, TIMEOUT_CONFIG['element_short'])).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            if element and element.is_displayed():
                return element
        except:
            continue
    try:
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in reversed(all_inputs):
            if inp.is_displayed() and inp.is_enabled(): return inp
    except: pass
    raise TimeoutException("انتهت مهلة البحث عن حقل الرابط")

def find_submit_button(driver, timeout=TIMEOUT_CONFIG['element_primary']):
    """البحث عن زر الإرسال النهائي مع مهلة محددة"""
    selectors = [
        "//div[contains(@class, 'free')]//button",
        "//button[@type='submit']",
        "//*[contains(text(), 'طلب')]",
        "//*[contains(text(), 'Заказать')]",
        "//*[contains(text(), 'Submit')]",
        "//button[contains(@class, 'btn-primary') or contains(@class, 'btn-success')]",
        "//button[last()]"
    ]
    for selector in selectors:
        try:
            element = WebDriverWait(driver, min(timeout/3, TIMEOUT_CONFIG['element_short'])).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            if element and element.is_displayed(): return element
        except:
            continue
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                btn_text = btn.text.lower()
                if "заказать" in btn_text or "طلب" in btn_text or "submit" in btn_text:
                    if btn.is_displayed() and btn.is_enabled(): return btn
            except: continue
    except: pass
    raise TimeoutException("انتهت مهلة البحث عن زر الإرسال")

# ==================== الوظيفة الأساسية للأتمتة ====================

def run_smm_automation(target_link, loop_count):
    """الوظيفة الرئيسية لتشغيل أتمتة الخدمات بالترتيب الصحيح الحين"""
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
            
            driver.set_page_load_timeout(TIMEOUT_CONFIG['page_load'])
            driver.get(TARGET_URL)
            time.sleep(5) 
            
            # 🎯 البحث الدقيق المرن عن الخدمة مع إعادة المحاولة
            try:
                order_button = retry_with_timeout(find_tiktok_service, driver, timeout=TIMEOUT_CONFIG['element_primary'])
            except TimeoutException:
                send_telegram_log("⚠️ *انتهت مهلة البحث، جاري الانتقال للطريقة البديلة...*")
                try:
                    order_button = retry_with_timeout(find_tiktok_service_alternative, driver, timeout=TIMEOUT_CONFIG['element_secondary'], max_attempts=2)
                except TimeoutException:
                    order_button = None
            
            if not order_button:
                error_screenshot = f"error_service_not_found_{i+1}.png"
                driver.save_screenshot(error_screenshot)
                with open(error_screenshot, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption="❌ *فشل العثور على الخدمة الحين؛ راجع التصميم الحالي.*")
                os.remove(error_screenshot)
                raise Exception("لم يتم العثور على خدمة TikTok متابعين")

            # النقر والانتقال لصفحة العداد
            driver.execute_script("arguments[0].scrollIntoView(true);", order_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", order_button)
            
            # إدارة التبويبات المتعددة والتحول للنافذة النشطة
            try:
                WebDriverWait(driver, TIMEOUT_CONFIG['window_switch']).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])
                send_telegram_log("🔀 *تم كشف التبويب الجديد والتحول إليه بنجاح.*")
            except TimeoutException:
                send_telegram_log("ℹ️ *نواصل العمل في نفس التبويب المتاح الحين.*")
            
            current_url = driver.current_url
            send_telegram_log(f"🔗 *المتصفح متواجد الآن بالرابط للتحقق:* \n`{current_url}`")
            
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: بدأ العداد الكبير بالصفحة...*\nجاري انتظار الـ 5 دقائق الإلزامية في الخلفية.")
            
            # المؤقت الحي للتليغرام
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *مؤقت حي للوجبة {i+1}:* متبقي {minutes_left} دقائق ويفتح حقل الطلب...")
            time.sleep(60) 
            
            # الانتظار الـ 10 ثوانٍ الإضافية للأمان التام التي أضفتها أنت يا بطل
            send_telegram_log(f"⏱️ *انتهى وقت العداد للوجبة {i+1}!* جاري الانتظار 10 ثوانٍ للأمان واستقرار الحقول...")
            time.sleep(10)
            
            # البحث عن حقل الرابط
            try:
                link_input = find_link_input(driver, timeout=TIMEOUT_CONFIG['element_primary'])
            except TimeoutException:
                link_input = None
            
            if not link_input:
                error_screenshot = f"error_input_not_found_{i+1}.png"
                driver.save_screenshot(error_screenshot)
                with open(error_screenshot, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption="❌ *فشل رصد حقل إدخال الرابط بعد الـ 10 ثوانٍ!*")
                os.remove(error_screenshot)
                raise Exception("لم يتم العثور على حقل إدخال الرابط.")
            
            # حقن الرابط الآمن بالجافا سكربت
            driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: !0 }));", link_input)
            time.sleep(3)
            
            # البحث عن زر الإرسال النهائي وضغطه
            try:
                final_submit = find_submit_button(driver, timeout=TIMEOUT_CONFIG['element_primary'])
            except TimeoutException:
                final_submit = None
            
            if not final_submit: raise Exception("فشل العثور على زر الإطلاق النهائي.")
            
            driver.execute_script("arguments[0].scrollIntoView(true);", final_submit)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", final_submit)
            
            # فحص إشعار النجاح بالموقع
            try:
                WebDriverWait(driver, TIMEOUT_CONFIG['success_check']).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'success') or contains(text(), 'успешно') or contains(text(), 'طلب')]"))
                )
                send_telegram_log(f"✅ *[الوجبة {i+1}]: تم رصد إشعار النجاح الأخضر بالموقع الحين!*")
            except TimeoutException:
                send_telegram_log(f"⚠️ *[الوجبة {i+1}]: لم نرى علامة النجاح لكن تم إرسال النقرة بنجاح.*")
            
            time.sleep(6)
            
            # التقاط لقطة شاشة النجاح الصورية
            try:
                screenshot_path = f"final_success_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=f"✅ *[صورة الوجبة {i+1}]:* شاهد لقطة شاشة حالة الإطلاق الحالية الحين!")
                os.remove(screenshot_path)
            except Exception as e_img: print(f"Screenshot error: {e_img}")
                
            send_telegram_log(f"⏳ *[الوجبة {i+1}]:* اكتملت بنجاح كامل.")
            time.sleep(5)
            
        send_telegram_log(f"🎉 *عاشت إيدك يا علي! اكتملت كافة الوجبات المتكررة بنجاح ساحق ومثالي مئة بالمئة!*")
        
    except Exception as e:
        send_telegram_log(f"❌ *خطأ سحابي في السيرفر المقفل:* \n`{str(e)[:150]}`")
        try:
            error_screenshot = "final_error.png"
            driver.save_screenshot(error_screenshot)
            with open(error_screenshot, "rb") as photo:
                bot.send_photo(ADMIN_ID, photo, caption="❌ *لقطة حية للحالة عند حدوث الخطأ العام الحين!*")
            os.remove(error_screenshot)
        except: pass
    finally:
        if driver: driver.quit()

# ==================== دوال معالج البوت ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🔒 *أهلاً بك يا علي في النسخة الخارقة المطورة بيديك والمدعومة بالفحص الشامل العام الحين!*\n\nقم بإرسال رابط الحساب لكي ننطلق بدون أي مشاكل:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text.startswith('http'))
def handle_link(message):
    url = message.text.strip()
    user_states[ADMIN_ID] = {'link': url}
    
    msg = bot.send_message(ADMIN_ID, "📥 *تم استلام الرابط بنجاح!*\n🔢 كم وجبة رشق تريد تكرارها؟ أرسل الرقم هسة:")
    bot.register_next_step_handler(msg, handle_loop_count)

def handle_loop_count(message):
    try:
        loop_count = int(message.text.strip())
        if loop_count < 1: loop_count = 1
    except:
        loop_count = 1
        
    target_link = user_states[ADMIN_ID]['link']
    threading.Thread(target=run_smm_automation, args=(target_link, loop_count)).start()
    bot.send_message(ADMIN_ID, f"⏳ *جاري تشغيل الـ {loop_count} وجبة المتتالية سحابياً...*\nترقب تحديثات المؤقت واللقطات الحية الحين!")

if __name__ == "__main__":
    threading.Thread(target=self_destruct, daemon=True).start()
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        os._exit(0)
