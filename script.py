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
    'after_click_service': 5,
    'after_window_switch': 5,
    'after_submit': 8,
    'between_orders': 5,
    'before_link_input': 3,
    'after_link_input': 3,
    'counter_wait': 3,
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

def validate_tiktok_link(link):
    link = link.strip()
    if not link.startswith("https://"):
        link = "https://" + link
    if "tiktok.com" not in link:
        return None
    if "@" not in link and "vm." not in link and "vt." not in link:
        return None
    return link

def click_element_safely(driver, element):
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

def wait_for_stable_page(driver, timeout=10):
    try:
        old_html = driver.page_source
        time.sleep(2)
        new_html = driver.page_source
        return True
    except:
        return True

# ==================== دوال البحث عن الخدمة ====================

def wait_for_page_load(driver, timeout=TIMEOUT_CONFIG['page_load']):
    try:
        send_telegram_log("⏳ *جاري انتظار تحميل الصفحة...*")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        send_telegram_log("📜 *جاري التمرير لتحميل المحتوى...*")
        for scroll in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        wait_for_stable_page(driver)
        time.sleep(5)
        send_telegram_log("✅ *تم تحميل الصفحة بنجاح*")
        return True
    except Exception as e:
        send_telegram_log(f"⚠️ *خطأ في تحميل الصفحة: {str(e)[:50]}*")
        return False

def find_and_click_tiktok_service(driver):
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
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{name}')]")
            for element in elements:
                if element.is_displayed():
                    send_telegram_log(f"✅ *تم العثور على الخدمة: {name[:30]}...*")
                    if click_element_safely(driver, element):
                        send_telegram_log("✅ *تم النقر على اسم الخدمة - جاري الانتقال إلى صفحة العداد...*")
                        time.sleep(TIMEOUT_CONFIG['after_click_service'])
                        return True
        except Exception as e:
            send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            continue
    return False

def wait_for_counter_page(driver, timeout=30):
    try:
        send_telegram_log("⏳ *جاري انتظار ظهور صفحة العداد...*")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'минут') or contains(text(), ':')]"))
        )
        time.sleep(TIMEOUT_CONFIG['after_window_switch'])
        wait_for_stable_page(driver)
        send_telegram_log("✅ *تم الانتقال إلى صفحة العداد بنجاح*")
        return True
    except TimeoutException:
        send_telegram_log("⚠️ *انتهت مهلة انتظار صفحة العداد*")
        return False

# ==================== دوال البحث عن حقل الرابط ====================

