import json


class SuClass:
    def __init__(self, db_class):
        self.db_class = db_class

    
    def insert_servce_user(self, schema, address, name, postcode, sp_id, parent_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        # Create the schema with the given name
        query = f'INSERT INTO {schema}.service_user (address, name, postcode, sp_id, parent_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (name, postcode) DO NOTHING;'
        params = (address, name, postcode, sp_id, parent_id)
        cur.execute(query, params)

        # Commit the changes to the database
        conn.commit()
        # Close the database connection
        conn.close()


    def get_all_service_users_ids(self, schema):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        # Retrieve all service user IDs from the specified schema and service provider ID
        query = f'SELECT su_id FROM {schema}.service_user;'
        cur.execute(query)
        records = cur.fetchall()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Extract and return the service user IDs from the records
        service_user_ids = [record[0] for record in records]
        return service_user_ids



    def get_all_service_users_for_sp_id(self, schema, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        # Retrieve all service users from the specified schema and service provider ID
        query = f'SELECT su_id, name FROM {schema}.service_user WHERE sp_id = %s;'
        params = (sp_id,)
        cur.execute(query, params)
        records = cur.fetchall()

        # Close the cursor and connection
        cur.close()
        conn.close()

        return records


    def get_all_service_users(self, schema):
        conn = self.db_class.connect()
        cur = conn.cursor()

        query = f"SELECT su_id, name FROM {schema}.service_user;"
        cur.execute(query)
        records = cur.fetchall()

        cur.close()
        conn.close()

        service_users = [{'name': record[1], 'su_id': record[0]} for record in records]
        json_records = json.dumps(service_users)
        return json_records


    def insert_contractor_details(self, schema, sp_id, su_id):
        conn = self.db_class.connect()
        cur = conn.cursor()

        # # Insert into service_provider_staff table
        # query = f"INSERT INTO {schema}.service_provider_staff (sp_id, staff_id) VALUES (%s, %s)"
        # cur.execute(query, (sp_id, staff_id))

        # Insert into contractor table
        query = f"INSERT INTO {schema}.contractor (sp_id, su_id) VALUES (%s, %s)"
        cur.execute(query, (sp_id, su_id))

        conn.commit()
        conn.close()


    def get_contractors_for_su_id(self, schema_name, su_id):
        contractors = []
        conn = self.db_class.connect()
        cur = conn.cursor()

        # Retrieve service_user name
        cur.execute(f"SELECT name FROM {schema_name}.service_user WHERE su_id = %s;", (su_id,))
        service_user_name = cur.fetchone()[0]

        # Retrieve contractors assigned to the service_user with ID and name
        cur.execute(f"SELECT p.sp_id, p.name FROM {schema_name}.service_provider AS p JOIN {schema_name}.contractor AS c ON p.sp_id = c.sp_id WHERE c.su_id = %s;", (su_id,))
        contractor_data = cur.fetchall()

        for contractor in contractor_data:
            contractor_dict = {
                'sp_id': contractor[0],
                'name': contractor[1]
            }
            contractors.append(contractor_dict)

        cur.close()
        conn.close()
        json_records = json.dumps(contractors)
        return json_records


    def get_skills_available_for_su_id(self, schema_name, su_id):
        skills = []
        conn = self.db_class.connect()
        cur = conn.cursor()

        # Retrieve skills available for the service_user
        query = f"""
            SELECT p.sp_id, s.sp_staff_id, sk.skills_list_id
            FROM {schema_name}.service_provider AS p
            JOIN {schema_name}.contractor AS c ON p.sp_id = c.sp_id
            JOIN {schema_name}.service_provider_staff AS s ON p.sp_id = s.sp_id
            JOIN {schema_name}.staff_skill AS ss ON s.sp_staff_id = ss.sp_staff_id
            JOIN {schema_name}.skills_list AS sk ON ss.skills_list_id = sk.skills_list_id
            WHERE c.su_id = %s;
        """
        cur.execute(query, (su_id,))
        skills_data = cur.fetchall()

        for skill in skills_data:
            skill_tuple = (
                skill[0],
                skill[1],
                skill[2]
            )
            skills.append(skill_tuple)

        cur.close()
        conn.close()

        json_records = json.dumps(skills)
        return json_records



    # def get_contractors_for_su_id(self, schema_name, su_id):
    #     contractors = []
    #     conn = self.db_class.connect()
    #     cur = conn.cursor()

    #     # Retrieve service_user name
    #     cur.execute(f"SELECT name FROM {schema_name}.service_user WHERE su_id = %s;", (su_id,))  # Pass su_id[0]
    #     service_user_name = cur.fetchone()[0]

    #     # Retrieve contractors assigned to the service_user
    #     cur.execute(f"SELECT p.name FROM {schema_name}.service_provider AS p JOIN {schema_name}.contractor AS c ON p.sp_id = c.sp_id WHERE c.su_id = %s;", (su_id,))  # Pass su_id[0]
    #     provider_names = cur.fetchall()

    #     contractors = [provider[0] for provider in provider_names]

    #     cur.close()
    #     conn.close()
    #     json_records = json.dumps(contractors)
    #     return json_records
    #     # return service_user_name, contractors
    

    def get_postcode_for_su(self, schema, su_id):
        # Establish a database connection
        conn = self.db_class.connect()

        # Create a cursor to execute SQL queries
        cur = conn.cursor()

        # Execute the SQL query
        cur.execute(
            f"SELECT postcode FROM {schema}.service_user WHERE su_id = {su_id}"
        )

        # Fetch the row returned by the query
        row = cur.fetchone()

        # Close the cursor and connection
        cur.close()
        conn.close()

        json_row0 = json.dumps(row[0])
        # Return the postcode value
        if row:
            return json_row0
        else:
            return None


    def get_all_sps_for_su_id(self, schema_name, su_id):
        conn = self.db_class.connect()
        cur = conn.cursor()

        # Retrieve service provider names and sp_id for the given su_id
        query = f"""
            SELECT sp.sp_id, sp.name
            FROM {schema_name}.service_provider AS sp
            JOIN {schema_name}.contractor AS c ON sp.sp_id = c.sp_id
            WHERE c.su_id = %s;
        """
        cur.execute(query, (su_id,))
        result = cur.fetchall()

        cur.close()
        conn.close()
        json_records = json.dumps(result)
        return json_records
