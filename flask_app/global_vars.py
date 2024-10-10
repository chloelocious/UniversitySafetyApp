import threading

# global vars for threading events (for scraping functionality)
stop_scraping_event = threading.Event()
current_lat_lon = None
