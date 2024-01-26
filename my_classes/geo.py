import requests
from geopy import distance
from geopy import Point
# from my_package import generate_postcode_1
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
import googlemaps
# from bs4 import BeautifulSoup
import random

class GeoClass:
    def __init__(self, db_class):
        self.db_class = db_class

    def distance(self, coor1, coor2):
        lat1, lon1 = coor1 
        lat2, lon2 = coor2
        # Convert latitude and longitude to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Calculate the differences between the latitudes and longitudes
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Apply the Haversine formula to calculate the distance between the two points
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c  # Radius of the earth in kilometers

        return distance

    def get_coordinates(self, address):
        # geolocator = Nominatim(user_agent="my-app")  # Replace "my-app" with your own user agent string
        geolocator = Nominatim(user_agent="denis71@gmail.com")
        location = geolocator.geocode(address)
        if location is None:
            return None  # Address not found
        else:
            return location.latitude, location.longitude
        

    def distance2 (self, coor1, coor2):
        lat1, lon1 = coor1 
        lat2, lon2 = coor2
        # Define the coordinates of the two points
        point_a = Point(lat1, lon1) # London
        point_b = Point(lat2, lon2) # New York City

        # Calculate the shortest distance between the two points
        shortest_distance = distance.distance(point_a, point_b).km

        # print(f"The shortest distance between {coor1} and {coor2} is {shortest_distance:.2f} kilometers.")
        return shortest_distance
    

    def check_postcode_DO_NOT_USE(self, postcode):
        # Create a geocoder instance
        geolocator = Nominatim(user_agent="my_service_project")
        
        
        # Attempt to geocode the postcode
        location = geolocator.geocode(postcode)
        
        # Check if a location was found
        if location is not None:
            # Postcode is valid and geocoded successfully
            return True
        else:
            # Postcode is not valid or could not be geocoded
            return False
        



    def googlemaps_validate_postcode(self, postcode, api_key):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            # Check if at least one result exists
            if len(data["results"]) > 0:
                address_components = data["results"][0]["address_components"]

                for component in address_components:
                    if "postal_code" in component["types"]:
                        result_postcode = component["long_name"]
                        
                        if result_postcode == postcode:
                            return True

            return False

        return False



    def googlemaps_determine_distance(self, staff_postcode, su_postcode, api_key):
       value = random.randint(1, 21) * 5
       return value
        # # Construct the URL for the Distance Matrix API request
        # url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric'
        # url += '&origins=' + staff_postcode
        # url += '&destinations=' + su_postcode
        # url += '&key=' + api_key

        # # Send the API request
        # response = requests.get(url)
        # data = response.json()

        # # Parse the distance from the API response
        # if data['status'] == 'OK':
        #     distance_text = data['rows'][0]['elements'][0]['distance']['text']
        #     distance_value = float(''.join(filter(str.isdigit, distance_text)))
        #     return distance_value
        # else:
        #     return -9999 #'Error: Unable to calculate the distance'


    def NOT_WORKING_webscrape_check_valid_postcode(postcode):
        url = 'https://www.gov.uk/find-local-council'
        data = {'postcode': postcode, 'find-council-submit': 'Find'}
        
        session = requests.Session()
        response = session.post(url, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = soup.find('p', class_='govuk-body')
        if result and 'Your local authority is' in result.text:
            return True
        else:
            return False



    def googlemaps_check_postcode_DO_NOT_USE(self, postcode, api_key = 'AIzaSyBz7w6I09gkMm5pp7CwL3l7OJ5EUjojU-4'):
        gmaps = googlemaps.Client(key=api_key)
        
        # Geocode the postcode
        geocode_result = gmaps.geocode(postcode, components={'country': 'GB'})
        
        # Check if any results were found
        if geocode_result:
            # Extract the first result
            first_result = geocode_result[0]
            
            # Check if the result has a postcode component
            if 'postcode' in first_result['address_components']:
                # Get the formatted postcode from the result
                formatted_postcode = first_result['address_components']['postcode']
                
                # Compare the formatted postcode with the input postcode
                if formatted_postcode == postcode:
                    return True
        
        # If no valid result was found or the postcode doesn't match, return False
        return False

        


    def get_all_postcodes(self, schema):
        conn = self.db_class.connect()
        cur = conn.cursor()

        # Execute the query to retrieve postcode_id and postcode
        query = f"SELECT postcode_id, postcode FROM {schema}.postcodes;"
        cur.execute(query)

        # Fetch all rows from the result set
        rows = cur.fetchall()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the list of postcode_id and postcode tuples
        return rows


    def delete_postcode(self, schema, postcode_id):
        conn = self.db_class.connect()
        cur = conn.cursor()

        # Execute the query to delete the row
        query = f"DELETE FROM {schema}.postcodes WHERE postcode_id = %s;"
        cur.execute(query, (postcode_id,))

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

    # Test the function
    # postcode = "ZM19"  # Replace with your desired postcode
    # result = webscrape_to_determine_valid_postcode(postcode)
    # print(result)
    # Example usage
    # postcode = 'SW1A 1AA'  # Replace with the desired postcode
    # is_valid = webscrape_check_valid_postcode(postcode)
    # print(is_valid)