def find_link_input_advanced(driver):
    selectors = [
        "//input[contains(@placeholder, 'Ссылка')]",
        "//input[contains(@placeholder, 'Link')]",
        "//input[contains(@placeholder, 'https')]",
        "//input[contains(@placeholder, 'tiktok')]",
        "//input[contains(@placeholder, 'аккаунт')]",
        "//input[@type='url']",
        "//input[@type='text']",
        "//input[contains(@name, 'link')]",
        "//input[contains(@name, 'url')]",
        "//input[contains(@id, 'link')]",
        "//input[contains(@id, 'url')]",
        "//input",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    placeholder = element.get_attribute("placeholder") or ""
                    element_type = element.get_attribute("type") or ""
                    if "поиск" in placeholder.lower() or "بحث" in placeholder.lower():
                        continue
                    if "email" in placeholder.lower() or "почта" in placeholder.lower():
                        continue
                    if "password" in element_type.lower():
                        continue
                    if element.get_attribute("hidden") == "true":
                        continue
                    return element
        except:
            continue
    return None

def find_link_input_by_scanning(driver):
    try:
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in all_inputs:
            if inp.is_displayed() and inp.is_enabled():
                placeholder = inp.get_attribute("placeholder") or ""
                input_type = inp.get_attribute("type") or ""
                if "url" in input_type or "text" in input_type:
                    if "поиск" not in placeholder.lower() and "بحث" not in placeholder.lower():
                        if "email" not in placeholder.lower() and "почта" not in placeholder.lower():
                            if "password" not in input_type.lower():
                                return inp
    except:
        pass
    return None

def find_submit_button(driver):
    selectors = [
        "//button[@type='submit']",
        "//*[contains(text(), 'Заказать')]",
        "//*[contains(text(), 'заказать')]",
        "//*[contains(text(), 'Отправить')]",
        "//*[contains(text(), 'Задать')]",
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
            
            wait_for_page_load(driver)
            
            # الخطوة 1: البحث عن خدمة TikTok والنقر عليها
            service_clicked = False
            try:
                send_telegram_log("🎯 *الخطوة 1: البحث عن خدمة TikTok والنقر عليها...*")
                service_clicked = find_and_click_tiktok_service(driver)
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ: {str(e)[:50]}*")
            
            if not service_clicked:
                send_telegram_log("❌ *لم يتم العثور على خدمة TikTok!*")
                raise Exception("لم يتم العثور على خدمة TikTok")
            
            time.sleep(TIMEOUT_CONFIG['after_click_service'])
            
            # الخطوة 2: التبديل إلى النافذة الجديدة
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    send_telegram_log("🔀 *تم التبديل إلى النافذة الجديدة*")
                    time.sleep(TIMEOUT_CONFIG['after_window_switch'])
                    wait_for_stable_page(driver)
            except:
                pass
            
            if not wait_for_counter_page(driver):
                send_telegram_log("⚠️ *لم تظهر صفحة العداد، جاري المحاولة...*")
                time.sleep(5)
            
            current_url = driver.current_url
            send_telegram_log(f"🔗 *الصفحة الحالية:* `{current_url}`")
            
            # الخطوة 3: انتظار 5 دقائق
            send_telegram_log(f"⏱️ *[الوجبة {i+1}]: جاري انتظار 5 دقائق...*")
            for minutes_left in range(4, 0, -1):
                time.sleep(60)
                send_telegram_log(f"⏳ *متبقي {minutes_left} دقائق...*")
            time.sleep(60)
            
            send_telegram_log(f"⏱️ *انتهى وقت الانتظار للوجبة {i+1}!*")
            
            time.sleep(TIMEOUT_CONFIG['before_link_input'])
            wait_for_stable_page(driver)
            
            # الخطوة 4: البحث عن حقل الرابط وإدخاله
            send_telegram_log("🔍 *جاري البحث عن حقل الرابط...*")
            
            link_input = find_link_input_advanced(driver)
            if not link_input:
                link_input = find_link_input_by_scanning(driver)
            
            if not link_input:
                try:
                    all_inputs = driver.find_elements(By.TAG_NAME, "input")
                    for inp in all_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            value = inp.get_attribute("value") or ""
                            if not value:
                                placeholder = inp.get_attribute("placeholder") or ""
                                if "поиск" not in placeholder.lower() and "بحث" not in placeholder.lower():
                                    if "email" not in placeholder.lower() and "почта" not in placeholder.lower():
                                        link_input = inp
                                        break
                except:
                    pass
            
            if not link_input:
                send_telegram_log("❌ *لم نجد حقل الرابط!*")
                raise Exception("لم يتم العثور على حقل إدخال الرابط")
            
            try:
                link_input.clear()
                time.sleep(1)
                driver.execute_script("arguments[0].value = arguments[1];", link_input, target_link)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", link_input)
                send_telegram_log(f"✅ *تم إدخال الرابط: {target_link[:40]}...*")
            except:
                try:
                    link_input.clear()
                    link_input.send_keys(target_link)
                    send_telegram_log(f"✅ *تم إدخال الرابط: {target_link[:40]}...*")
                except Exception as e:
                    send_telegram_log(f"⚠️ *خطأ في إدخال الرابط: {str(e)[:50]}*")
                    raise Exception("فشل إدخال الرابط")
            
            time.sleep(TIMEOUT_CONFIG['after_link_input'])
            wait_for_stable_page(driver)
            
            # الخطوة 5: البحث عن زر الإرسال والنقر عليه
            send_telegram_log("🔍 *جاري البحث عن زر 'Заказать'...*")
            
            submit_button = None
            
            try:
                submit_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Заказать') or contains(text(), 'заказать') or contains(text(), 'Задать') or contains(text(), 'Отправить')]"))
                )
                send_telegram_log("✅ *تم العثور على زر 'Заказать'!*")
            except:
                pass
            
            if not submit_button:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if "заказать" in btn_text or "задать" in btn_text or "отправить" in btn_text:
                            if btn.is_displayed() and btn.is_enabled():
                                submit_button = btn
                                send_telegram_log(f"✅ *تم العثور على زر: {btn.text[:20]}*")
                                break
                except:
                    pass
            
            if not submit_button:
                try:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Заказать') or contains(text(), 'Задать')]")
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            submit_button = element
                            send_telegram_log(f"✅ *تم العثور على عنصر: {element.text[:20]}*")
                            break
                except:
                    pass
            
            if not submit_button:
                send_telegram_log("❌ *لم نجد زر الإرسال!*")
                raise Exception("فشل العثور على زر الإرسال")
            
            if click_element_safely(driver, submit_button):
                send_telegram_log("✅ *تم النقر على زر 'Заказать'!*")
            else:
                raise Exception("فشل النقر على زر الإرسال")
            
            # ⏳ انتظار 8 ثوانٍ لظهور صفحة النجاح
            send_telegram_log("⏳ *جاري انتظار ظهور صفحة التأكيد (8 ثوان)...*")
            time.sleep(8)
            
            # الخطوة 6: انتظار ظهور رسالة "Спасибо за доверие!"
            try:
                send_telegram_log("🔍 *جاري البحث عن رسالة 'Спасибо за доверие!'...*")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Спасибо за доверие!') or contains(text(), 'спасибо')]"))
                )
                send_telegram_log("✅ *تم تأكيد الطلب! ظهور رسالة النجاح*")
            except TimeoutException:
                send_telegram_log("⚠️ *لم نرى رسالة التأكيد، ولكن تم الإرسال*")
            
            # الخطوة 7: انتظار انتهاء العداد (3 ثوانٍ)
            try:
                send_telegram_log("⏳ *جاري انتظار انتهاء العداد (3 ثوان)...*")
                time.sleep(TIMEOUT_CONFIG['counter_wait'])
                send_telegram_log("✅ *انتهى العداد!*")
            except:
                pass
            
            # الخطوة 8: التأكد من نجاح الطلب
            try:
                WebDriverWait(driver, TIMEOUT_CONFIG['success_check']).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'success') or contains(text(), 'успешно') or contains(text(), 'Спасибо')]"))
                )
                send_telegram_log(f"✅ *[الوجبة {i+1}]: نجاح!*")
            except:
                send_telegram_log(f"⚠️ *[الوجبة {i+1}]: تم الإرسال*")
            
            # 📸 الخطوة 9: التقاط صورة للنتيجة النهائية
            try:
                send_telegram_log("📸 *جاري التقاط صورة للنتيجة النهائية...*")
                
                # انتظار قليل للتأكد من استقرار الصفحة
                time.sleep(2)
                
                # التقاط الصورة
                screenshot_path = f"final_result_{i+1}.png"
                driver.save_screenshot(screenshot_path)
                
                # إرسال الصورة مع شرح
                caption = f"✅ *[نتيجة الوجبة {i+1}]*\n\n"
                caption += f"📋 *الحالة:* تم إكمال الطلب بنجاح ✅\n"
                caption += f"🔗 *الرابط:* `{target_link}`\n"
                caption += f"⏱️ *الوقت:* {time.strftime('%H:%M:%S')}\n\n"
                caption += f"📸 *صورة تأكيد الطلب*"
                
                with open(screenshot_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption=caption)
                
                # حذف الصورة بعد الإرسال
                os.remove(screenshot_path)
                send_telegram_log("✅ *تم إرسال صورة النتيجة*")
                
            except Exception as e:
                send_telegram_log(f"⚠️ *خطأ في التقاط الصورة: {str(e)[:50]}*")
            
            send_telegram_log(f"✅ *[الوجبة {i+1}]: اكتملت*")
            
            if i < loop_count - 1:
                send_telegram_log(f"⏳ *جاري الانتظار {TIMEOUT_CONFIG['between_orders']} ثوان قبل الوجبة التالية...*")
                time.sleep(TIMEOUT_CONFIG['between_orders'])
            
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
    validated_url = validate_tiktok_link(url)
    if not validated_url:
        bot.send_message(ADMIN_ID, "❌ *الرابط غير صحيح!*\nأرسل رابط TikTok صحيح مثل:\n`https://www.tiktok.com/@username`\nأو\n`https://vm.tiktok.com/xxxxx/`")
        return
    user_states[ADMIN_ID] = {'link': validated_url}
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
