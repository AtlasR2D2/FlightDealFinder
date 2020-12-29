import datetime as dt
from dateutil.relativedelta import relativedelta
import os
import requests
from flight_search import FlightSearch

class DataManager:
    """This class is responsible for managing the data"""
    def __init__(self, flight_search_x: FlightSearch):
        self.base_url = "https://api.sheety.co/2e22d7be903560b0d1d0aa06e5139fec/flightDetailsV1/prices"
        self.SHEETY_AUTH_TOKEN = os.environ["SHEETY_AUTH_TOKEN"]
        self.headers = {
            "Authorization": self.SHEETY_AUTH_TOKEN
        }
        self.flight_search = flight_search_x
        self.get_wks_data()
        self.update_iata_codes()
        self.startdate = (dt.datetime.today() + dt.timedelta(days=1)).date()
        self.enddate = (dt.datetime.today() + relativedelta(months=6)).date()
        print(self.enddate)
        self.flight_data = {}
        self.construct_flight_data()    # Container to store overall flight data


    def construct_flight_data(self):
        for row in self.wks_data:
            airports = self.flight_search.get_placeid_codes(row['city'])
            self.flight_data[row['city']] = {
                "city": row['city'],
                "iataCode": row["iataCode"],
                "LowestPrice": row["lowestPrice"],
                "MinQuoteDetails": self.check_quotes(airports, row["lowestPrice"]),
                "Airports": airports
            }

    def check_quotes(self, airports_x, lowest_price_x):
        """Will check min quote each day over specified period against LowestPrice Cap"""
        """min quote details will be updated if min quote is below threshold and/or lower than previous entry"""
        min_quote = None
        for airport in airports_x:
            for single_date in date_range(self.startdate, self.enddate):
                outbound_date_x = single_date.strftime("%Y-%m-%d")
                quote_x = self.flight_search.get_quotes_info(destination=airport,outbound_date=outbound_date_x)
                if quote_x["min_quote"] <= lowest_price_x:
                    if min_quote is not None:
                        if min_quote["min_quote"] >= quote_x["min_quote"]:
                            min_quote = quote_x
                        else:
                            # already have lowest quote
                            pass
                    else:
                        # Add first min quote
                        min_quote = quote_x
                else:
                    # Quote is not below lowest price
                    pass
        return min_quote


    def check_for_deals(self):
        """will produce a text message string for any deals"""
        deals_msg = ""
        for destination_x in self.flight_data.items():
            try:
                if destination_x["MinQuoteDetails"] is not None:
                    if destination_x["LowestPrice"] >= destination_x["MinQuoteDetails"]["min_quote"]:
                        if len(deals_msg) == 0:
                            deals_msg += "\n\n"
                        # Store Quote Details
                        min_quote_string = destination_x["MinQuoteDetails"]["min_quote_string"]
                        departure_date = destination_x["MinQuoteDetails"]["departure_date"]
                        carrier_outbound = destination_x["MinQuoteDetails"]["carrier_outbound"]
                        origin = destination_x["MinQuoteDetails"]["origin"]
                        destination = destination_x["MinQuoteDetails"]["destination"]
                        # Add Quote Details to msg
                        deals_msg += f"Low price alert! Only {min_quote_string} to fly from {origin} to {destination}, \
                                    leaving on {departure_date} with {carrier_outbound}."
            except:
                pass
        return deals_msg


    def get_wks_data(self):
        self.wks_data = requests.get(url=self.base_url, headers=self.headers).json()["prices"]

    def update_iata_codes(self):
        for ix in range(len(self.wks_data)):
            row = self.wks_data[ix]
            if len(row["iataCode"]) == 0:
                city = row["city"]
                self.update_url = f"{self.base_url}/{row['id']}"
                iata_code = self.flight_search.get_iata_code(city_x=city.title())
                row["iataCode"] = iata_code
                self.update_body = {
                    "price": row
                }
                response = requests.put(url=self.update_url, json=self.update_body, headers=self.headers)


def date_range(start_date, end_date):
    """generator function to iterate over days between two dates"""
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)