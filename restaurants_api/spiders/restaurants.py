import scrapy
import json

class RestaurantsSpider(scrapy.Spider):
    name = "restaurants"
    allowed_domains = ["maps.googleapis.com"]
    start_urls = []
    
    api_key = '<GOOGLE MAPS API KEY>'
    
    def __init__(self, city=None, api_key=api_key, **kwargs):
        super().__init__(**kwargs)
        self.city = city
        self.start_urls.append(f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={api_key}")

    def parse(self, response):
        data = json.loads(response.body)
        lat = data["results"][0]["geometry"]["location"]["lat"]
        lng = data["results"][0]["geometry"]["location"]["lng"]
        location = f"{lat}%2C{lng}"
        radius = 50000
        types = ['restaurant', 'food', 'cafe', 'bar', 'meal_takeaway']
        for type in types:
            yield scrapy.FormRequest(f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type={type}&key={self.api_key}", callback=self.parse_restaurants)
    
    def parse_restaurants(self, response):
        data = json.loads(response.body)
        for result in data["results"]:
            place_id = result["place_id"]
            yield scrapy.Request(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={self.api_key}", callback=self.parse_details)

    def parse_details(self, response):
        data = json.loads(response.body)
        place_id = data["result"]["place_id"]
        name = data["result"]["name"]
        types = data["result"]["types"]
        overview = data["result"]["editorial_summary"]["overview"]
        address = data["result"]["formatted_address"]
        location = data["result"]["geometry"]["location"]
        phone = data["result"]["formatted_phone_number"]
        website = data["result"]["website"]
        price_level = data["result"]["price_level"]
        rating = data["result"]["rating"]
        reviews = []
        for review in data["result"]["reviews"]:
            reviews.append(review['text'])
        # reviews = data["result"]["reviews"]
        yield {
            "place_id" : place_id,
            "name": name,
            "types": types,
            "overview" : overview,
            "address": address,
            "location": location,
            "phone": phone,
            "website" : website,
            "price_level" : price_level,
            "rating": rating,
            "reviews": reviews
        } 
