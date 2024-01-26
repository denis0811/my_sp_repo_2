# from my_package.aux1 import get_next_index
import random
import json

class SpClass:
    def __init__(self, db_class):
        self.db_class = db_class
        self.json_schemas = None
        # self.sp_obj = None

    def get_schema(self):
        json_schemas = self.get_all_schemas()
        if json_schemas is not None:
            schemas = json.loads(json_schemas)
            if len(schemas) > 0:
                return schemas[0]
        return None
    
    def create_schema_and_tables(self, schema_name):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        # Create the schema with the given name
        cur.execute(f"CREATE SCHEMA  IF NOT EXISTS {schema_name}")

        cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")


#************************************************* FUCTIONS *************************************************#
        # Create the CREATE FUNCTION SQL command for the "count_staff_by_sp_id" function
        cur.execute(f"""
            CREATE OR REPLACE FUNCTION public.count_staff_by_sp_id(schema_name TEXT, sp_id INTEGER)
            RETURNS INTEGER AS $$
            DECLARE
                query TEXT;
                result INTEGER;
            BEGIN
                query := 'SELECT COUNT(*) FROM ' || quote_ident(schema_name) || '.service_provider_staff WHERE sp_id = ' || sp_id;
                EXECUTE query INTO result;
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
        """)

        
        query = f"""
        CREATE OR REPLACE FUNCTION public.get_sp_name_for_staff_id(schema_name TEXT, staff_id INTEGER)
                RETURNS TEXT AS $$
                DECLARE
                    sp_name TEXT;
                BEGIN
                    EXECUTE 'SELECT name FROM ' || quote_ident(schema_name) || '.service_provider sp JOIN ' || quote_ident(schema_name) || '.service_provider_staff sps ON sp.sp_id = sps.sp_id WHERE sps.sp_staff_id = ' || staff_id || ' INTO sp_name;';

                    RETURN sp_name;
                END;
                $$ LANGUAGE plpgsql;

        """

        cur.execute(query)



     
        # query = """
        # CREATE OR REPLACE FUNCTION {schema_name}.get_sp_name_by_staff_id(schema_name TEXT, staff_id INTEGER)
        # RETURNS TEXT
        # AS $$
        # BEGIN
        #     RETURN (
        #         SELECT name
        #         FROM {schema_name}.service_provider
        #         WHERE sp_id = (
        #             SELECT sp_id
        #             FROM {schema_name}.service_provider_staff
        #             WHERE sp_staff_id = $2
        #         )
        #     );
        # END;
        # $$ LANGUAGE plpgsql;
        # """.format(schema_name=schema_name)

        # cur.execute(query)

        query = f"""
                CREATE OR REPLACE FUNCTION public.get_sp_name_by_staff_id(schema_name TEXT, staff_id INTEGER)
                RETURNS TEXT
                AS $$
                BEGIN
                    RETURN (
                        SELECT name
                        FROM schema_name.service_provider
                        WHERE sp_id = (
                            SELECT sp_id
                            FROM schemaname.service_provider_staff
                            WHERE sp_staff_id = $2
                        )
                    );
                END;
                $$ LANGUAGE plpgsql;
                """
        #.format(schema_name=schema_name)

        cur.execute(query)


        cur.execute(f"""
            CREATE OR REPLACE FUNCTION public.get_parent_contractor(schema_name TEXT, input_sp_id INTEGER)
            RETURNS TABLE (name TEXT, sp_id INTEGER)
            AS $$
            BEGIN
                RETURN QUERY EXECUTE format('
                    SELECT name, sp_id
                    FROM schema_name.service_provider
                    WHERE sp_id = (
                        SELECT parent_id
                        FROM %I.service_provider
                        WHERE sp_id = %s
                    )', schema_name, schema_name, input_sp_id);
            END;
            $$ LANGUAGE plpgsql;
        """)

    # SELECT *
    # FROM get_parent_contractor('your_schema_name', your_sp_id);



        cur.execute(f"""
            CREATE OR REPLACE FUNCTION public.get_children_of_sp_id(schema_name TEXT, parent_sp_id INTEGER, OUT child_sp_id INTEGER, OUT child_name TEXT)
            RETURNS SETOF record
            AS $$
            BEGIN
                RETURN QUERY (
                    SELECT sp_id, name
                    FROM schema_name.service_provider
                    WHERE parent_id = parent_sp_id
                );
                RETURN;
            END;
            $$ LANGUAGE plpgsql;
            """)

        cur.execute(f"""
            CREATE OR REPLACE FUNCTION public.get_main_contractor_name(schema_name TEXT)
            RETURNS TEXT
            AS $$
            BEGIN
                RETURN (
                    SELECT name
                    FROM schema_name.service_provider
                    WHERE parent_id = 0
                );
            END;
            $$ LANGUAGE plpgsql;
            """)



        cur.execute(f"""
            CREATE OR REPLACE FUNCTION public.get_provider_name(schema_name TEXT, input_sp_id INTEGER)
            RETURNS TEXT AS
            $$
            BEGIN
            RETURN (
                SELECT name
                FROM schema_name.service_provider
                WHERE sp_id = input_sp_id
            );
            END;
            $$
            LANGUAGE plpgsql;
            """)
