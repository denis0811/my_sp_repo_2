import random
from faker import Faker
import re
import time
import os
from geopy.geocoders import Nominatim
import json   
from datetime import datetime, timedelta

# from my_classes.db import db

class AuxClass:
    def __init__(self, db_class):
        self.db_class = db_class
        self.fake = Faker()    

    def get_next_index(self):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        # Create the index table if it doesn't exist
        cur.execute("CREATE TABLE IF NOT EXISTS index_table (next_index INTEGER)")

        # Get the current index value from the table
        cur.execute("SELECT next_index FROM index_table")
        result = cur.fetchone()

        if result is None:
            # If the table is empty, start the index at 1
            next_index = 1
            cur.execute("INSERT INTO index_table (next_index) VALUES (%s)", (next_index,))
        else:
            # Otherwise, increment the current index by 1
            next_index = result[0] + 1
            cur.execute("UPDATE index_table SET next_index = %s", (next_index,))

        # Commit the transaction and close the connection
        conn.commit()
        cur.close()
        conn.close()

        # Return the next index value to the calling program
        return next_index
    
    def delete_sp1_schemas(self):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()


        # Create a cursor object to execute SQL commands
        cur = conn.cursor()
        
        try:
            # get a list of all schemas
            cur.execute("SELECT schema_name FROM information_schema.schemata")
            schema_rows = cur.fetchall()
            
            # delete all schemas that start with 'sp1_'
            for row in schema_rows:
                schema_name = row[0]
                if schema_name.startswith('sp'):
                    cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
                    print(f"Deleted schema: {schema_name}")
                    
                # commit the changes
                conn.commit()
            print("All sp_ schemas have been deleted")
            
        except Exception as e:
            print("Error:", e)
            conn.rollback()
            
        finally:
            # close the cursor and connection
            cur.close()
            conn.close()


    def my_logs(self, logs_path, log_file, content):
        os.makedirs(logs_path, exist_ok=True)
        with open (os.path.join(logs_path, log_file), 'a') as fp:
            fp.write(content + '\n')
        fp.close()


    def read_file(self, file_path):
        rows = []
        with open(file_path, 'r') as file:
            rows = file.readlines()
            rows = [line.strip() for line in rows]
        return rows

    def write_to_file(file_path, content):
        with open(file_path, 'a') as file:
            file.write(content)




    def get_random_postcode_and_address(self, n):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        # Retrieve all records from the postcodes table and generate fake addresses and company names
        # cur.execute("SELECT * FROM postcodes")
        # Execute a SELECT query to fetch a random postcode
        cur.execute("SELECT postcode FROM postcodes ORDER BY random() LIMIT 1")

        fake = Faker('en_GB')
        count = 0
        results = []
        for row in cur.fetchall():
            count += 1
            if count > n:
                break
            id = self.get_next_index()
            fake_address = fake.street_address()
            fake_company = fake.company()
            results.append((id, fake_company, fake_address, row[0]))
            # print((fake_company, fake_address, row[0]))
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        # Return the list of postcode-address-company tuples
        return results


    def remove_special_chars(self, input_string):
            # replace commas, spaces, and special characters with an underscore,
            # unless an underscore is already present
            output_string = re.sub(r'[^\w\s]|(?<!_)_+(?!_)', '_', input_string)
            output_string = re.sub(r'\s+', '_', output_string)
            output_string = re.sub(r',', '_', output_string)
            
            # Remove commas, spaces, and special characters
            s = re.sub('[,\s\W]+', '_', output_string)
            
            # Replace consecutive underscores with a single underscore
            s = re.sub('_+', '_', output_string)
            return s


    def slow_print(self, string):
        for char in string:
            print(char, end='', flush=True)
            time.sleep(0.1)
        print()

    # def print_line_b_line(self, data):
    #     for sublist in data:
    #         print(' '.join(str(item) for item in sublist))


    def print_line_b_line(self, input):
        if isinstance(input, str):
            print(input)
        elif isinstance(input, (tuple, list)):
            for item in input:
                if isinstance(item, (tuple, list)):
                    print(' '.join(str(i) for i in item))
                else:
                    print(item)



    def get_all_schemas(self):
        sql = "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'sp1%';" 
        results = self.db_class.query(sql)
        schemas = [row[0] for row in results]
        return json.dumps(schemas)




    def fake_staff_data(self, num_tuples):
        # fake = Faker('en_GB')
        # distances = [5, 10, 15, 20, 25, 35, 50, 75]
        data = []
        for i in range(num_tuples):
            first_name = self.fake.first_name()
            middle_name = self.fake.first_name()
            last_name = self.fake.last_name()
            phone = self.fake.phone_number()
            email = None
            national_insurance_number = self.fake_ni_num()
            tuple = self.get_random_postcode_and_address(1) # calling the method using self
            address = tuple[0][2]  # assuming address is the second element in the tuple returned by get_random_postcode_and_address
            postcode = tuple[0][3] # assuming postcode is the first element in the tuple returned by get_random_postcode_and_address
            if random.random() < 0.5:
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            # distance = random.choice(distances)
            distance = random.choice(range(1, 12)) * 5  # Random distance from [5, 10, ..., 50]
            data.append((first_name, middle_name, last_name, address, postcode, phone, email, national_insurance_number, distance))
        return data


    def fake_ni_num(self):
        # The first two characters are letters
        letters = self.fake.random_letters(length=2)#.upper()
        u_letters = [letter.upper() for letter in letters]
        # The next six characters are digits
        digits = [random.randint(0, 9) for i in range(6)]
        # The last character is a letter
        last_letter = self.fake.random_letter().upper()
        # Combine the parts to create the NI number
        # ni_number = f"{u_letters}{digits}{last_letter}"
        ni_number = ''.join(u_letters) + ''.join(map(str, digits)) + ''.join(last_letter)

        return ni_number



    def check_postcode(postcode):
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


    def insert_from_text_file(self, file_path):
        conn = self.db_class.connect()
        cur = conn.cursor()

        with open(file_path, 'r') as file:
            for line in file:
                postcode = line.strip()  # Assuming each line contains only the postcode
                query = f"INSERT INTO postcodes (postcode) VALUES ('{postcode}') ON CONFLICT (postcode) DO NOTHING RETURNING postcode_id;"
                cur.execute(query)
                inserted_id = cur.fetchone()
                if inserted_id:
                    print(f"Inserted postcode_id: {inserted_id[0]} for postcode: {postcode}")
                else:
                    print(f"Skipped duplicate postcode: {postcode}")

        conn.commit()
        cur.close()
        conn.close()



    def generate_child_distribution(self, num_children):
        sum_list = []
        i = 1
        while sum(sum_list) < num_children:
            if num_children - sum(sum_list) >= i:
                sum_list.append(i)
            else:
                sum_list.append(num_children - sum(sum_list))
            i += 1

        random.shuffle(sum_list)
        return json.dumps(sum_list)


    def db_clean(self):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        try:
            # get a list of all schemas
            cur.execute("SELECT schema_name FROM information_schema.schemata")
            schema_rows = cur.fetchall()
            
            # delete all schemas that start with 'sp1_'
            for row in schema_rows:
                schema_name = row[0]
                if schema_name.startswith('sp'):
                    cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
                    print(f"Deleted schema: {schema_name}")
                    
                # commit the changes
                conn.commit()
            print("All sp_ schemas have been deleted")
            
        except Exception as e:
            print("Error:", e)
            conn.rollback()
            
        finally:
            # close the cursor and connection
            cur.close()
            conn.close()
 


    def generate_non_overlapping_times(self, start_date, end_date):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        time_lengths = [5, 6, 7, 8, 12, 16, 24]

        # Calculate the total number of available time slots within the date range
        total_slots = ((end_date - start_date).days + 1) * len(time_lengths)

        # Initialize a list to store generated time slots
        time_slots = []

        # Generate time slots starting at 22:30 and 23:00
        for date in [start_date, end_date]:
            start_time_1 = datetime(date.year, date.month, date.day, 22, 30)
            end_time_1 = start_time_1 + timedelta(hours=random.choice(time_lengths))
            time_slots.append((start_time_1, end_time_1))

            start_time_2 = datetime(date.year, date.month, date.day, 23)
            end_time_2 = start_time_2 + timedelta(hours=random.choice(time_lengths))
            time_slots.append((start_time_2, end_time_2))

        # Generate remaining random time slots
        for i in range(total_slots - 2):
            random_start_time = random.randint(0, 23)  # Random hour of the day
            random_length = random.choice(time_lengths)

            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

            start_time = datetime(random_date.year, random_date.month, random_date.day, random_start_time)
            end_time = start_time + timedelta(hours=random_length)  # Calculate end time by adding random length

            is_overlapping = False
            for slot in time_slots:
                if start_time <= slot[1] and end_time >= slot[0]:
                    is_overlapping = True
                    break

            if not is_overlapping:
                time_slots.append((start_time, end_time))

        return time_slots


    def find_duplicate_entries(self, json_string):
        data = json.loads(json_string)
        seen = set()
        duplicates = []

        for entry in data:
            entry_hash = hash(json.dumps(entry, sort_keys=True))
            if entry_hash in seen:
                duplicates.append(entry)
            else:
                seen.add(entry_hash)
        if duplicates:
            return True, duplicates
        else:
            return False, duplicates

# # Example usage
# json_string = '[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}, {"id": 1, "name": "John"}]'
# duplicates = find_duplicate_entries(json_string)
# print(duplicates)

# Example usage
# start_date = "2023-06-01"
# end_date = "2023-06-15"
# aux_obj = AuxClass(None)
# times = aux_obj.generate_non_overlapping_times(start_date, end_date)
# for start_time, end_time in times:
#     print(f"Start: {start_time}, End: {end_time}")

# # Example usage
# postcode = "CV2 2ZC"  # Replace with the postcode you want to check
# is_valid =AuxClass.check_postcode(postcode)
# print(is_valid)



