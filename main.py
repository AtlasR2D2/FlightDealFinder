# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

flight_search = FlightSearch()
data_manager = DataManager(flight_search_x=flight_search)

# Output SMS if applicable
notification_manager = NotificationManager()
NotificationManager.send_sms(msg=data_manager.check_for_deals())