#************************************************* FUCTIONS END*************************************************#

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.service_provider (
            sp_id SERIAL PRIMARY KEY,
            name TEXT,
            address TEXT,
            postcode TEXT,
            parent_id INTEGER,
            sp_level TEXT,
            sp_guid UUID DEFAULT uuid_generate_v4() UNIQUE,
            max_distance INTEGER DEFAULT 100,
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.skills_list (
            skills_list_id SERIAL PRIMARY KEY,
            skill_name VARCHAR(255),
            sp_id INTEGER,
            CONSTRAINT fk_service_provider
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE,
            CONSTRAINT uc_skill_sp UNIQUE (skill_name, sp_id)
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.service_provider_staff (
            sp_staff_id SERIAL PRIMARY KEY,
            sp_id INTEGER,
            first_name VARCHAR NOT NULL,
            middle_name VARCHAR,
            last_name VARCHAR,
            address VARCHAR,
            postcode VARCHAR,
            telephone VARCHAR,
            email VARCHAR,
            sp_staff_guid UUID DEFAULT uuid_generate_v4(),
            national_insurance_number VARCHAR,
            max_commute INTEGER,
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.service_user (
            su_id SERIAL PRIMARY KEY,
            name TEXT,
            address TEXT,
            postcode TEXT,
            service_user_guid UUID DEFAULT uuid_generate_v4(),
            sp_id INTEGER REFERENCES {schema_name}.service_provider(sp_id),
            parent_id INTEGER DEFAULT 0,
            outsourced_id INTEGER DEFAULT 0,
            CONSTRAINT unique_service_user_name_postcode UNIQUE (name, postcode),
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.staff_skill (
            staff_skill_id SERIAL PRIMARY KEY,
            skills_list_id INTEGER,
            sp_staff_id INTEGER,
            CONSTRAINT fk_skills_list
                FOREIGN KEY (skills_list_id)
                REFERENCES {schema_name}.skills_list(skills_list_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_sp_staff
                FOREIGN KEY (sp_staff_id)
                REFERENCES {schema_name}.service_provider_staff(sp_staff_id)
                ON DELETE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.proximity_matrix (
            proximity_matrix_id SERIAL PRIMARY KEY,
            staff_id INTEGER NOT NULL,
            sp_id INTEGER NOT NULL,
            su_id INTEGER NOT NULL,
            distance DECIMAL,
            max_distance DECIMAL,
            proximate BOOLEAN,
            proximity_guid UUID DEFAULT uuid_generate_v4(),
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_staff_id
                FOREIGN KEY (staff_id)
                REFERENCES {schema_name}.service_provider_staff(sp_staff_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.shift_pattern (
            pattern_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            pattern VARCHAR NOT NULL UNIQUE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.service_provider_booking (
            service_provider_booking_id SERIAL PRIMARY KEY,
            sp_id INTEGER,
            sp_staff_id INTEGER,
            pattern_id INTEGER,
            sp_rota_guid UUID DEFAULT uuid_generate_v4(),
            CONSTRAINT fk_staff_id
                FOREIGN KEY (sp_staff_id)
                REFERENCES {schema_name}.service_provider_staff(sp_staff_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_pattern_id
                FOREIGN KEY (pattern_id)
                REFERENCES {schema_name}.shift_pattern(pattern_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.contractor (
            contractor_id SERIAL PRIMARY KEY,
            sp_id INTEGER,
            su_id INTEGER,
           -- staff_id INTEGER,
            contract_details_id INTEGER,
            CONSTRAINT fk_sp_id
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_su_id
                FOREIGN KEY (su_id)
                REFERENCES {schema_name}.service_user(su_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
           -- CONSTRAINT fk_staff_id
           --     FOREIGN KEY (staff_id)
            --    REFERENCES {schema_name}.service_provider_staff(sp_staff_id)
            --    ON DELETE SET NULL
           --     ON UPDATE CASCADE
        );
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.service_user_rota (
            service_user_rota_id SERIAL PRIMARY KEY,
            skills_list_id INTEGER,
            start_date DATE,
            end_date DATE,
            start_time TIME,
            end_time TIME,
            total_skill_ids_in_time_slot INTEGER,
            sp_id INTEGER,
            staff_id INTEGER,
            su_rota_guid UUID DEFAULT uuid_generate_v4(),
            CONSTRAINT fk_service_provider
                FOREIGN KEY (sp_id)
                REFERENCES {schema_name}.service_provider(sp_id)
                ON DELETE CASCADE
        );
        """)


        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

    
    def insert_provider(self, schema_name, name, address, postcode, max_distance, parent_id=0, sp_level=None ):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        # Create the schema with the given name
        # sql = f'INSERT INTO "{schema_name}"."service_provider" (name, address, postcode, parent_id, sp_level) VALUES (%s, %s, %s, %s, %s);'
        sql = f'INSERT INTO "{schema_name}"."service_provider" (name, address, postcode, max_distance, parent_id, sp_level) VALUES (%s, %s, %s, %s,%s, %s) RETURNING sp_id;'
        if parent_id is None:
            parent_id = 'NULL'
        if sp_level is None:
            sp_level = 'NULL'
        cur.execute(sql, (name, address, postcode, max_distance, parent_id, sp_level))
        sp_id = cur.fetchone()[0]

        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()
        
        return sp_id
    

    def get_sp1_for_schema(self, schema_name):
        sql = f"SELECT sp_id FROM {schema_name}.service_provider WHERE parent_id = 0 LIMIT 1;"
        results = self.db_class.query(sql)
        sp_id = results[0][0] if results else None
        return json.dumps(sp_id)
    

    def get_all_spxs_for_schema(self, schema_name, x):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        sql =  f"SELECT sp_id, name, sp_level, parent_id FROM {schema_name}.service_provider WHERE sp_level = 'sp{x}';"
        # Execute the query.
        results = self.db_class.query(sql)
        # Close the cursor.
        cur.close()
        # Return the results.
        return json.dumps(results)
    
    
    def get_all_sps_for_schema(self, schema_name):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        sql = f"SELECT sp_id, name, sp_level, parent_id FROM {schema_name}.service_provider"
    
        # Execute the query.
        results = self.db_class.query(sql)
        # Close the cursor.
        cur.close()
        # Return the results.
        return json.dumps(results)
    
    def get_all_sp_ids_for_schema(self, schema_name):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        sql = f"SELECT sp_id, name, sp_level, parent_id FROM {schema_name}.service_provider"

        # Execute the query.
        cur.execute(sql)
        # Fetch all the rows returned by the query.
        rows = cur.fetchall()
        # Close the cursor.
        cur.close()
        # Create a list to store the sp_ids.
        sp_ids = [row[0] for row in rows]
        # Return the sp_ids as JSON.
        # return json.dumps(sp_ids)
        return sp_ids



    def insert_staff(self, schema_name,tup):
        #(first_name, middle_name, last_name, address, postcode, phone, email)
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        # query = f"INSERT INTO {schema_name}.service_provider_staff (sp_id, first_name, middle_name, last_name, address, postcode, telephone, email, national_insurance_number, max_commute) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        query = f"INSERT INTO {schema_name}.service_provider_staff (sp_id, first_name, middle_name, last_name, address, postcode, telephone, email, national_insurance_number, max_commute) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(query, (tup))
        conn.commit()
        conn.close()


    def return_skills_for_sp_id(self, schema_name, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        query = f"SELECT skills_list_id FROM {schema_name}.skills_list WHERE sp_id = {sp_id}"
        cur.execute(query)
        result = cur.fetchall()

        conn.close()

        return result



    def get_all_schemas(self):
        schemas =[]
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        sql = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema' AND schema_name != 'public';"
        cur.execute(sql)
        schemas = [schema[0] for schema in cur.fetchall() if schema[0].startswith('sp1_')]
        json_schemas = json.dumps(schemas)
        return json_schemas
    

    def return_parent_name(self, schema_name, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        # Execute the SQL query
        cur.execute(f"SELECT s1.name AS child_name, s2.name AS parent_name \
                      FROM {schema_name}.service_provider AS s1 \
                      JOIN {schema_name}.service_provider AS s2 \
                      ON s1.parent_id = s2.sp_id \
                      WHERE s1.sp_id = {sp_id};")
        
        # Get the results and return the parent name, or return None if no results
        results = cur.fetchone()
        if results is not None:
            parent_name = results[1]
            return parent_name
        else:
            return None
        

    def return_sp_name(self, schema_name, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(f"SELECT name FROM {schema_name}.service_provider WHERE sp_id = {sp_id};")
        result = cur.fetchone()
        if result is not None:
            sp_name = result[0]
            return json.dumps(sp_name)
        else:
            print(f"No service provider found with id {sp_id}")
            return None

    def func_count_staff_by_sp_id(self, schema, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(f"SELECT public.count_staff_by_sp_id('{schema}', {sp_id})")
        result = cur.fetchone()
        # Process the results as needed
        cur.close()
        conn.close()
        if result is not None:
            count = result[0]
            return count
        else:
            print(f"No service provider found with provider_id{sp_id}")
            return None


    def func_get_provider_from_sp_id(self, schema_name, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(
            f'''
        CREATE OR REPLACE FUNCTION "{schema_name}".delete_service_provider(input_sp_id INTEGER)
        RETURNS VOID AS $$
        BEGIN
            EXECUTE 'DELETE FROM ' || quote_ident('{schema_name}') || '.service_provider WHERE sp_id = ' || input_sp_id;
        END;
        $$ LANGUAGE plpgsql;
    '''
            )
        cur.execute(f"SELECT {schema_name}.get_provider_name('{schema_name}', {sp_id})")
        result = cur.fetchone()[0] if cur.rowcount > 0 else None
        cur.close()
        conn.close()

        return result


    def func_get_provider_names(self, schema_name):
        conn = self.db_class.connect()
        cur = conn.cursor()
        
        # Drop the function if it exists
        cur.execute(f'DROP FUNCTION IF EXISTS "{schema_name}".get_provider_names()')
        conn.commit()
        
        # Create the function with the updated return type
        function_sql = f'''
            CREATE OR REPLACE FUNCTION "{schema_name}".get_provider_names()
            RETURNS TABLE (provider_id INTEGER, provider_name TEXT, parent_id INTEGER) AS $$
            BEGIN
                RETURN QUERY SELECT sp_id AS provider_id, name AS provider_name, service_provider.parent_id FROM "{schema_name}".service_provider;
            END;
            $$ LANGUAGE plpgsql;
        '''
        
        cur.execute(function_sql)
        conn.commit()
        
        cur.execute(f'SELECT * FROM "{schema_name}".get_provider_names()')
        result = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return result




    def func_delete_service_provider(self, schema, sp_id):
        pass
        # conn = self.db_class.connect()
        # cur = conn.cursor()
        # cur.callproc('public.delete_sp', [schema, sp_id])
        # result = cur.fetchone()[0]  # Extract the result from the returned tuple
        # cur.close()
        # conn.close()


    def get_children_and_grandchildren(self, schema_name, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        # query = f"""
        # WITH RECURSIVE child_hierarchy AS (
        #     SELECT sp_id, name, parent_id
        #     FROM {schema_name}.service_provider
        #     WHERE sp_id = %s
        #     UNION ALL
        #     SELECT sp.sp_id, sp.name, sp.parent_id
        #     FROM {schema_name}.service_provider sp
        #     INNER JOIN child_hierarchy ch ON sp.parent_id = ch.sp_id
        # )
        # SELECT *
        # FROM child_hierarchy
            # """
        query = f"""
        WITH RECURSIVE child_hierarchy AS (
            SELECT sp_id, name, parent_id
            FROM {schema_name}.service_provider
            WHERE sp_id = %s
            UNION ALL
            SELECT sp.sp_id, sp.name, sp.parent_id
            FROM {schema_name}.service_provider sp
            INNER JOIN child_hierarchy ch ON sp.parent_id = ch.sp_id
        )
        SELECT *
        FROM child_hierarchy
        WHERE sp_id <> %s  -- Exclude the initial parent
        """
        with cur as cursor:
            cursor.execute(query, (sp_id, sp_id))
            result = cursor.fetchall()

        return result


        # Call the function to retrieve children and grandchildren
        sp_id = 1  # Replace with the desired sp_id
        result = get_children_and_grandchildren(connection, sp_id)

        # Print the result
        for row in result:
            print(row)

        cur.close()
        conn.close()

    def get_sp_ids_of_children_and_grandchildren(self, schema_name, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        query = f"""
        WITH RECURSIVE child_hierarchy AS (
            SELECT sp_id, parent_id
            FROM {schema_name}.service_provider
            WHERE sp_id = %s
            UNION ALL
            SELECT sp.sp_id, sp.parent_id
            FROM {schema_name}.service_provider sp
            INNER JOIN child_hierarchy ch ON sp.parent_id = ch.sp_id
        )
        SELECT sp_id
        FROM child_hierarchy
        WHERE sp_id <> %s  -- Exclude the initial parent
        """

        with cur as cursor:
            cursor.execute(query, (sp_id, sp_id))
            result = [row[0] for row in cursor.fetchall()]

        return result



    def delete_sp(self, schema, sp_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(f"""
            DELETE FROM {schema}.service_provider
            WHERE sp_id = %s
            """, (sp_id,))
        conn.commit()

        cur.close()
        conn.close()


    def return_all_sp_ids(self, schema_name):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(f"SELECT sp_id, name FROM {schema_name}.service_provider")
        all_sp_ids = cur.fetchall()
        json_all_sp_ids = json.dumps(all_sp_ids)
        return json_all_sp_ids


    def return_a_fraction_of_providers(self, n, sp_ids):
        rand_num_providers = int(len(sp_ids) * n)
        random.shuffle(sp_ids)
        providers = sp_ids[0:rand_num_providers]
        json_providers = json.dumps(providers)
        return json_providers

    def add_fraction_of_providers_to_contractor_table(cur, schema_name, n, su_id):
        # Step 1: Retrieve all sp_id and name from the service_provider table
        cur.execute(f"SELECT sp_id, name FROM {schema_name}.service_provider")
        all_sp_ids = cur.fetchall()


    
    def insert_contractor(self, schema_name, sp_id, su_id):
        conn = self.db_class.connect()
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {schema_name}.contractor (sp_id, su_id)
            VALUES (%s, %s)
        """, (sp_id, su_id))
       

    def get_all_staff_id_pc_max_commute_for_sp(self, schema, sp_id):
        # Establish a database connection
        conn = self.db_class.connect()

        # Create a cursor to execute SQL queries
        cur = conn.cursor()

        # Execute the SQL query
        cur.execute(
            f"SELECT sp_staff_id, postcode, max_commute FROM {schema}.service_provider_staff WHERE sp_id = {sp_id}"
        )

        # Fetch all the rows returned by the query
        rows = cur.fetchall()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the fetched rows
        json_rows = json.dumps(rows)
        return json_rows


    def insert_proximity_matrix(self, schema, staff_id, su_id, proximate, distance, max_commute):
        # Establish a database connection
        conn = self.db_class.connect()

        # Create a cursor to execute SQL queries
        cur = conn.cursor()

        # Build the SQL query for inserting a row into the proximity_matrix table
        query = f"""
            INSERT INTO {schema}.proximity_matrix (staff_id, sp_id, su_id, distance, max_distance, proximate)
            VALUES ({staff_id}, 
                    (SELECT sp_id FROM {schema}.service_provider_staff WHERE sp_staff_id = {staff_id}), 
                    {su_id}, 
                    {distance},
                    {max_commute},
                    {proximate});
        """

        # Execute the SQL query
        cur.execute(query)

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

    def insert_random_skill(self, schema, sp_id, skill):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()

        query = f"INSERT INTO {schema}.skills_list (skill_name, sp_id) VALUES ('{skill}', {sp_id}) ON CONFLICT (skill_name, sp_id) DO NOTHING"


        cur.execute(query, (sp_id, skill))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

       
    def insert_staff_skills(self, schema_name, staff_id, skill_list_id):
        conn = self.db_class.connect()
        cur = conn.cursor()

        sql = f"INSERT INTO {schema_name}.staff_skill (skills_list_id, sp_staff_id) VALUES (%s, %s)"
        values = (skill_list_id, staff_id)

        cur.execute(sql, values)

        conn.commit()

        cur.close()
        conn.close()


    
    def return_all_staff_ids_for_sp_id(self, schema, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        query = f"SELECT sp_staff_id FROM {schema}.service_provider_staff WHERE sp_id = {sp_id}"
        cur.execute(query)
        result = cur.fetchall()
        
        conn.close()
        
        return result
    

    def get_sp_id_restricted_potential_skills_for_su_id(self, schema, su_id, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        query = f'''
            SELECT sl.skill_name, c.sp_id
            FROM {schema}.skills_list AS sl
            JOIN {schema}.contractor AS c ON sl.sp_id = c.sp_id
            WHERE c.su_id = {su_id} AND c.sp_id = {sp_id}
        '''
        cur.execute(query)
        result = cur.fetchall()
        
        conn.close()
        json_result = json.dumps(result)
        return json_result



    def get_sp_id_restricted_potential_skills_for_su_id_w_staff_names(self, schema, su_id, sp_id):
        conn = self.db_class.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        query = f'''
            SELECT sl.skill_name, c.sp_id, ss.first_name, ss.middle_name, ss.last_name
            FROM {schema}.skills_list AS sl
            JOIN {schema}.contractor AS c ON sl.sp_id = c.sp_id
            JOIN {schema}.service_provider_staff AS ss ON c.staff_id = ss.sp_staff_id
            WHERE c.su_id = {su_id} AND c.sp_id = {sp_id}
        '''
        cur.execute(query)
        result = cur.fetchall()
        
        conn.close()
        json_result = json.dumps(result)
        return json_result
    

    def get_contractors_and_skills_for_su_id(self, schema_name, su_id):
        conn = self.db_class.connect()
        try:
            # Create a cursor object
            cur = conn.cursor()
            sql = f"""
                SELECT c.sp_id, s.skills_list_id
                FROM {schema_name}.contractor c
                JOIN {schema_name}.skills_list s ON c.sp_id = s.sp_id
                WHERE c.su_id = %s;
            """
            # Execute the query with the provided su_id as a parameter.
            cur.execute(sql, (su_id,))
            # Fetch all the rows from the result set.
            results = cur.fetchall()
            # Close the cursor.
            cur.close()
            # Return the results as a JSON string.
            return json.dumps(results)
        finally:
            # Close the connection.
            conn.close()

# db_obj = DBClass()
# sp_obj = SpClass(db_class=db_obj)
# su_obj = SuClass(db_class=db_obj)
# schemas = sp_obj.get_all_schemas()
# all_sp_ids = sp_obj.return_all_sp_ids(schemas[0])
# fraction_of_providers = sp_obj.return_a_fraction_of_providers(0.5, all_sp_ids)
# all_su = su_obj.get_all_service_users(schemas[0])
# for su_id in all_su:
#     for sp_id, name in fraction_of_providers:
#      print(f'Insert to contractor - su_id = {su_id} - sp_id = {sp_id}')