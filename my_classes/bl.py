from my_classes.db import DBClass
from my_classes.aux_tools import AuxClass
from my_classes.sp import SpClass 
from my_classes.su import SuClass
from my_classes.geo import GeoClass
import json
import random

class BusinessLogicClass:
    def __init__(self, db_class = None):
        # self.db_class = db_class
        self.db_obj = DBClass()
        self.db_sys_obj = DBClass(config_file='C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt')
        self.aux_obj_sys = AuxClass(db_class=self.db_sys_obj)
        self.aux_obj_db = AuxClass(db_class=self.db_obj)
        self.sp_obj = SpClass(db_class=self.db_obj)  # default db path is being used here
        self.su_obj = SuClass(db_class=self.db_obj)
        self.geo_obj = GeoClass(db_class=self.db_sys_obj)
        # db_obj = DBClass()
        # db_sys_obj = DBClass(config_file='C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt')
        # self.sp_obj = SpClass(db_obj)
        # self.su_obj = SuClass(db_obj)
        # self.aux_obj_sys = AuxClass(db_sys_obj)
        # self.aux_obj_db = AuxClass(db_obj)
        # self.bl_obj = BusinessLogicClass(db_obj)
        # self.geo_obj = GeoClass(db_sys_obj)


    def get_all_potential_skills_for_su_id(self, schema, su_id):
        conn = self.db_obj.connect()
        # Create a cursor object
        cur = conn.cursor()
        
        # query = f"SELECT s.skill_id, s.skill_name FROM {schema}.service_user su JOIN {schema}.contractor c ON su.su_id = c.su_id JOIN {schema}.service_provider_staff sps ON c.staff_id = sps.sp_staff_id JOIN {schema}.skills_list s ON sps.sp_id = s.sp_id WHERE su.su_id = {su_id}"
        # cur.execute(query)
        # cur.execute(f"""
        # SELECT c.su_id, sl.skill_name, sps.first_name, sps.last_name, sp.name AS service_provider_name
        # FROM {schema}.contractor c
        # JOIN {schema}.staff_skill ss ON c.sp_id = ss.sp_staff_id
        # JOIN {schema}.skills_list sl ON ss.skills_list_id = sl.skills_list_id
        # JOIN {schema}.service_provider_staff sps ON ss.sp_staff_id = sps.sp_staff_id
        # JOIN {schema}.service_provider sp ON c.sp_id = sp.sp_id
        # WHERE c.su_id = {su_id};

        # """)
        # cur.execute(f"""
        # SELECT c.su_id, sl.skills_list_id, sl.skill_name, sps.sp_id
        # FROM {schema}.contractor c
        # JOIN {schema}.staff_skill ss ON c.sp_id = ss.sp_staff_id
        # JOIN {schema}.skills_list sl ON ss.skills_list_id = sl.skills_list_id
        # JOIN {schema}.service_provider_staff sps ON ss.sp_staff_id = sps.sp_staff_id
        # JOIN {schema}.service_provider sp ON c.sp_id = sp.sp_id
        # WHERE c.su_id = {su_id};

        # """)

        cur.execute(f"""SELECT c.su_id, sl.skills_list_id, sl.skill_name, sps.sp_id
        FROM {schema}.contractor c
        JOIN {schema}.staff_skill ss ON c.sp_id = ss.sp_staff_id
        JOIN {schema}.skills_list sl ON ss.skills_list_id = sl.skills_list_id
        JOIN {schema}.service_provider_staff sps ON ss.sp_staff_id = sps.sp_staff_id
        JOIN {schema}.service_provider sp ON c.sp_id = sp.sp_id
        WHERE c.su_id = {su_id}
        GROUP BY c.su_id, sl.skills_list_id, sl.skill_name, sps.sp_id
        HAVING COUNT(*) = 1;

        """)


        result = cur.fetchall()
        
        conn.close()
        json_result = json.dumps(result)
        return json_result

    def get_potential_skills_from_sp(self, schema, su_id, sp_id):
        sp_obj = SpClass()
        sp_obj.get_sp_id_restricted_potential_skills_for_su_id(su_id, sp_id)
    # import json

    # def get_sp_id_restricted_potential_skills_for_su_id(self, schema, su_id, sp_id):
    #     conn = self.db_class.connect()
    #     # Create a cursor object
    #     cur = conn.cursor()
        
    #     query = f'''
    #         SELECT sl.skill_name, c.sp_id
    #         FROM {schema}.skills_list AS sl
    #         JOIN {schema}.contractor AS c ON sl.sp_id = c.sp_id
    #         WHERE c.su_id = {su_id} AND c.sp_id = {sp_id}
    #     '''
    #     cur.execute(query)
    #     result = cur.fetchall()
        
    #     conn.close()
    #     json_result = json.dumps(result)
    #     return json_result


    def insert_random_skills_for_sps(self, schema, sp_obj):
        skills = ['skill1', 'skill2', 'skill3','skill1a', 'skill2b', 'skill3c','skill11b', 'skill2c', 'skill3a','skill1b', 'skill11', 'skill12','skill1a', 'skill2b', 'skill3c','skill11b', 'skill2c', 'skill3a','skill1b', 'skill11', 'skill12']
        sps = json.loads(self.sp_obj.return_all_sp_ids(schema))
        for sp in sps:
            sp_id = sp[0]
            for i in range(random.randint(1,len(skills))): # randomly assign between 1 and 7 skills to that sp
                            skill = random.choice(skills)
                            self.sp_obj.insert_random_skill(schema, sp_id, skill)



    def insert_staff_skills(self, schema, sp_obj):
        sps = json.loads(self.sp_obj.return_all_sp_ids(schema))
        for sp in sps:
            sp_id = sp[0]
            skills_res = self.sp_obj.return_skills_for_sp_id(schema, sp_id)
            skills = [item[0] for item in skills_res]
            n = len(skills)
            if len(skills) == 0:
                continue
            print(f'SP skills {sp_id} = {skills}')
            staff_ids = self.sp_obj.return_all_staff_ids_for_sp_id(schema, sp_id)
            for s_id in staff_ids:
                rand_skill_selection = random.sample(skills, random.randint(1, n))
                print(rand_skill_selection)
                for skill in rand_skill_selection:
                    self.sp_obj.insert_staff_skills(schema, s_id, skill)
          

    def set_potential_services(self, schema, sp_obj):
        self.insert_random_skills_for_sps(schema, sp_obj)
        self.insert_staff_skills(schema, sp_obj)



    def insert_providers_for_each_service_user(self, sp_obj, su_obj, geo_obj):
        json_schemas = self.sp_obj.get_all_schemas()
        schemas = json.loads(json_schemas)
        # schema = schemas[0]
        count = 0 
        with open('C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\google_api.txt', 'r') as file:
            key = file.read().strip()
        for schema in schemas:
            all_sp_ids =json.loads( self.sp_obj.return_all_sp_ids(schema))
            json_service_users = self.su_obj.get_all_service_users(schema)
            service_users = json.loads(json_service_users)
            for su_id, su_name in service_users:
                fraction_of_providers = json.loads(self.sp_obj.return_a_fraction_of_providers(0.5, all_sp_ids))
                su_postcode = json.loads(self.su_obj.get_postcode_for_su(schema, su_id))
                for sp_id, sp_name in fraction_of_providers:
                    # if random.random() < 0.5:
                    print(f'Inserting to contractor - su_id = {su_id} {su_name} - sp_id = {sp_id} {sp_name}')
                    su_obj.insert_contractor_details(schema, sp_id, su_id)
                    all_staff_id_pc_max_comm = json.loads(self.sp_obj.get_all_staff_id_pc_max_commute_for_sp(schema, sp_id))
                    for staff_id, staff_postcode, max_commute in all_staff_id_pc_max_comm:
                        count +=1
                        print(f'Compare postcodes for Site @ {su_postcode} with Staff {staff_id} from {staff_postcode}/{sp_name} & Max Commute = {max_commute*3} [{count} INSERTS]')
                        distance = self.geo_obj.googlemaps_determine_distance(staff_postcode, su_postcode, key)
                        if distance <= max_commute:
                            proximate = True
                        else:
                            proximate = False
                        self.sp_obj.insert_proximity_matrix( schema, staff_id, su_id, proximate, distance, max_commute)
                    print('*'*80)


    # def create_schemas(num_sp1s):
    #     sp1s = []
    #     aux_obj_db.delete_sp1_schemas() # before starting again
    #     range_limit = num_sp1s #+ 1
    #     for i in range(range_limit):
    #         tuples = aux_obj_sys.get_random_postcode_and_address(1)
    #         sp_id, provider_name, address, postcode = tuples[0]
    #         schema_name = 'sp1' + '_' + aux_obj_sys.remove_special_chars(tuples[0][1]).lower()
    #         sp_obj.create_schema_and_tables(schema_name)
    #         distance = random.choice(range(1, 11)) * 5  # Random distance from [5, 10, ..., 50]
    #         sp1s.append(sp_obj.insert_provider(schema_name,provider_name, address, postcode, distance, parent_id=0, sp_level='sp1'))
    #         res = f'{provider_name} @ sp1'
    #         print(res)
    #         aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)
    #     return sp1s
    
    # def create_sp_records(n, sp_max):
    #         children = json.loads(aux_obj_db.generate_child_distribution(sp_max))
    #         count = 0
    #         # skills = ['skill1', 'skill2', 'skill3','skill1a', 'skill2b', 'skill3c','skill11b', 'skill2c', 'skill3a','skill1b', 'skill11', 'skill12']
    #         schemas = json.loads(sp_obj.get_all_schemas())
    #         for schema in schemas:
    #             x = n - 1
    #             sp_details = json.loads(sp_obj.get_all_spxs_for_schema(schema, x))
    #             for sp_detail in sp_details:
    #                 if count >= len(children):
    #                     num_children = 0
    #                     count += 1
    #                     continue
    #                 else:
    #                     num_children = children[count]
    #                 count += 1
    #                 print(f'nodes for {sp_detail[1]} is {num_children}')
    #                 p_id = sp_detail[0]
    #                 # num_children = random.randint(sp_min, sp_max)
    #                 for j in range(num_children):
    #                     tuples = aux_obj_sys.get_random_postcode_and_address(1)
    #                     sp_id, provider_name, address, postcode = tuples[0]
    #                     parent_name = sp_detail[1]
    #                     if random.random() < 0.5:
    #                         distance = random.choice(range(1, 11)) * 5  # Random distance from [5, 10, ..., 50]
    #                     else:
    #                         distance = None
    #                     sp_id = sp_obj.insert_provider(schema,provider_name, address, postcode, distance, p_id, sp_level=f'sp{n}') 
    #                     res = f'[sp{n}] - {provider_name} CHILD => PARENT {parent_name}'
    #                     print(res)
    #                     aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)


    # def add_staff_for_sp(x):
    #     schemas = json.loads(sp_obj.get_all_schemas())
    #     for schema in schemas:
    #         sp_details = json.loads(sp_obj.get_all_spxs_for_schema(schema, x))
    #         for sp in sp_details:
    #             num_staff = random.randint(40, 150)
    #             data = aux_obj_sys.fake_staff_data(num_staff)
    #             for datum in data:
    #                 tup = (sp[0],) + datum
    #                 sp_obj.insert_staff(schema, tup) #TODO add sp_id of provider staff works for 
    #                 res = f'{datum} added to [{sp[1]}] sp{x}'
    #                 print(res)
    #                 aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)

    
    # def create_random_schemas(n):
    #     sp_levels = 4
    #     sp_min = 3
    #     sp_max = 6
    #     num_sps= random.randint(sp_min, sp_max)
    #     sp1s = create_schemas(1)
    #     range_limit = sp_levels + 1
    #     for i in range(2, range_limit):
    #         create_sp_records(i, sp_max)
    #     generate_and_insert_su(aux_obj_sys, aux_obj_db, sp_obj, su_obj)
    #     for j in range(1, range_limit):
    #         add_staff_for_sp(j)    
                    