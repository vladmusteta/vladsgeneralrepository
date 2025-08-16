"""
Authentication Manager
Handles all Facebook authentication flows including 2FA
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

class AuthManager:
    def __init__(self, browser_manager, op_manager):
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()
        self.op_manager = op_manager
    
    def login(self):
        """Enhanced login with specific Facebook 2FA flow"""
        print("🔑 Logging in with enhanced 2FA handling...")
        
        # Get credentials
        username, password = self.op_manager.get_credentials()
        if not username or not password:
            print("❌ Could not get credentials from 1Password")
            return False
        
        # Go to Facebook
        self.driver.get("https://facebook.com")
        time.sleep(3)
        
        # Handle cookies first
        self._handle_cookies()
        
        # Check if already logged in
        current_url = self.driver.current_url.lower()
        if "login" not in current_url and len(current_url.split('/')) <= 4:
            print("🎉 Already logged in!")
            return True
        
        # Go to login page
        self.driver.get("https://facebook.com/login")
        time.sleep(3)
        
        try:
            # Fill login form
            if not self._fill_login_form(username, password):
                return False
            
            # Handle 2FA flow with device approval → authenticator app
            auth_success = self._handle_enhanced_2fa_flow()
            
            if not auth_success:
                print("❌ 2FA authentication failed")
                return False
            
            # Verify login
            if "login" not in self.driver.current_url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def _handle_cookies(self):
        """Handle cookie dialog"""
        try:
            print("🍪 Handling cookies...")
            time.sleep(2)
            
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            for button in buttons:
                try:
                    text = button.text.strip().lower()
                    if any(phrase in text for phrase in ['allow all', 'accept all', 'allow cookies']):
                        print(f"🎯 Found cookie button: '{text}'")
                        self._enhanced_click(button)
                        print("✅ Cookies accepted")
                        time.sleep(2)
                        return
                except:
                    continue
                    
            print("⚠️ No cookie button found, continuing...")
        except Exception as e:
            print(f"⚠️ Cookie handling error: {e}")
    
    def _fill_login_form(self, username, password):
        """Fill the login form with credentials"""
        try:
            # Fill login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "email"))
            )
            password_field = self.driver.find_element(By.ID, "pass")
            
            email_field.clear()
            email_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            print("✅ Filled login form")
            
            # Click login button with enhanced handling
            login_button = self.driver.find_element(By.NAME, "login")
            login_success = self._enhanced_click(login_button)
            
            if not login_success:
                print("❌ Could not click login button")
                return False
            
            print("⏳ Logging in...")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"❌ Login form error: {e}")
            return False
    
    def _enhanced_click(self, element):
        """Enhanced clicking with multiple fallback methods"""
        click_methods = [
            ("Regular click", lambda el: el.click()),
            ("JavaScript click", lambda el: self.driver.execute_script("arguments[0].click();", el)),
            ("ActionChains click", lambda el: ActionChains(self.driver).move_to_element(el).click().perform()),
            ("Scroll and click", lambda el: (
                self.driver.execute_script("arguments[0].scrollIntoView(true);", el),
                time.sleep(1),
                el.click()
            )),
            ("Send ENTER key", lambda el: el.send_keys(Keys.RETURN)),
        ]
        
        for method_name, click_func in click_methods:
            try:
                print(f"   Trying: {method_name}")
                click_func(element)
                time.sleep(1)
                print(f"   ✅ {method_name} succeeded")
                return True
            except Exception as e:
                print(f"   ❌ {method_name} failed: {str(e)[:50]}...")
                continue
        
        return False
    
    def _handle_enhanced_2fa_flow(self):
        """Handle the specific Facebook 2FA flow"""
        try:
            print("🔐 Checking for 2FA challenges...")
            time.sleep(3)
            
            # Take screenshot to see current state
            self.browser.take_screenshot("2fa_initial_state.png")
            print("📸 Initial 2FA screenshot: 2fa_initial_state.png")
            
            print(f"🔍 Current URL: {self.driver.current_url.lower()}")
            
            # Step 1: Check for device approval screen
            if self._handle_device_approval_screen():
                print("✅ Handled device approval screen")
                time.sleep(3)
            
            # Step 2: Check for authentication method selection
            if self._handle_authentication_method_selection():
                print("✅ Selected authentication app")
                time.sleep(3)
            
            # Step 3: Handle authenticator app code entry
            if self._handle_authenticator_code_entry():
                print("✅ Entered authenticator code")
                return True
            
            # Fallback: Try direct OTP field (legacy 2FA)
            if self._handle_legacy_2fa():
                print("✅ Handled legacy 2FA")
                return True
            
            print("ℹ️ No 2FA challenge detected or all methods handled")
            return True
            
        except Exception as e:
            print(f"❌ 2FA flow error: {e}")
            return False
    
    def _handle_device_approval_screen(self):
        """Handle device approval screen - Click 'Try another way'"""
        try:
            print("🔍 Looking for device approval screen...")
            
            # Look for indicators of device approval screen
            device_indicators = [
                "check your notifications on another device",
                "we sent a notification",
                "waiting for approval",
                "try another way"
            ]
            
            page_text = self.driver.page_source.lower()
            is_device_approval = any(indicator in page_text for indicator in device_indicators)
            
            if is_device_approval:
                print("📱 Device approval screen detected!")
                
                # Take screenshot
                self.browser.take_screenshot("device_approval_screen.png")
                print("📸 Device approval screenshot: device_approval_screen.png")
                
                # Look for "Try another way" button
                try_another_selectors = [
                    "//button[contains(text(), 'Try another way')]",
                    "//a[contains(text(), 'Try another way')]",
                    "//div[contains(text(), 'Try another way')]",
                    "button[value*='try']",
                    "[data-testid*='try']"
                ]
                
                for selector in try_another_selectors:
                    try:
                        if selector.startswith("//"):
                            try_another_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            try_another_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        
                        print(f"🎯 Found 'Try another way' button: {selector}")
                        self._enhanced_click(try_another_element)
                        print("✅ Clicked 'Try another way'")
                        time.sleep(3)
                        return True
                        
                    except TimeoutException:
                        continue
                
                # Fallback: Look for any button with "another" in text
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in all_buttons:
                    try:
                        button_text = button.text.strip().lower()
                        if "another" in button_text or "try" in button_text:
                            print(f"🎯 Found alternative button: '{button_text}'")
                            self._enhanced_click(button)
                            print("✅ Clicked alternative 'Try another way' button")
                            time.sleep(3)
                            return True
                    except:
                        continue
                
                print("⚠️ Could not find 'Try another way' button")
                return False
            
            return False
            
        except Exception as e:
            print(f"❌ Device approval screen error: {e}")
            return False
    
    def _handle_authentication_method_selection(self):
        """Handle authentication method selection - Select 'Authentication app'"""
        try:
            print("🔍 Looking for authentication method selection...")
            
            # Take screenshot
            self.browser.take_screenshot("auth_method_selection.png")
            print("📸 Auth method screenshot: auth_method_selection.png")
            
            # Look for indicators of method selection screen
            method_indicators = [
                "choose a way to confirm",
                "authentication app",
                "available confirmation methods",
                "notification on another device"
            ]
            
            page_text = self.driver.page_source.lower()
            is_method_selection = any(indicator in page_text for indicator in method_indicators)
            
            if is_method_selection:
                print("📋 Authentication method selection screen detected!")
                
                # Look for Authentication app option
                auth_app_selectors = [
                    "//div[contains(text(), 'Authentication app')]",
                    "//label[contains(text(), 'Authentication app')]",
                    "//span[contains(text(), 'Authentication app')]",
                    "[data-testid*='auth']",
                    "input[value*='auth']"
                ]
                
                for selector in auth_app_selectors:
                    try:
                        if selector.startswith("//"):
                            auth_app_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            auth_app_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        
                        print(f"🎯 Found 'Authentication app' option: {selector}")
                        self._enhanced_click(auth_app_element)
                        print("✅ Selected 'Authentication app'")
                        time.sleep(2)
                        
                        # Look for and click Continue button
                        self._click_continue_button()
                        return True
                        
                    except TimeoutException:
                        continue
                
                # Fallback: Look for radio buttons and select the one related to auth app
                radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                for radio in radio_buttons:
                    try:
                        # Look for associated text
                        parent = radio.find_element(By.XPATH, "./..")
                        parent_text = parent.text.lower()
                        if "authentication" in parent_text or "app" in parent_text:
                            print(f"🎯 Found auth app radio button: '{parent_text}'")
                            self._enhanced_click(radio)
                            print("✅ Selected authentication app radio button")
                            time.sleep(2)
                            
                            # Click continue
                            self._click_continue_button()
                            return True
                    except:
                        continue
                
                print("⚠️ Could not find 'Authentication app' option")
                return False
            
            return False
            
        except Exception as e:
            print(f"❌ Authentication method selection error: {e}")
            return False
    
    def _click_continue_button(self):
        """Find and click Continue button"""
        continue_button = None
        try:
            continue_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
        except:
            try:
                continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                pass
        
        if continue_button:
            print("🎯 Found Continue button")
            self._enhanced_click(continue_button)
            print("✅ Clicked Continue")
            time.sleep(3)
    
    def _handle_authenticator_code_entry(self):
        """Handle authenticator code entry - Enter code from 1Password"""
        try:
            print("🔍 Looking for authenticator code entry screen...")
            
            # Take screenshot
            self.browser.take_screenshot("auth_code_entry.png")
            print("📸 Auth code screenshot: auth_code_entry.png")
            
            # Look for indicators of code entry screen
            code_indicators = [
                "go to your authentication app",
                "enter the 6-digit code",
                "two-factor authentication app",
                "6-digit code"
            ]
            
            page_text = self.driver.page_source.lower()
            is_code_entry = any(indicator in page_text for indicator in code_indicators)
            
            if is_code_entry:
                print("🔐 Authenticator code entry screen detected!")
                
                # Get OTP from 1Password
                print("🔑 Getting OTP from 1Password...")
                otp_code = self.op_manager.get_otp()
                
                if not otp_code:
                    print("❌ Could not get OTP from 1Password")
                    return False
                
                print(f"✅ Retrieved OTP: {otp_code}")
                
                # Look for code input field
                code_field_selectors = [
                    "input[placeholder*='Code']",
                    "input[placeholder*='code']",
                    "input[aria-label*='code']",
                    "input[name*='code']",
                    "input[id*='code']",
                    "input[type='text']",
                    "input[maxlength='6']"
                ]
                
                for selector in code_field_selectors:
                    try:
                        code_field = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        print(f"🎯 Found code input field: {selector}")
                        code_field.clear()
                        code_field.send_keys(otp_code)
                        print("✅ Entered OTP code")
                        time.sleep(2)
                        
                        # Look for and click Continue button
                        continue_selectors = [
                            "//button[contains(text(), 'Continue')]",
                            "button[type='submit']",
                            "input[type='submit']"
                        ]
                        
                        for continue_selector in continue_selectors:
                            try:
                                if continue_selector.startswith("//"):
                                    continue_button = self.driver.find_element(By.XPATH, continue_selector)
                                else:
                                    continue_button = self.driver.find_element(By.CSS_SELECTOR, continue_selector)
                                
                                print(f"🎯 Found continue button: {continue_selector}")
                                self._enhanced_click(continue_button)
                                print("✅ Clicked Continue")
                                time.sleep(5)
                                return True
                                
                            except:
                                continue
                        
                        # If no continue button, try Enter key
                        code_field.send_keys(Keys.RETURN)
                        print("✅ Pressed Enter to submit")
                        time.sleep(5)
                        return True
                        
                    except TimeoutException:
                        continue
                
                print("⚠️ Could not find code input field")
                return False
            
            return False
            
        except Exception as e:
            print(f"❌ Authenticator code entry error: {e}")
            return False
    
    def _handle_legacy_2fa(self):
        """Handle legacy 2FA (direct OTP field)"""
        try:
            otp_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "approvals_code"))
            )
            
            print("🔐 Legacy 2FA detected! Getting OTP from 1Password...")
            otp_code = self.op_manager.get_otp()
            
            if otp_code:
                print(f"✅ Retrieved OTP: {otp_code}")
                otp_field.clear()
                otp_field.send_keys(otp_code)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                self._enhanced_click(submit_button)
                print("📤 Submitted legacy 2FA code...")
                time.sleep(5)
                return True
            else:
                print("❌ Could not get OTP for legacy 2FA")
                return False
                
        except TimeoutException:
            print("ℹ️ No legacy 2FA challenge detected")
            return False
        except Exception as e:
            print(f"⚠️ Legacy 2FA error: {e}")
            return False