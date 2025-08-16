"""
Utils Module
Contains utility functions and helpers
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Event:
    """Event data model"""
    title: str
    link: str
    date_time: Optional[str] = None
    location: Optional[str] = None
    city_match: bool = False
    source_approach: int = 1
    urgency: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'Title': self.title,
            'Link': self.link,
            'Date/Time': self.date_time,
            'Location': self.location,
            'City_Match': self.city_match,
            'Source_Approach': self.source_approach,
            'Urgency': self.urgency
        }

class FileManager:
    """Handles file operations"""
    
    @staticmethod
    def save_events_to_json(events: List[Event], city_name: str, filename: Optional[str] = None) -> Optional[str]:
        """Save events to JSON file with consistent naming"""
        if not events:
            print("No events to save")
            return None
        
        try:
            if not filename:
                # Create consistent filename: facebook_events_Timisoara.json
                # Remove special characters and spaces from city name
                clean_city_name = FileManager._clean_city_name_for_filename(city_name)
                filename = f"facebook_events_{clean_city_name}.json"
            
            # Convert events to dictionaries
            events_data = [event.to_dict() if isinstance(event, Event) else event for event in events]
            
            data = {
                "city": city_name,
                "timestamp": datetime.now().isoformat(),
                "total_events": len(events),
                "events": events_data,
                "browser_used": "Remote Selenium with Enhanced 2FA",
                "scraping_session": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "filename": filename
                }
            }
            
            # Check if file exists and notify about replacement
            if FileManager._file_exists(filename):
                print(f"📝 Replacing existing file: {filename}")
            else:
                print(f"📝 Creating new file: {filename}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(events)} events to {filename}")
            print(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return filename
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            return None
    
    @staticmethod
    def _clean_city_name_for_filename(city_name: str) -> str:
        """Clean city name for use in filename"""
        import re
        
        # Replace special characters and spaces
        clean_name = re.sub(r'[^\w\s-]', '', city_name)  # Remove special chars except spaces and hyphens
        clean_name = re.sub(r'\s+', '_', clean_name)      # Replace spaces with underscores
        clean_name = clean_name.strip('_')                # Remove leading/trailing underscores
        
        return clean_name if clean_name else "Unknown_City"
    
    @staticmethod
    def _file_exists(filename: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(filename)
    
    @staticmethod
    def get_events_filename(city_name: str) -> str:
        """Get the standard filename for a city"""
        clean_city_name = FileManager._clean_city_name_for_filename(city_name)
        return f"facebook_events_{clean_city_name}.json"
    
    @staticmethod
    def load_events_from_json(city_name: str, filename: Optional[str] = None) -> Optional[dict]:
        """Load previously saved events from JSON file"""
        try:
            if not filename:
                filename = FileManager.get_events_filename(city_name)
            
            if not FileManager._file_exists(filename):
                print(f"📁 No existing file found: {filename}")
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📖 Loaded events from {filename}")
            print(f"📊 Contains {data.get('total_events', 0)} events from {data.get('timestamp', 'unknown time')}")
            
            return data
            
        except Exception as e:
            print(f"❌ Load error: {e}")
            return None

class EventDisplayer:
    """Handles event display and formatting"""
    
    @staticmethod
    def display_events(events: List[Event], city_name: str) -> None:
        """Display found events in a formatted way"""
        if events:
            print(f"\n🎉 SUCCESS! Found {len(events)} events in {city_name}!")
            print("=" * 60)
            
            for i, event in enumerate(events, 1):
                if isinstance(event, Event):
                    EventDisplayer._display_single_event(event, i)
                else:
                    EventDisplayer._display_dict_event(event, i)
        else:
            print(f"😕 No events found in {city_name}")
            print("📸 Check the screenshots for debugging")
    
    @staticmethod
    def _display_single_event(event: Event, index: int) -> None:
        """Display a single Event object"""
        print(f"\n📅 Event #{index}:")
        print(f"   Title: {event.title}")
        if event.date_time:
            print(f"   Date: {event.date_time}")
        if event.location:
            print(f"   Location: {event.location}")
        if event.city_match:
            print(f"   ✅ City match confirmed")
        if event.urgency:
            print(f"   ⚡ Urgency: {event.urgency}")
        print(f"   Link: {event.link}")
    
    @staticmethod
    def _display_dict_event(event: dict, index: int) -> None:
        """Display a dictionary event (for backward compatibility)"""
        print(f"\n📅 Event #{index}:")
        print(f"   Title: {event.get('Title', 'N/A')}")
        if event.get('Date/Time'):
            print(f"   Date: {event['Date/Time']}")
        if event.get('Location'):
            print(f"   Location: {event['Location']}")
        if event.get('City_Match'):
            print(f"   ✅ City match confirmed")
        if event.get('Urgency'):
            print(f"   ⚡ Urgency: {event['Urgency']}")
        print(f"   Link: {event.get('Link', 'N/A')}")

class EventValidator:
    """Validates event data"""
    
    @staticmethod
    def is_valid_event_link(href: str) -> bool:
        """Check if this is a valid event link"""
        if not href:
            return False
        
        # Must be a real event link
        return (href and '/events/' in href and 
                'facebook.com/events/' in href and 
                len(href.split('/')) >= 5)
    
    @staticmethod
    def is_navigation_link(href: str, text: str) -> bool:
        """Check if this is a navigation link that should be skipped"""
        if not href or not text:
            return True
        
        # Skip navigation links
        if (href == 'https://www.facebook.com/events/' or 
            'events/?acontext' in href or
            'events/discovery' in href or
            'events/explore' in href or
            text.lower().strip() in ['events', 'discover', 'explore']):
            return True
        
        return False
    
    @staticmethod
    def is_valid_event_title(title: str) -> bool:
        """Check if event title is valid"""
        if not title or len(title) < 3:
            return False
        
        # Filter out common navigation/UI elements
        title_lower = title.lower().strip()
        invalid_titles = ['events', 'discover', 'create', 'home', 'feed']
        
        return title_lower not in invalid_titles

class TextParser:
    """Handles text parsing utilities"""
    
    @staticmethod
    def extract_date_from_text(text: str) -> Optional[str]:
        """Extract date information from text"""
        date_keywords = [
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'today', 'tomorrow', 'tonight'
        ]
        
        text_lower = text.lower()
        for keyword in date_keywords:
            if keyword in text_lower:
                return keyword.title()
        
        return None
    
    @staticmethod
    def extract_urgency_from_text(text: str) -> Optional[str]:
        """Extract urgency information from text"""
        text_lower = text.lower()
        
        if 'tonight' in text_lower or 'today' in text_lower:
            return 'Today'
        elif 'tomorrow' in text_lower:
            return 'Tomorrow'
        
        return None
    
    @staticmethod
    def clean_title(title: str, max_length: int = 120) -> str:
        """Clean and truncate title"""
        if not title:
            return ""
        
        title = title.strip()
        if len(title) > max_length:
            title = title[:max_length] + "..."
        
        return title
    
    @staticmethod
    def parse_event_lines(lines: List[str]) -> tuple:
        """Parse event text lines to extract title, date, and location"""
        event_title = ""
        event_date = ""
        event_location = ""
        
        if len(lines) >= 2:
            potential_date = lines[0].strip()
            # Check for date patterns
            if any(word in potential_date.lower() for word in [
                'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
                'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                'today', 'tomorrow', 'tonight'
            ]):
                event_date = potential_date
                event_title = lines[1].strip() if len(lines) > 1 else ""
                event_location = lines[2].strip() if len(lines) > 2 else ""
            else:
                event_title = potential_date
                # Check if second line contains date
                if len(lines) > 1:
                    second_line = lines[1].strip().lower()
                    if any(word in second_line for word in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']):
                        event_date = lines[1].strip()
                        event_location = lines[2].strip() if len(lines) > 2 else ""
        
        return event_title, event_date, event_location

class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def log_success(message: str) -> None:
        """Log success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def log_error(message: str) -> None:
        """Log error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def log_warning(message: str) -> None:
        """Log warning message"""
        print(f"⚠️ {message}")
    
    @staticmethod
    def log_info(message: str) -> None:
        """Log info message"""
        print(f"ℹ️ {message}")
    
    @staticmethod
    def log_debug(message: str) -> None:
        """Log debug message"""
        print(f"🔍 {message}")

class EventConverter:
    """Converts between different event formats"""
    
    @staticmethod
    def dict_to_event(event_dict: dict) -> Event:
        """Convert dictionary to Event object"""
        return Event(
            title=event_dict.get('Title', ''),
            link=event_dict.get('Link', ''),
            date_time=event_dict.get('Date/Time'),
            location=event_dict.get('Location'),
            city_match=event_dict.get('City_Match', False),
            source_approach=event_dict.get('Source_Approach', 1),
            urgency=event_dict.get('Urgency')
        )
    
    @staticmethod
    def events_to_dicts(events: List[Event]) -> List[dict]:
        """Convert list of Event objects to list of dictionaries"""
        return [event.to_dict() if isinstance(event, Event) else event for event in events]

class ConfigManager:
    """Manages configuration and constants"""
    
    # Selenium ports to try
    DEFAULT_SELENIUM_PORTS = [30479, 30444, 4444]
    
    # Timeout settings
    DEFAULT_TIMEOUT = 10
    ELEMENT_WAIT_TIMEOUT = 5
    SCREENSHOT_DELAY = 2
    
    # Enhanced scrolling settings
    MAX_SCROLLS = 20
    SCROLL_PAUSE_TIME = 5  # 5 seconds as requested
    STABLE_SCROLL_COUNT = 3
    ADVANCED_LOADING_ATTEMPTS = 4
    
    # Event extraction limits
    MAX_EVENTS_TO_PROCESS = 100  # Increased for better coverage
    
    # Text limits
    MAX_TITLE_LENGTH = 120
    MIN_TITLE_LENGTH = 3
    
    # Date filter patterns
    THIS_WEEK_PATTERNS = [
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
    
    # Enhanced load more button texts
    LOAD_MORE_TEXTS = [
        "see more", "load more", "show more", "more events", 
        "view more", "see all", "show all", "meer weergeven",
        "load more events", "show more events", "view all events",
        "continue reading", "expand", "more results"
    ]
    
    # Browser optimization flags
    BROWSER_ARGS = [
        "--headless",
        "--no-sandbox", 
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",  # Speed up by not loading images
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding"
    ]