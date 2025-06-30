"""
Browser Manager Module
Handles all browser setup, connection, and basic operations
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserManager:
    def __init__(self, selenium_ports=[30479, 30444, 4444]):
        self.selenium_ports = selenium_ports
        self.driver = None

    def setup_driver(self):
        """Use proven remote Selenium setup"""
        try:
            print("🔧 Setting up with proven remote Selenium...")
            
            if self.connect():
                print("✅ Connected to remote Selenium successfully!")
                return True
            else:
                print("❌ Could not connect to remote Selenium")
                return False
                
        except Exception as e:
            print(f"❌ Remote Selenium setup failed: {e}")
            return False

    def connect(self):
        """Try remote Selenium first, then fallback to local headless Chromium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Speed up by not loading images
        chrome_options.add_argument("--disable-javascript")  # Optional: disable JS if not needed

        # Try remote Selenium first
        for port in self.selenium_ports:
            try:
                print(f"🔍 Trying to connect to remote Selenium at port {port}...")
                self.driver = webdriver.Remote(
                    command_executor=f'http://localhost:{port}/wd/hub',
                    options=chrome_options
                )
                print(f"✅ Connected to remote Selenium on port {port}")
                return True
            except Exception as e:
                print(f"❌ Remote port {port} failed: {str(e)[:100]}...")

        # Fallback options in order of preference
        fallback_options = [
            self._try_local_chrome_with_chromedriver,
            self._try_local_chromium,
            self._try_firefox_fallback
        ]
        
        for fallback in fallback_options:
            try:
                if fallback(chrome_options):
                    return True
            except Exception as e:
                print(f"❌ Fallback failed: {str(e)[:100]}...")
                continue
        
        print("❌ All browser connection attempts failed")
        return False
    
    def _try_local_chrome_with_chromedriver(self, chrome_options):
        """Try local Chrome with ChromeDriver"""
        print("🔄 Trying local Chrome with system ChromeDriver...")
        from selenium.webdriver.chrome.service import Service
        
        # Try different common ChromeDriver paths
        chromedriver_paths = [
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver", 
            "/opt/chromedriver",
            "chromedriver"  # In PATH
        ]
        
        for path in chromedriver_paths:
            try:
                service = Service(path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"✅ Successfully launched Chrome with ChromeDriver at {path}")
                return True
            except Exception:
                continue
        return False
    
    def _try_local_chromium(self, chrome_options):
        """Try local Chromium"""
        print("🔄 Trying local Chromium...")
        
        # Try different Chromium binary paths
        chromium_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/opt/chromium/chromium"
        ]
        
        for path in chromium_paths:
            try:
                chrome_options.binary_location = path
                self.driver = webdriver.Chrome(options=chrome_options)
                print(f"✅ Successfully launched Chromium at {path}")
                return True
            except Exception:
                continue
        return False
    
    def _try_firefox_fallback(self, chrome_options):
        """Last resort: try Firefox"""
        print("🔄 Last resort: trying Firefox...")
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            
            self.driver = webdriver.Firefox(options=firefox_options)
            print("✅ Successfully launched Firefox")
            return True
        except Exception:
            return False

    def quit(self):
        """Close the browser"""
        if self.driver:
            print("🔒 Closing browser...")
            self.driver.quit()

    def get_driver(self):
        """Get the WebDriver instance"""
        return self.driver

    def take_screenshot(self, filename):
        """Take a screenshot for debugging"""
        if self.driver:
            try:
                self.driver.save_screenshot(filename)
                print(f"📸 Screenshot saved: {filename}")
                return True
            except Exception as e:
                print(f"Failed to save screenshot: {e}")
                return False
        return False

    def navigate_to(self, url):
        """Navigate to a specific URL"""
        if self.driver:
            try:
                self.driver.get(url)
                return True
            except Exception as e:
                print(f"❌ Navigation failed: {e}")
                return False
        return False

    def wait_for_element(self, locator, timeout=10):
        """Wait for an element to be present"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except Exception as e:
            print(f"⚠️ Element not found: {e}")
            return None

    def wait_for_clickable_element(self, locator, timeout=10):
        """Wait for an element to be clickable"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception as e:
            print(f"⚠️ Clickable element not found: {e}")
            return None

    def find_elements(self, locator):
        """Find multiple elements"""
        try:
            return self.driver.find_elements(*locator)
        except Exception as e:
            print(f"⚠️ Elements not found: {e}")
            return []

    def find_element(self, locator):
        """Find a single element"""
        try:
            return self.driver.find_element(*locator)
        except Exception as e:
            print(f"⚠️ Element not found: {e}")
            return None

    def safe_click(self, element):
        """Safely click an element with fallback to JavaScript"""
        try:
            element.click()
            return True
        except Exception as e:
            print("🔄 Trying JavaScript click...")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_error:
                print(f"❌ Both click methods failed: {e}, {js_error}")
                return False

    def scroll_to_element(self, element):
        """Scroll element into view"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Warning: Could not scroll to element: {e}")
            return False

    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return True
        except Exception as e:
            print(f"⚠️ Scroll to bottom failed: {e}")
            return False

    def scroll_by(self, pixels):
        """Scroll by specific number of pixels"""
        try:
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            return True
        except Exception as e:
            print(f"⚠️ Scroll by pixels failed: {e}")
            return False

    def execute_script(self, script, *args):
        """Execute JavaScript code"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            print(f"⚠️ Script execution failed: {e}")
            return None

    def get_page_source(self):
        """Get page source"""
        try:
            return self.driver.page_source
        except Exception as e:
            print(f"⚠️ Could not get page source: {e}")
            return ""

    def get_current_url(self):
        """Get current URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            print(f"⚠️ Could not get current URL: {e}")
            return ""

    def handle_cookie_consent(self):
        """Handle Facebook cookie consent dialog"""
        print("🍪 Checking for cookie consent dialog...")
        try:
            time.sleep(3)
            self.take_screenshot("cookie_debug.png")
            print("📸 Debug screenshot saved: cookie_debug.png")

            print("🔍 Finding all buttons on the page...")
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(all_buttons)} buttons total")

            for i, button in enumerate(all_buttons[:15]):
                try:
                    button_text = button.text.strip()
                    if button_text:
                        print(f"   Button {i+1}: '{button_text}'")
                        text_lower = button_text.lower()
                        if any(phrase in text_lower for phrase in [
                            'allow all cookies', 'accept all cookies',
                            'allow all', 'accept all',
                            'allow cookies', 'accept cookies'
                        ]):
                            print(f"🎯 Found cookie button: '{button_text}'")
                            self.scroll_to_element(button)
                            if self.safe_click(button):
                                print("✅ Successfully clicked cookie button!")
                                time.sleep(3)
                                return True
                except Exception:
                    continue

            # Try specific Facebook cookie selectors
            success = self._try_facebook_cookie_selectors()
            if success:
                return True

            # Last resort: look for blue buttons
            success = self._try_blue_buttons()
            if success:
                return True

            print("ℹ️ Could not find or click cookie consent button")
            return False
        except Exception as e:
            print(f"ℹ️ Cookie consent handling error: {e}")
            return False

    def _try_facebook_cookie_selectors(self):
        """Try specific Facebook cookie selectors"""
        print("🔍 Trying specific Facebook cookie selectors...")
        selectors = [
            "button[data-cookiebanner*='accept']",
            "button[data-testid*='accept']",
            "button[data-testid*='cookie']",
            "div[data-testid*='cookie'] button",
            "div[role='dialog'] button[type='submit']",
            "[aria-label*='cookie'] button",
            "button[style*='rgb(24, 119, 242)']",
            "button[style*='#1877f2']",
            "div[role='dialog'] button:last-child",
            "div[role='dialog'] button[class*='primary']",
            "button[class*='_42ft']",
            "button[class*='_4jy0']",
        ]

        for selector in selectors:
            try:
                print(f"🔍 Trying: {selector}")
                button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                button_text = button.text.strip()
                print(f"   Found button with text: '{button_text}'")
                self.scroll_to_element(button)
                if self.safe_click(button):
                    print("✅ Successfully clicked Facebook cookie button!")
                    time.sleep(3)
                    return True
            except Exception:
                continue
        return False

    def _try_blue_buttons(self):
        """Last resort: look for blue buttons"""
        print("🔍 Last resort: looking for blue buttons...")
        try:
            elements = self.driver.find_elements(By.TAG_NAME, "*")
            for element in elements[:50]:
                try:
                    if element.tag_name.lower() == 'button':
                        bg_color = self.driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).backgroundColor;", element)
                        if 'rgb(24, 119, 242)' in str(bg_color) or '1877f2' in str(bg_color):
                            element_text = element.text.strip()
                            print(f"🎯 Found blue button: '{element_text}'")
                            if self.safe_click(element):
                                print("✅ Successfully clicked blue button!")
                                time.sleep(3)
                                return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"Blue button search failed: {e}")
            return False