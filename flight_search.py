import requests
import os

ORIGIN_PLACE = "LHR-sky"

class FlightSearch:
    #This class is responsible for talking to the Skyscanner API.
    def __init__(self):

        self.places_url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/UK/GBP/en-GB/"
        self.quotes_base_url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/UK/GBP/en-GB/"

        self.headers = {
            'x-rapidapi-key': os.environ["XRAPID_API_KEY"],
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        }

    def get_iata_code(self, city_x: str):
        """Returns the IATA city code for a given city"""
        querystring = {"query": city_x}
        response = requests.request("GET", self.places_url, headers=self.headers, params=querystring)
        return response.json()["Places"][0]["CityId"].split(sep="-")[0]

    def get_placeid_codes(self, city_x: str):
        """Returns a list of PlaceIDs for airports in a given city"""
        placeid_list = []
        querystring = {"query": city_x}
        response = requests.request("GET", self.places_url, headers=self.headers, params=querystring)
        place_data = response.json()["Places"]
        for row in place_data:
            placeid_list.append(row["PlaceId"])
        return placeid_list

    def get_quotes_info(self, destination, outbound_date):
        """Returns a quote for a specified destination and outbound_date"""
        quote_details = {}
        querystring = {
           "inboundpartialdate": ""
        }
        self.quotes_url = f"{self.quotes_base_url}{ORIGIN_PLACE}/{destination}-sky/{outbound_date}/"
        try:
            response = requests.request("GET", self.quotes_url, headers=self.headers, params=querystring)
            json_data = response.json()

            if "errors" in json_data.items():
                raise Exception(f"get_quotes_info response error: {json_data['errors'][0]}")
            min_quote = json_data["Quotes"][0]["MinPrice"]
            min_quote_string = json_data["Currencies"][0]["Symbol"] + "{:.2f}".format(json_data["Quotes"][0]["MinPrice"])
            departure_date = json_data["Quotes"][0]["OutboundLeg"]["DepartureDate"].split(sep="T")[0]
            carrier_id_outbound = json_data["Quotes"][0]["OutboundLeg"]["CarrierIds"][0]
            for carrier_row in json_data["Carriers"]:
                if carrier_row["CarrierId"] == carrier_id_outbound:
                    carrier_outbound = carrier_row["Name"]
                    break
            origin_id = json_data["Quotes"][0]["OutboundLeg"]["OriginId"]
            for place_row in json_data["Places"]:
                if place_row["PlaceId"] == origin_id:
                    origin = place_row["CityName"] + "-" + place_row["IataCode"]
                    break
            destination_id = json_data["Quotes"][0]["OutboundLeg"]["DestinationId"]
            for place_row in json_data["Places"]:
                if place_row["PlaceId"] == destination_id:
                    destination = place_row["CityName"] + "-" + place_row["IataCode"]
                    break
            quote_details = {
                "min_quote": min_quote,
                "min_quote_string": min_quote_string,
                "departure_date": departure_date,
                "carrier_outbound": carrier_outbound,
                "origin": origin,
                "destination": destination
            }
            return quote_details
        except:
            pass
