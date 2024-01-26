from my_classes.db import DBClass
from my_classes.aux_tools import AuxClass
from my_classes.sp import SpClass 
from my_classes.su import SuClass
from my_classes.geo import GeoClass
from my_classes.bl import BusinessLogicClass
import random
import json
from faker import Faker

class DatabaseSetup:
    def __init__(self):
        self.db_obj = DBClass()
        self.db_sys_obj = DBClass(config_file='C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt')
        self.aux_obj_sys = AuxClass(db_class=self.db_sys_obj)
        self.aux_obj_db = AuxClass(db_class=self.db_obj)
        self.sp_obj = SpClass(db_class=self.db_obj)
        self.su_obj = SuClass(db_class=self.db_obj)
        self.geo_obj = GeoClass(db_class=self.db_sys_obj)
        self.bl_obj = BusinessLogicClass(db_class=self.db_obj)

    def create_schemas(self, num_sp1s):
        print('in: create sp schemas ')
        sp1s = []
        self.aux_obj_db.delete_sp1_schemas()  # Delete existing schemas
        for _ in range(num_sp1s):
            tuples = self.aux_obj_sys.get_random_postcode_and_address(1)
            sp_id, provider_name, address, postcode = tuples[0]
            schema_name = 'sp1_' + self.aux_obj_sys.remove_special_chars(provider_name).lower()
            self.sp_obj.create_schema_and_tables(schema_name)
            distance = random.choice(range(1, 11)) * 5
            sp1s.append(self.sp_obj.insert_provider(schema_name, provider_name, address, postcode, distance, parent_id=0, sp_level='sp1'))
        return sp1s
    
    def create_sp_records(self, n, sp_max):
        print('in: create sp records ')
        children = json.loads(self.aux_obj_db.generate_child_distribution(sp_max))
        count = 0
        schemas = json.loads(self.sp_obj.get_all_schemas())
        for schema in schemas:
            x = n - 1
            sp_details = json.loads(self.sp_obj.get_all_spxs_for_schema(schema, x))
            for sp_detail in sp_details:
                num_children = children[count] if count < len(children) else 0
                count += 1
                for _ in range(num_children):
                    tuples = self.aux_obj_sys.get_random_postcode_and_address(1)
                    provider_name, address, postcode = tuples[0][1], tuples[0][2], tuples[0][3]
                    distance = random.choice(range(1, 11)) * 5 if random.random() < 0.5 else None
                    self.sp_obj.insert_provider(schema, provider_name, address, postcode, distance, sp_detail[0], sp_level=f'sp{n}')

    def generate_and_insert_su(self):
        print('in: generate and insert su ')
        schemas = json.loads(self.aux_obj_db.get_all_schemas())
        for schema in schemas:
            sp_id = json.loads(self.sp_obj.get_sp1_for_schema(schema))
            num_su = random.randint(3, 6)
            for _ in range(num_su):
                tuples = self.aux_obj_sys.get_random_postcode_and_address(1)
                su_name, address, postcode = tuples[0][1], tuples[0][2], tuples[0][3]
                self.su_obj.insert_servce_user(schema, address, su_name, postcode, sp_id, 0)

    def add_staff_for_sp(self, x):
        print('in: add staff for sp ')
        schemas = json.loads(self.sp_obj.get_all_schemas())
        for schema in schemas:
            sp_details = json.loads(self.sp_obj.get_all_spxs_for_schema(schema, x))
            for sp in sp_details:
                num_staff = random.randint(30, 100)
                staff_data = self.aux_obj_sys.fake_staff_data(num_staff)
                for staff in staff_data:
                    staff_tuple = (sp[0],) + staff  # sp[0] is the sp_id
                    self.sp_obj.insert_staff(schema, staff_tuple)
                    self.aux_obj_db.slow_print(staff_tuple)

    def set_services_for_sps_staff(self, schema):
        print(f'Setting services for SP staff in schema: {schema}')
        self.bl_obj.set_potential_services(schema, self.sp_obj)

    def build_schema_w_sps_sus_staff(self):
        print('Building schema with SPs, SUs, staff...')
        sp1s = self.create_schemas(1)
        sp_levels = 2
        sp_max = 3
        for i in range(2, sp_levels + 1):
            self.create_sp_records(i, sp_max)
        self.generate_and_insert_su()
        for j in range(1, sp_levels + 1):
            self.add_staff_for_sp(j)
        # skills that sps provide and the skills each staff member of that sp has 
        schema = self.sp_obj.get_schema()
        self.set_services_for_sps_staff(schema)

# Example Usage
database_setup = DatabaseSetup()
database_setup.build_schema_w_sps_sus_staff()