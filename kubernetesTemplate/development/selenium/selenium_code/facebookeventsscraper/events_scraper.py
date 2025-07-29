"""
Events Scraper Module
Handles all Facebook events scraping functionality
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EventsScraper:
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()
        self.events_found = []
        self.failed_buttons = set()  # Track buttons that don't work across scrolls
    
    def search_and_extract_events(self, city_name="Timișoara"):
        """Search and extract events with simplified search terms"""
        print(f"📅 Searching for events in {city_name}...")
        
        all_events = []
        
        try:
            # Simplified search approaches - just use city name
            search_approaches = [
                f"https://www.facebook.com/events/search/?q={city_name}",
            ]
            
            print(f"🔍 Using simplified search: {search_approaches[0]}")
            
            for i, approach in enumerate(search_approaches):
                print(f"\n🔍 Approach {i+1}: {approach}")
                
                try:
                    self.driver.get(approach)
                    time.sleep(3)
                    
                    # Apply date filter for "This week"
                    if self._apply_this_week_filter():
                        print(f"✅ Applied 'This week' filter for approach {i+1}")
                        time.sleep(3)
                    else:
                        print("⚠️ Could not apply date filter, continuing without filter")
                    
                    # Load more events with smart scrolling
                    events_from_approach = self._load_and_extract_events(city_name, approach_num=i+1)
                    
                    if events_from_approach:
                        print(f"✅ Found {len(events_from_approach)} events from approach {i+1}")
                        all_events.extend(events_from_approach)
                    else:
                        print(f"⚠️ No events from approach {i+1}")
                        
                except Exception as e:
                    print(f"❌ Approach {i+1} failed: {e}")
                    continue
            
            # Remove duplicates
            unique_events = self._remove_duplicates(all_events)
            self.events_found = unique_events
            
            print(f"\n📊 TOTAL RESULTS: {len(unique_events)} unique events")
            return unique_events
            
        except Exception as e:
            print(f"❌ Event search error: {e}")
            return []
    
    def _apply_this_week_filter(self):
        """Apply 'This week' date filter on Facebook Events search page"""
        try:
            print("📅 Applying 'This week' date filter...")
            
            # Take screenshot to see current state
            self.browser.take_screenshot("before_date_filter.png")
            print("📸 Screenshot before filter: before_date_filter.png")
            
            # Method 1: Find the specific "This week" checkbox using more precise selectors
            this_week_patterns = [
                "//input[@type='checkbox'][following-sibling::*[contains(text(), 'This week')] or preceding-sibling::*[contains(text(), 'This week')]]",
                "//input[@type='checkbox'][..//*[contains(text(), 'This week')]]",
                "//label[contains(text(), 'This week')]//input[@type='checkbox']",
                "//label[contains(text(), 'This week')]",
                "//div[contains(text(), 'This week')]//input[@type='checkbox']",
                "//div[contains(text(), 'This week')]//*[@role='checkbox']",
                "//div[contains(text(), 'This week')]",
                "//span[contains(text(), 'This week')]//input[@type='checkbox']",
                "//span[contains(text(), 'This week')]/ancestor::*//input[@type='checkbox']",
                "//span[contains(text(), 'This week')]",
                "//div[@role='checkbox'][.//text()[contains(., 'This week')]]",
                "//*[@role='checkbox'][contains(@aria-label, 'This week')]",
                "//*[contains(@aria-label, 'This week')]",
                "//*[contains(text(), 'This week') and (@role='checkbox' or @type='checkbox' or ancestor::label)]"
            ]
            
            for i, pattern in enumerate(this_week_patterns):
                try:
                    print(f"🔍 Trying pattern {i+1}: {pattern[:60]}...")
                    
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, pattern))
                    )
                    
                    if element.is_displayed():
                        print(f"✅ Found 'This week' element with pattern {i+1}")
                        
                        # Check if it's already selected/checked
                        is_selected = self._check_if_selected(element)
                        
                        if is_selected:
                            print("ℹ️ 'This week' filter already applied")
                            return True
                        
                        # Try to click it
                        click_success = self._enhanced_click(element)
                        if click_success:
                            print("✅ Successfully applied 'This week' filter")
                            time.sleep(3)
                            
                            # Take screenshot after applying filter
                            self.browser.take_screenshot("after_date_filter.png")
                            print("📸 Screenshot after filter: after_date_filter.png")
                            
                            return True
                        else:
                            print(f"❌ Could not click element from pattern {i+1}")
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"⚠️ Pattern {i+1} error: {e}")
                    continue
            
            # Additional methods if patterns fail
            if self._try_facebook_ui_structure() or self._try_javascript_approach() or self._try_checkbox_analysis():
                return True
            
            print("❌ Could not find or click 'This week' option after trying all methods")
            print("💡 Continuing without date filter - events from all dates will be included")
            return False
            
        except Exception as e:
            print(f"❌ Date filter error: {e}")
            return False
    
    def _check_if_selected(self, element):
        """Check if element is already selected/checked"""
        try:
            if element.tag_name.lower() == 'input':
                return element.is_selected()
            elif element.get_attribute('aria-checked'):
                return element.get_attribute('aria-checked').lower() == 'true'
            elif 'checked' in element.get_attribute('class').lower():
                return True
        except:
            pass
        return False
    
    def _enhanced_click(self, element):
        """Enhanced clicking with multiple fallback methods"""
        click_methods = [
            ("Regular click", lambda el: el.click()),
            ("JavaScript click", lambda el: self.driver.execute_script("arguments[0].click();", el)),
            ("Scroll and click", lambda el: (
                self.driver.execute_script("arguments[0].scrollIntoView(true);", el),
                time.sleep(1),
                el.click()
            )),
        ]
        
        for method_name, click_func in click_methods:
            try:
                click_func(element)
                return True
            except Exception:
                continue
        return False
    
    def _try_facebook_ui_structure(self):
        """Try Facebook-specific UI structure approach"""
        try:
            print("🔍 Trying Facebook-specific UI structure...")
            
            # Look for the dates filter container first
            dates_selectors = [
                "//div[contains(@aria-label, 'Dates')]",
                "//div[.//text()[contains(., 'Dates')]]",
                "//*[contains(text(), 'Today')]/ancestor::div[contains(.//text(), 'This week')]",
                "//*[contains(text(), 'Tomorrow')]/ancestor::div[contains(.//text(), 'This week')]"
            ]
            
            for selector in dates_selectors:
                try:
                    dates_container = self.driver.find_element(By.XPATH, selector)
                    if dates_container.is_displayed():
                        print(f"✅ Found dates container: {selector[:50]}...")
                        
                        # Look for "This week" within the container
                        this_week_in_container = dates_container.find_elements(By.XPATH, ".//*[contains(text(), 'This week')]")
                        
                        for element in this_week_in_container:
                            if element.is_displayed():
                                print(f"🎯 Found 'This week' in dates container")
                                if self._enhanced_click(element):
                                    print("✅ Successfully clicked 'This week' in container")
                                    time.sleep(3)
                                    return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"⚠️ Facebook UI structure method error: {e}")
            return False
    
    def _try_javascript_approach(self):
        """Try JavaScript approach to find and click"""
        try:
            print("🔍 Trying JavaScript approach...")
            
            js_code = """
            // Find all elements containing "This week" text
            var elements = document.evaluate(
                "//*[contains(text(), 'This week')]",
                document,
                null,
                XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,
                null
            );
            
            for (var i = 0; i < elements.snapshotLength; i++) {
                var element = elements.snapshotItem(i);
                
                // Check if element or its ancestors are clickable
                var clickableParent = element;
                for (var j = 0; j < 5; j++) {
                    if (clickableParent.onclick || 
                        clickableParent.getAttribute('role') === 'checkbox' ||
                        clickableParent.tagName === 'INPUT' ||
                        clickableParent.tagName === 'LABEL' ||
                        clickableParent.tagName === 'BUTTON') {
                        
                        // Try to click it
                        try {
                            clickableParent.click();
                            return 'Clicked: ' + clickableParent.tagName;
                        } catch (e) {
                            // Try with events
                            var event = new MouseEvent('click', {bubbles: true, cancelable: true});
                            clickableParent.dispatchEvent(event);
                            return 'Event clicked: ' + clickableParent.tagName;
                        }
                    }
                    
                    if (clickableParent.parentElement) {
                        clickableParent = clickableParent.parentElement;
                    } else {
                        break;
                    }
                }
            }
            
            return 'No clickable This week element found';
            """
            
            result = self.driver.execute_script(js_code)
            print(f"🔧 JavaScript result: {result}")
            
            if "Clicked" in result:
                print("✅ JavaScript successfully clicked 'This week'")
                time.sleep(3)
                return True
            return False
                
        except Exception as e:
            print(f"⚠️ JavaScript approach error: {e}")
            return False
    
    def _try_checkbox_analysis(self):
        """Analyze page structure for checkboxes more carefully"""
        try:
            print("🔍 Analyzing page structure for checkboxes...")
            
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            print(f"Found {len(checkboxes)} checkboxes, analyzing context...")
            
            for i, checkbox in enumerate(checkboxes):
                try:
                    checkbox_context = self._get_checkbox_context(checkbox)
                    
                    print(f"   Checkbox {i+1} context: '{checkbox_context.strip()[:100]}...'")
                    
                    if "this week" in checkbox_context.lower():
                        print(f"🎯 Found 'This week' checkbox {i+1}!")
                        
                        if not checkbox.is_selected():
                            if self._enhanced_click(checkbox):
                                print("✅ Successfully checked 'This week' checkbox")
                                time.sleep(3)
                                return True
                        else:
                            print("ℹ️ 'This week' checkbox already checked")
                            return True
                            
                except Exception:
                    continue
            return False
                    
        except Exception as e:
            print(f"⚠️ Checkbox analysis error: {e}")
            return False
    
    def _get_checkbox_context(self, checkbox):
        """Get context around a checkbox"""
        context_methods = [
            lambda cb: cb.find_element(By.XPATH, "./..").get_attribute('textContent'),
            lambda cb: cb.find_element(By.XPATH, "./../..").get_attribute('textContent'),
            lambda cb: cb.find_element(By.XPATH, "./../../..").get_attribute('textContent'),
            lambda cb: self.driver.find_element(By.CSS_SELECTOR, f"label[for='{cb.get_attribute('id')}']").text if cb.get_attribute('id') else "",
            lambda cb: " ".join([el.text for el in cb.find_elements(By.XPATH, "./following-sibling::*")]),
            lambda cb: " ".join([el.text for el in cb.find_elements(By.XPATH, "./preceding-sibling::*")])
        ]
        
        checkbox_context = ""
        for method in context_methods:
            try:
                context = method(checkbox)
                if context:
                    checkbox_context += " " + context.lower()
            except:
                continue
        return checkbox_context
    
    def _load_and_extract_events(self, city_name, approach_num=1):
        """Load more events with aggressive scrolling and extract"""
        try:
            print(f"📜 Loading events for approach {approach_num}...")
            
            # Initial wait
            time.sleep(3)
            
            # Get initial count
            initial_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']")
            print(f"   Initial event links found: {len(initial_links)}")
            
            # Aggressive scrolling to load more events
            self._scroll_to_load_events()
            
            # Take screenshot
            screenshot_name = f"events_loaded_approach_{approach_num}_{city_name}.png"
            self.browser.take_screenshot(screenshot_name)
            print(f"   📸 Screenshot: {screenshot_name}")
            
            # Extract events
            return self._extract_events_enhanced(city_name, approach_num)
            
        except Exception as e:
            print(f"❌ Load and extract error: {e}")
            return []
    
    def _scroll_to_load_events(self):
        """Perform enhanced scrolling to load ALL events with smart exit conditions"""
        print("   🔄 Starting enhanced scrolling to load all events...")

        max_scrolls = 20
        scroll_pause_time = 5
        last_count = 0
        stable_count = 0
        
        for scroll in range(max_scrolls):
            print(f"   📜 Scroll {scroll+1}/{max_scrolls}: Scrolling to bottom...")

            # Scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait 5 seconds for content to load
            print(f"   ⏳ Waiting {scroll_pause_time} seconds for content to load...")
            time.sleep(scroll_pause_time)

            # Check if more content loaded
            current_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']")
            current_count = len(current_links)

            print(f"   📊 After scroll {scroll+1}: {current_count} event links found")

            if current_count == last_count:
                stable_count += 1
                print(f"   ⚠️ No new content loaded (stable cycle {stable_count})")

                # Try clicking "load more" buttons. Pass self.failed_buttons to avoid re-trying
                button_worked = self._click_load_more_buttons()

                if button_worked:
                    print("   ✅ Load more button worked, resetting counters...")
                    stable_count = 0
                    last_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
                    continue
                else:
                    print("   ℹ️ No effective load more button found or clicked in this cycle.")

                # If still no change after multiple attempts, try advanced techniques
                if stable_count >= 2:  # Consider stopping after 2-3 stable counts
                    print(f"   🛑 No new content after {stable_count} attempts, trying advanced loading...")
                    if self._try_advanced_loading_techniques():
                        print("   ✅ Advanced loading worked, resetting counters...")
                        stable_count = 0
                        last_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
                        continue
                    else:
                        print(f"   🏁 Stopping scrolling at {current_count} events (no more content)")
                        break # No more content or techniques worked

            else:
                # Content increased, reset counters
                stable_count = 0
                new_events = current_count - last_count
                print(f"   ✅ Loaded {new_events} new events! Total: {current_count}")

            last_count = current_count

        print(f"   🏁 Scrolling completed. Final count: {last_count} event links")

        # Take final screenshot (moved here from previous duplicate method)
        self.browser.take_screenshot("final_scroll_state.png")
        print("   📸 Final state screenshot: final_scroll_state.png")


    def _click_load_more_buttons(self):
        """
        Unified method to find and click "load more" buttons.
        Returns True if a button was successfully clicked and new content loaded, False otherwise.
        """
        load_more_texts = [
            "see more", "load more", "show more", "more events", 
            "view more", "see all", "show all", "meer weergeven",
            "load more events", "show more events", "view all events"
        ]
        
        # Filter out generic buttons that likely don't work (e.g., Facebook links)
        skip_phrases = ["see more on facebook", "view on facebook", "go to facebook"]
        
        current_event_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
        
        for text in load_more_texts:
            try:
                selectors = [
                    f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]",
                    f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]",
                    f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]",
                    f"//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]"
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if not element.is_displayed() or not element.is_enabled():
                                continue

                            button_text = element.text.strip().lower()

                            # Skip known non-working buttons
                            if any(skip in button_text for skip in skip_phrases):
                                continue
                            
                            # Create a unique identifier for this button
                            button_id = f"{button_text}_{element.location}"
                            if button_id in self.failed_buttons:
                                continue # Skip buttons that previously failed

                            print(f"   🎯 Trying load more button: '{button_text}'")

                            # Scroll to button and click
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1) # Short wait before click

                            if self._enhanced_click(element):
                                print(f"   ✅ Clicked: '{button_text}', checking for new content...")
                                time.sleep(3) # Wait for content to load after click

                                new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
                                if new_count > current_event_count:
                                    print(f"   🎉 Button worked! {current_event_count} → {new_count} events")
                                    return True # A button worked and added content
                                else:
                                    print(f"   ❌ Button didn't add content, marking as failed: '{button_text}'")
                                    self.failed_buttons.add(button_id) # Mark as failed for future attempts
                            else:
                                print(f"   ❌ Could not click button: '{button_text}'")
                                self.failed_buttons.add(button_id) # Mark as failed if click itself failed
                    except NoSuchElementException:
                        continue # If selector doesn't find elements, just continue to next
                    except Exception as e:
                        print(f"   ⚠️ Error processing button element: {e}")
                        continue
            except Exception as e:
                print(f"   ⚠️ Error with selector for '{text}': {e}")
                continue
        
        print("   ℹ️ No effective load more buttons found or clicked.")
        return False # No buttons worked to load new content

    def _try_advanced_loading_techniques(self):
        """Try advanced techniques to load more content with better success detection"""
        print("   🔍 Trying advanced loading techniques...")
        
        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
        
        # Technique 1: Multiple rapid scrolls
        try:
            print("   📜 Technique 1: Rapid scroll bursts...")
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(0.3)
            time.sleep(2) # Give a moment for content to appear
            
            new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
            if new_count > initial_count:
                print(f"   ✅ Rapid scrolls worked: {initial_count} → {new_count}")
                return True
        except Exception as e:
            print(f"   ⚠️ Rapid scroll technique error: {e}")
            pass
        
        # Technique 2: Try to trigger lazy loading by scrolling up slightly then back down
        try:
            print("   🔄 Technique 2: Lazy loading triggers...")
            self.driver.execute_script("window.scrollBy(0, -300);") # Scroll up slightly
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll back to bottom
            time.sleep(2) # Wait for content
            
            new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
            if new_count > initial_count:
                print(f"   ✅ Lazy loading trigger worked: {initial_count} → {new_count}")
                return True
        except Exception as e:
            print(f"   ⚠️ Lazy loading technique error: {e}")
            pass
        
        # Technique 3: Press END key
        try:
            print("   ⌨️ Technique 3: END key press...")
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.END)
            time.sleep(3)
            
            new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']"))
            if new_count > initial_count:
                print(f"   ✅ END key worked: {initial_count} → {new_count}")
                return True
        except Exception as e:
            print(f"   ⚠️ END key technique error: {e}")
            pass
            
        print("   ℹ️ Advanced loading techniques didn't find new content.")
        return False
    
    def _extract_events_enhanced(self, city_name, approach_num=1):
        """Enhanced event extraction with more aggressive collection"""
        events = []
        
        try:
            print(f"🔍 Extracting events from approach {approach_num}...")
            
            # Get all event links
            event_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']")
            print(f"   Found {len(event_links)} potential event links")
            
            # Process more events (increased from previous limit)
            max_events_to_process = min(100, len(event_links)) # Increased to 100 for more comprehensive scraping
            
            for i, link in enumerate(event_links[:max_events_to_process]):
                try:
                    event = self._process_event_link(link, city_name, approach_num, i)
                    if event:
                        events.append(event)
                        
                        # Only print every 10th event to reduce spam, or for the first few
                        if len(events) % 10 == 0 or len(events) <= 5:
                            print(f"   ✅ Event {len(events)}: {event['Title'][:50]}...")
                        
                except Exception as e:
                    if i < 5:  # Only print errors for first few problematic links
                        print(f"   ⚠️ Error processing link {i+1}: {e}")
                    continue
            
            print(f"   📊 Extracted {len(events)} events from approach {approach_num}")
            return events
            
        except Exception as e:
            print(f"❌ Enhanced extraction error: {e}")
            return []
    
    def _process_event_link(self, link, city_name, approach_num, index):
        """Process a single event link and extract information"""
        href = link.get_attribute('href')
        text = link.text.strip()
        
        # Debug output for first few and some random samples
        if index < 10 or index % 20 == 0: # Adjusted print frequency
            print(f"   Link {index+1}: '{text[:30]}...' -> {href[:50]}...")
        
        # Skip navigation links (more specific filtering)
        if (href == 'https://www.facebook.com/events/' or 
            'events/?acontext' in href or
            'events/discovery' in href or
            'events/explore' in href or
            text.lower().strip() in ['events', 'discover', 'explore', 'create event', 'home', 'feed']):
            return None
        
        # Must be a real event link
        if not (href and '/events/' in href and 
                'facebook.com/events/' in href and 
                len(href.split('/')) >= 5): # Ensure it's a deep link to an event
            return None
        
        # More lenient text filtering
        if not text or len(text) < 5: # Increased minimum text length for more meaningful links
            return None
        
        # Parse event info (enhanced)
        lines = text.split('\n')
        event_title, event_date, event_location = self._parse_event_text(lines)
        
        # Fallback title extraction
        if not event_title:
            event_title = text.split('\n')[0] if '\n' in text else text
        
        # Clean up title
        if len(event_title) > 120:
            event_title = event_title[:120].rsplit(' ', 1)[0] + "..." if ' ' in event_title[:120] else event_title[:120] + "..." # Clean cut
        
        # Create event object
        event = {
            'Title': event_title,
            'Link': href,
            'City_Match': city_name.lower() in text.lower(),
            'Source_Approach': approach_num
        }
        
        # Add date if found
        if event_date:
            event['Date/Time'] = event_date
        
        # Add location if found
        if event_location:
            event['Location'] = event_location
        elif city_name.lower() in text.lower():
            event['Location'] = f"Near {city_name}" # Infer location if city name is in text
        
        # Add additional metadata for sorting
        lower_text = text.lower()
        if 'tonight' in lower_text or 'today' in lower_text:
            event['Urgency'] = 'Today'
        elif 'tomorrow' in lower_text:
            event['Urgency'] = 'Tomorrow'
        elif 'this week' in lower_text:
            event['Urgency'] = 'This Week'
        
        return event
    
    def _parse_event_text(self, lines):
        """Parse event text lines to extract title, date, and location"""
        event_title = ""
        event_date = ""
        event_location = ""
        
        if not lines:
            return "", "", ""

        # Prioritize the longest line as potential title, or first line
        event_title = max(lines, key=len).strip() if lines else ""
        if not event_title and lines:
            event_title = lines[0].strip()

        # Iterate through lines to find date and location
        for line in lines:
            lower_line = line.strip().lower()
            if not event_date and any(word in lower_line for word in [
                'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
                'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                'today', 'tomorrow', 'tonight', 'this week', 'next week'
            ]):
                event_date = line.strip()
            elif not event_location and (len(line.strip().split()) > 1 and len(line.strip()) > 5): # Simple check for a plausible location line
                # Avoid setting title as location
                if line.strip() != event_title:
                    event_location = line.strip()

        # If title was a date, re-assign title from next line
        if event_date and event_title == event_date and len(lines) > 1:
            # Find next line that's not a date/location
            for i in range(1, len(lines)):
                if not any(word in lines[i].strip().lower() for word in [
                    'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
                    'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                    'today', 'tomorrow', 'tonight', 'this week', 'next week'
                ]) and not (len(lines[i].strip().split()) > 1 and len(lines[i].strip()) > 5):
                    event_title = lines[i].strip()
                    break
        
        return event_title, event_date, event_location
    
    def _remove_duplicates(self, all_events):
        """Remove duplicates across all events with smart deduplication"""
        try:
            print(f"🔄 Removing duplicates from {len(all_events)} total events...")
            
            seen_titles = set()
            seen_links = set()
            unique_events = []
            
            for event in all_events:
                title = event.get('Title', '').strip()
                link = event.get('Link', '').strip()
                
                # Create a normalized title for comparison (first 70 chars, lowercase, alphanumeric only)
                title_key = ''.join(filter(str.isalnum, title[:70].lower()))
                
                is_duplicate = False
                
                if link and link in seen_links:
                    is_duplicate = True
                elif title_key and len(title_key) > 10 and title_key in seen_titles: # Require longer title key for more robust matching
                    is_duplicate = True
                
                if not is_duplicate:
                    unique_events.append(event)
                    if title_key and len(title_key) > 10:
                        seen_titles.add(title_key)
                    if link:
                        seen_links.add(link)
                
            print(f"✅ Kept {len(unique_events)} unique events (removed {len(all_events) - len(unique_events)} duplicates)")
            
            # Sort by relevance (city matches first, then by date urgency)
            unique_events.sort(key=self._sort_events_by_relevance)
            print(f"📊 Sorted events by relevance (city matches and dates first)")
            
            return unique_events
            
        except Exception as e:
            print(f"❌ Deduplication error: {e}")
            return all_events
    
    def _sort_events_by_relevance(self, event):
        """Sort events by relevance score"""
        score = 0
        if event.get('City_Match'):
            score += 100
        if event.get('Urgency') == 'Today':
            score += 50
        elif event.get('Urgency') == 'Tomorrow':
            score += 25
        elif event.get('Urgency') == 'This Week':
            score += 15
        if event.get('Date/Time'):
            score += 10
        return -score  # Negative for descending order (higher score first)
    
    def get_events_found(self):
        """Get the list of found events"""
        return self.events_found