#!/usr/bin/env python3
"""
Facebook Events Scraper - Refactored Version
Enhanced 2FA Flow: Device approval → Try another way → Authentication app → 1Password code
"""

from browser_manager import BrowserManager
from auth_manager import AuthManager
from events_scraper import EventsScraper
from onepassword_manager import OnePasswordManager
from utils import FileManager, EventDisplayer, Logger, Event, EventConverter

class FacebookEventsScraper:
    """Main scraper class that orchestrates all components"""
    
    def __init__(self, selenium_ports=[30479, 30444, 4444]):
        # Initialize all managers
        self.browser = BrowserManager(selenium_ports)
        self.op_manager = OnePasswordManager("Facebook")
        self.auth_manager = None
        self.events_scraper = None
        self.events_found = []
        
        Logger.log_info("Facebook Events Scraper initialized")
    
    def setup(self):
        """Setup all components"""
        try:
            Logger.log_info("Setting up scraper components...")
            
            # Setup browser
            if not self.browser.setup_driver():
                Logger.log_error("Browser setup failed")
                return False
            
            # Initialize other managers with browser
            self.auth_manager = AuthManager(self.browser, self.op_manager)
            self.events_scraper = EventsScraper(self.browser)
            
            Logger.log_success("All components setup successfully")
            return True
            
        except Exception as e:
            Logger.log_error(f"Setup failed: {e}")
            return False
    
    def authenticate(self):
        """Handle authentication"""
        try:
            Logger.log_info("Starting authentication process...")
            
            if not self.auth_manager:
                Logger.log_error("Auth manager not initialized")
                return False
            
            success = self.auth_manager.login()
            
            if success:
                Logger.log_success("Authentication completed successfully")
            else:
                Logger.log_error("Authentication failed")
            
            return success
            
        except Exception as e:
            Logger.log_error(f"Authentication error: {e}")
            return False
    
    def scrape_events(self, city_name="Timișoara"):
        """Scrape events for the specified city"""
        try:
            Logger.log_info(f"Starting event scraping for {city_name}...")
            
            if not self.events_scraper:
                Logger.log_error("Events scraper not initialized")
                return []
            
            # Search and extract events
            events = self.events_scraper.search_and_extract_events(city_name)
            
            if events:
                # Convert to Event objects if they're dictionaries
                self.events_found = [
                    EventConverter.dict_to_event(event) if isinstance(event, dict) else event
                    for event in events
                ]
                Logger.log_success(f"Successfully scraped {len(self.events_found)} events")
            else:
                Logger.log_warning("No events found")
                self.events_found = []
            
            return self.events_found
            
        except Exception as e:
            Logger.log_error(f"Event scraping error: {e}")
            return []
    
    def save_results(self, city_name="Timișoara", filename=None):
        """Save scraped events to file with consistent naming"""
        try:
            if not self.events_found:
                Logger.log_warning("No events to save")
                return None
            
            Logger.log_info("Saving events to file...")
            
            # If no custom filename provided, use the standard format
            if not filename:
                filename = FileManager.get_events_filename(city_name)
                Logger.log_info(f"Using standard filename: {filename}")
            
            saved_filename = FileManager.save_events_to_json(self.events_found, city_name, filename)
            
            if saved_filename:
                Logger.log_success(f"Events saved to {saved_filename}")
                
                # Show file info
                import os
                if os.path.exists(saved_filename):
                    file_size = os.path.getsize(saved_filename)
                    Logger.log_info(f"File size: {file_size:,} bytes")
            else:
                Logger.log_error("Failed to save events")
            
            return saved_filename
            
        except Exception as e:
            Logger.log_error(f"Save error: {e}")
            return None
    
    def load_previous_results(self, city_name="Timișoara"):
        """Load previously saved events for comparison"""
        try:
            Logger.log_info(f"Checking for previous results for {city_name}...")
            
            previous_data = FileManager.load_events_from_json(city_name)
            
            if previous_data:
                Logger.log_success(f"Found previous results with {previous_data.get('total_events', 0)} events")
                return previous_data
            else:
                Logger.log_info("No previous results found")
                return None
                
        except Exception as e:
            Logger.log_error(f"Load previous results error: {e}")
            return None
    
    def display_results(self, city_name="Timișoara"):
        """Display scraped events"""
        try:
            EventDisplayer.display_events(self.events_found, city_name)
        except Exception as e:
            Logger.log_error(f"Display error: {e}")
    
    def run_full_scrape(self, city_name="Timișoara", save_file=True, display_results=True, compare_with_previous=False):
        """Run the complete scraping process"""
        Logger.log_info("🚀 ENHANCED 2FA FACEBOOK EVENTS SCRAPER")
        Logger.log_info("=" * 60)
        
        try:
            # Check previous results if requested
            previous_data = None
            if compare_with_previous:
                previous_data = self.load_previous_results(city_name)
            
            # Setup
            if not self.setup():
                return []
            
            # Authenticate
            if not self.authenticate():
                return []
            
            # Scrape events
            events = self.scrape_events(city_name)
            
            if events:
                # Display results
                if display_results:
                    self.display_results(city_name)
                
                # Compare with previous if available
                if compare_with_previous and previous_data:
                    self._compare_with_previous(events, previous_data)
                
                # Save to file (will replace existing file)
                if save_file:
                    saved_file = self.save_results(city_name)
                    if saved_file:
                        Logger.log_info(f"📁 Results saved to: {saved_file}")
                        Logger.log_info(f"🔄 File will be replaced on next run")
                
                Logger.log_success(f"✅ Scraping completed! Found {len(events)} events")
                Logger.log_info("💡 Used enhanced 2FA flow: Device approval → Try another way → Authentication app → 1Password")
            else:
                Logger.log_warning("😕 No events found or scraping failed")
                Logger.log_info("📸 Check the screenshots for debugging")
            
            return events
            
        except Exception as e:
            Logger.log_error(f"Scraping process error: {e}")
            return []
        
        finally:
            self.cleanup()
    
    def _compare_with_previous(self, current_events, previous_data):
        """Compare current results with previous scraping session"""
        try:
            previous_events = previous_data.get('events', [])
            previous_count = len(previous_events)
            current_count = len(current_events)
            
            Logger.log_info(f"📊 Comparison with previous results:")
            Logger.log_info(f"   Previous: {previous_count} events")
            Logger.log_info(f"   Current:  {current_count} events")
            Logger.log_info(f"   Change:   {current_count - previous_count:+d} events")
            
            if current_count > previous_count:
                Logger.log_success(f"🆕 Found {current_count - previous_count} new events!")
            elif current_count < previous_count:
                Logger.log_warning(f"📉 {previous_count - current_count} fewer events than before")
            else:
                Logger.log_info("🔄 Same number of events as previous run")
                
        except Exception as e:
            Logger.log_error(f"Comparison error: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.browser:
                self.browser.quit()
                Logger.log_info("Browser closed successfully")
        except Exception as e:
            Logger.log_error(f"Cleanup error: {e}")
    
    def get_events(self):
        """Get the list of found events"""
        return self.events_found


class ScraperFactory:
    """Factory class for creating scraper instances"""
    
    @staticmethod
    def create_scraper(selenium_ports=None):
        """Create a new scraper instance"""
        if selenium_ports is None:
            selenium_ports = [30479, 30444, 4444]
        
        return FacebookEventsScraper(selenium_ports)
    
    @staticmethod
    def create_simple_scraper():
        """Create a scraper with default settings"""
        return FacebookEventsScraper()


def main():
    """Main entry point"""
    try:
        # Create scraper instance
        scraper = ScraperFactory.create_simple_scraper()
        
        # Run the complete scraping process with consistent filename
        events = scraper.run_full_scrape(
            city_name="Timișoara",
            save_file=True,
            display_results=True,
            compare_with_previous=True  # Compare with previous run
        )
        
        # Show final filename info
        if events:
            expected_filename = FileManager.get_events_filename("Timișoara")
            Logger.log_info(f"📁 Events saved to: {expected_filename}")
            Logger.log_info(f"🔄 This file will be replaced on the next run")
        
        # Return results
        return events
        
    except KeyboardInterrupt:
        Logger.log_warning("Scraping interrupted by user")
        return []
    except Exception as e:
        Logger.log_error(f"Main execution error: {e}")
        return []


def scrape_city(city_name, selenium_ports=None, save_file=True, compare_with_previous=False):
    """Convenience function to scrape events for a specific city with consistent naming"""
    try:
        scraper = ScraperFactory.create_scraper(selenium_ports)
        events = scraper.run_full_scrape(
            city_name=city_name,
            save_file=save_file,
            display_results=True,
            compare_with_previous=compare_with_previous
        )
        
        if save_file and events:
            filename = FileManager.get_events_filename(city_name)
            Logger.log_info(f"📁 Results for {city_name} saved to: {filename}")
        
        return events
    except Exception as e:
        Logger.log_error(f"City scraping error: {e}")
        return []


def scrape_multiple_cities(cities, selenium_ports=None):
    """Scrape events for multiple cities"""
    all_results = {}
    
    for city in cities:
        Logger.log_info(f"🌍 Scraping events for {city}...")
        try:
            events = scrape_city(city, selenium_ports, save_file=True)
            all_results[city] = events
            Logger.log_success(f"✅ Completed {city}: {len(events)} events found")
        except Exception as e:
            Logger.log_error(f"❌ Failed to scrape {city}: {e}")
            all_results[city] = []
    
    return all_results


if __name__ == "__main__":
    # Example usage:
    
    # Single city scraping
    main()
    
    # Multiple cities scraping (uncomment to use)
    # cities = ["Timișoara", "București", "Cluj-Napoca"]
    # results = scrape_multiple_cities(cities)
    # 
    # for city, events in results.items():
    #     print(f"{city}: {len(events)} events found")
    
    # Custom scraping (uncomment to use)
    # scraper = ScraperFactory.create_scraper([30479, 4444])  # Custom ports
    # events = scraper.run_full_scrape("Your City Name", save_file=True)