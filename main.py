from my_classes.db import DBClass
from my_classes.aux_tools import AuxClass
from my_classes.sp import SpClass 
from my_classes.su import SuClass
from my_classes.geo import GeoClass
from my_classes.bl import BusinessLogicClass
import random
import sys
import time
import msvcrt
import uuid
import json

def generate_and_insert_su(aux_obj_sys, aux_obj_db, sp_obj, su_obj):
    schemas= json.loads(aux_obj_db.get_all_schemas())
    for schema in schemas:
        sp_id = json.loads(sp_obj.get_sp1_for_schema(schema))
        aux_obj_sys.slow_print(f'{schema} / {sp_id}')
        # sp_id = schema["sp_id"]
        # aux_obj_sys.slow_print(f'{schema_name} - {sp_id}')
        num_su = random.randint(30, 60)
        for i in range(num_su):
            tuples = aux_obj_sys.get_random_postcode_and_address(1)
            NOT_USED_sp_id, su_name, address, postcode = tuples[0]
            su_obj.insert_servce_user(schema, address, su_name, postcode, sp_id, 0)
            sp_name = json.loads(sp_obj.return_sp_name(schema, sp_id))
            print(f'[SERVICE USER] {su_name} - [PROVIDER] {sp_id} - {sp_name}')

def get_providers(sp_obj, schema_name):
    providers = sp_obj.func_get_provider_names(schema_name)
    # Step 1: Retrieve and display all providers
    for provider in providers:
        provider_id = provider[0]
        provider_name = provider[1]
        # sp_id = provider[0]
        offspring = sp_obj.get_children_and_grandchildren(schema_name, provider_id)
        offspring_ids = sp_obj.get_sp_ids_of_children_and_grandchildren(schema_name, provider_id)
        # sp_name = provider[1]
        print(f"Offspring SP ID: {provider_id} ({provider_name}) : {offspring_ids }[{len(offspring)}]")
    return offspring_ids

if __name__ == "__main__":
    # ini_path = f'C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt'
    # db_class = DBClass(ini_path)
    # aux_obj = AuxClass(db_class=db_class)
    # for i in range(10980):
    #     res = aux_obj.get_next_index()3
    #     print(res)
    # level = ['sp1', 'sp2', 'sp3', 'sp4', 'sp5']
    db_obj = DBClass()
    db_sys_obj = DBClass(config_file='C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt')
    aux_obj_sys = AuxClass(db_class=db_sys_obj)
    aux_obj_db = AuxClass(db_class=db_obj)
    sp_obj = SpClass(db_class=db_obj)  # default db path is being used here
    su_obj = SuClass(db_class=db_obj)
    geo_obj = GeoClass(db_class=db_sys_obj)
    bl_obj = BusinessLogicClass(db_class=db_obj)
    
    


    # def create_sp_records(n):
    # # will be multiple sp2s per schema  to generate for
    #     sql = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema' AND schema_name != 'public';"
    #     schemas =  db_class.query(sql)
    #     for schema in schemas:
    #         schema_name = schema[0]
    #         idx = n - 1
    #         sql = f"SELECT sp_id FROM {schema_name}.service_provider WHERE sp_level = 'sp{idx}';"
    #         parent_ids = db_class.query(sql) #multiple to generate for
    #         for p_id in parent_ids:
    #             # if random.random() >= .45:
    #             #     num_children = 0
    #             # else:
    #             #     num_children = random.randint(sp_min, sp_max)
    #             num_children = 5 # random.randint(sp_min, sp_max)
    #             for j in range(num_children):
    #                 tuples = aux_obj_sys.get_random_postcode_and_address(1)
    #                 sp_id, provider_name, address, postcode = tuples[0]
    #                 sp_obj.insert_provider(schema_name,provider_name, address, postcode, parent_id=p_id[0], sp_level=f'sp{n}') #or just p_id check
    #                 print(f'[sp{n}] - {provider_name}')
    
    def create_schemas(num_sp1s):
        sp1s = []
        count = 0
        aux_obj_db.delete_sp1_schemas() # before starting again
        range_limit = num_sp1s #+ 1
        for i in range(range_limit):
            tuples = aux_obj_sys.get_random_postcode_and_address(1)
            sp_id, provider_name, address, postcode = tuples[0]
            count = count + 1 
            schema_name = 'sp1' + '_' + aux_obj_sys.remove_special_chars(tuples[0][1]).lower()
            sp_obj.create_schema_and_tables(schema_name)
            distance = random.choice(range(1, 11)) * 5  # Random distance from [5, 10, ..., 50]
            sp1s.append(sp_obj.insert_provider(schema_name,provider_name, address, postcode, distance, parent_id=0, sp_level='sp1'))
            res = f'{provider_name} @ sp1'
            print(res)
            aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)
        return sp1s
           

    def create_sp_records(n, sp_max):
            children = json.loads(aux_obj_db.generate_child_distribution(sp_max))
            count = 0
            schemas = json.loads(sp_obj.get_all_schemas())
            for schema in schemas:
                x = n - 1
                sp_details = json.loads(sp_obj.get_all_spxs_for_schema(schema, x))
                for sp_detail in sp_details:
                    if count >= len(children):
                        num_children = 0
                        count += 1
                        continue
                    else:
                        num_children = children[count]
                    print(f'nodes for {sp_detail[1]} is {num_children}')
                    p_id = sp_detail[0]
                    # num_children = random.randint(sp_min, sp_max)
                    for j in range(num_children):
                        tuples = aux_obj_sys.get_random_postcode_and_address(1)
                        sp_id, provider_name, address, postcode = tuples[0]
                        # provider_name = f'sp{n}_sp{x}_{p_id}_{uuid.uuid4()}'
                        parent_name = sp_detail[1]
                        if random.random() < 0.5:
                            distance = random.choice(range(1, 11)) * 5  # Random distance from [5, 10, ..., 50]
                        else:
                            distance = None
                        sp_id = sp_obj.insert_provider(schema,provider_name, address, postcode, distance, p_id, sp_level=f'sp{n}') 
                        res = f'[sp{n}] - {provider_name} CHILD => PARENT {parent_name}'
                        print(res)
                        # aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)


    def add_staff_for_sp(x):
        schemas = json.loads(sp_obj.get_all_schemas())
        for schema in schemas:
            sp_details = json.loads(sp_obj.get_all_spxs_for_schema(schema, x))
            for sp in sp_details:
                num_staff = random.randint(30, 120)
                data = aux_obj_sys.fake_staff_data(num_staff)
                for datum in data:
                    tup = (sp[0],) + datum
                    sp_obj.insert_staff(schema, tup) #TODO add sp_id of provider staff works for 
                    res = f'{datum} added to [{sp[1]}] sp{x}'
                    print(res)
                    # aux_obj_db.my_logs('my_logs', 'to_analyse.txt', res)

# ################################ Create random schemas ################################ 
# sp_levels = 4
# sp_min = 3
# sp_max = 5
# num_sps= random.randint(sp_min, sp_max)
# sp1s = create_schemas(1)
# range_limit = sp_levels + 1
# for i in range(2, range_limit):
#     create_sp_records(i, sp_max)
# generate_and_insert_su(aux_obj_sys, aux_obj_db, sp_obj, su_obj)
# for j in range(1, range_limit):
#     add_staff_for_sp(j)    
################################ Schemas done ################################

############################### Insert providers for each service user ################################


############################### Providers inserted for Service User ################################


############################### skills promised by sp and staff - encapsulate bl_obj.set_potential_services  ################################
# bl_obj.insert_providers_for_each_service_user( sp_obj, su_obj, geo_obj)
# json_schemas = sp_obj.get_all_schemas()
# schemas = json.loads(json_schemas)
# schema = schemas[0]
# bl_obj.set_potential_services(schema, sp_obj)
#  # TODO: details of Su rota, specifically who, when, is it repeating, skills, staff_preference
# start_date = "2023-06-01"
# end_date = "2023-06-15"
# su_ids = su_obj.get_all_service_users_ids(schema)
# # s_time_e_time_tuples  = aux_obj_db.generate_non_overlapping_times(start_date, end_date)
# for su_id in su_ids:
#     print(f'*{su_id}*'*20)
#     json_skills_available = bl_obj.get_all_potential_skills_for_su_id(schema, su_id)
#     any_duplication, duplicates = aux_obj_db.find_duplicate_entries(json_skills_available)
#     skills_available = json.loads(bl_obj.get_all_potential_skills_for_su_id(schema, su_id))
#     if any_duplication:
#         print (f'{duplicates} - {su_id}')
#     print(skills_available)
#     num_items = len(skills_available)
#     print(f'*{su_id}*'*20 + f' [{num_items}]')
# skill_ids_set = set(sp_obj.get_all_skill_id_for_sp_ids(sp_id))
# su_obj.insert_su_rota_row(s_date, e_date, s_time, e_time, skill_id, skill_by_x, staff_id = None)

############################### skills ################################

############################### TODO: SU Rota  - Create ( Promised skills by Sp and Staff), SP Rota - created and verified ################################
# # # TODO: 
# # # bl_obj.get_potentails_services_by_sp(schema,su_id, sp_id)
# # # bl_obj.get_all_potetial_services(schema, su_id)
############################### Su and Sp Rota - Created and verified  ################################


############################### Staff  ################################
# Excel imports of details, availabily etc
############################### Staff  ################################

# TODO: ^^^^^^^^^
############################### Check providers for each user for single schema ################################
# for schema in schemas:
#     # print(schema)
#     json_service_users = su_obj.get_all_service_users(schema)
#     service_users = json.loads(json_service_users)
#     for su_id, su_name in service_users:
#         print(f"SU:{su_name} - [{su_id}]")
#         # json_contractors = su_obj.get_contractors_for_su_id(schema, su_id)
#         json_available_skills = su_obj.get_skills_available_for_su_id(schema, su_id)
        
#         #TODO: return distinct services 
#         # and also return all sp that provide each distinct service 
#         # and all staff who have that skill for each sp in that list 
        
        
#         # contractors_for_su_id = json.loads(json_contractors)
#         # print(f"Contractors: {contractors_for_su_id} [{su_id}]")
#         available_skills_for_su_id = json.loads(json_available_skills)
#         print(f"Skills: {available_skills_for_su_id} [{su_id}]")
#     #         for provider in contractors[1]:
#     #             print(provider)

#*************************************************** Get up to date schema info. Schema may have been changed to refresh will be required *************************************************** #
# json_schemas = sp_obj.get_all_schemas()
# schemas = json.loads(json_schemas)
# if len(schemas) > 0:
#     schema = schemas[0]
# else:
#     schema = None
#*************************************************** Get up to date schema info. Schema may have been changed to refresh will be required *************************************************** #  
schema = sp_obj.get_schema()


def get_sps(schema):
    json_sps = sp_obj.get_all_sps_for_schema(schema)
    sps = json.loads(json_sps)
    aux_obj_db.print_line_b_line(sps)


def get_sus(schema):
    json_sus = su_obj.get_all_service_users(schema)
    sus = json.loads(json_sus)
    print(f"Service user: {id}")
    aux_obj_db.print_line_b_line(sus)


def get_sps_for_su_id(schema):
    #TODO Search by SU name. May not be unique though (Should DB be changed to prevent?)
    id = input("su_id:") 
    json_sps = su_obj.get_all_sps_for_su_id(schema, id)
    sps = json.loads(json_sps)
    print(f"Service user: {id}")
    aux_obj_db.print_line_b_line(sps)

    

def set_contractors_for_su_id(schema):
    # id = input("su_id:") 
    # sp1 = sp_obj.get_sp1_for_schema(schema)
    schema = sp_obj.get_schema()
    sp_ids = sp_obj.get_all_sp_ids_for_schema(schema)
    su_ids = su_obj.get_all_service_users_ids(schema) 
    print(su_ids)
    print(sp_ids)
    combinations = []
    for su_id in su_ids:
        # num_times = random.randint(1, len(sp_ids))
        num_times = random.randint(1, 5)
        for _ in range(num_times):
            sp_id = random.choice(sp_ids)
            combinations.append((sp_id, su_id))
    print(combinations)
    # Insert each combination into the contractor table
    for sp_id, su_id in combinations:
        su_obj.insert_contractor_details(schema, sp_id, su_id)


def  get_contractors_for_su(schema):
    id = input("su_id:") 
    json_contractors = su_obj.get_contractors_for_su_id(schema, id)
    contractors = json.loads(json_contractors)
    print(f"SU: {id}")
    aux_obj_db.print_line_b_line(contractors)


def build_schema_w_sps_sus_staff(schema = None):
    sp_levels = 4
    sp_min = 2
    sp_max = 2
    num_sps= random.randint(sp_min, sp_max)
    sp1s = create_schemas(1)
    range_limit = sp_levels + 1
    for i in range(2, range_limit):
        create_sp_records(i, sp_max)
    generate_and_insert_su(aux_obj_sys, aux_obj_db, sp_obj, su_obj)
    for j in range(1, range_limit):
        add_staff_for_sp(j)  

def set_services_for_sps_staff(schema):
    schema = sp_obj.get_schema()
    bl_obj.set_potential_services(schema, sp_obj)


def  get_contractors_and_skills_for_su_id(schema):
    schema = sp_obj.get_schema()
    su_id = input("su_id: ")
    skills_avail = sp_obj.get_contractors_and_skills_for_su_id(schema, su_id)
    print(skills_avail)

def function4():
    print("In function 4")

# Mapping between input number and function
function_mapping = {
    '01': build_schema_w_sps_sus_staff,
    '011': set_services_for_sps_staff,
    '012': set_contractors_for_su_id,
    '4': get_contractors_and_skills_for_su_id,
    # '013': get_all_skills_an_sp_provides,
    '1': get_sps,
    '2': get_sus,
    '3': get_sps_for_su_id,
    '5': function4
}

while True:
    choice = input("Enter a number (1-4) to call a function (q to quit): ")
    if choice == 'q':
        break
    
    if choice in function_mapping:
        function = function_mapping[choice]
        schema = sp_obj.get_schema()
        function(schema)
    else:
        print("Invalid choice. Please try again.")
    
  
################################ Providers checked ################################

################################ Delete sp and see if it cascades ################################
# schemas = json.load(sp_obj.get_all_schemas())
# # sp_obj.delete_sp(schemas[0],4)
# print(su_obj.get_contractors_for_su_id(schemas[0], 2))

################################ DOne ################################



    # aux_obj_sys.insert_from_text_file('C:\\Users\\Denis\\Documents\\py_files - Copy\\rota_generator\\my_logs\\postcodes.txt')
    
    # TODO: sort proximity table. will be used by users and providers
    # all_pcs = geo_obj.get_all_postcodes("public")
    # with open('C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\google_api.txt', 'r') as file:
        # key = file.read().strip()
    # stubbb = geo_obj.googlemaps_validate_postcode("NN4 9AA", key)
    # print(stubbb)
    # with open('C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\google_api.txt', 'r') as file:
    #     key = file.read().strip()
    # valid_postcodes_file = 'C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_logs\\valid_postcodes.txt'
    # invalid_postcodes_file = 'C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_logs\\invalid_postcodes.txt'
    # valid_list = aux_obj_db.read_file(valid_postcodes_file) # VALID LIST ALREADY CONFIRMED
    # invalid_list = aux_obj_db.read_file(invalid_postcodes_file)
    # checked_list = [*valid_list, *invalid_list]
    # for pc in all_pcs:
    #     postcode_id, postcode = pc
    #     to_remove = postcode not in valid_list
    #     if to_remove:
    #         aux_obj_db.my_logs('my_logs', 'Invalid_Postcodes.txt', postcode)
    #         geo_obj.delete_postcode("public", postcode_id)
            # if(geo_obj.googlemaps_validate_postcode(postcode, key)):
            #     print(f"Postcode ID: {postcode_id}, Postcode: {postcode} [VALID]")
            #     aux_obj_db.my_logs('my_logs', 'Valid_Postcodes.txt', postcode)
            # else:
            # print(f"Postcode ID: {postcode_id}, Postcode: {postcode} [INVALID]")
    # print(f'{geo_obj.get_coordinates(cv)} - {geo_obj.get_coordinates(m)}' )
    # coor1 = geo_obj.get_coordinates(cv)
    # coor2 = geo_obj.get_coordinates(m)
    # distance = round(geo_obj.distance(coor1, coor2), 2)
    # print(f'distance from {cv} to {m} is {distance} ')
    # # print('TODO: [Proximity Table & Matrix]')
    # schemas = sp_obj.get_all_schemas()
    # schema_name = schemas[0]
  
    # offspring_ids = get_providers(sp_obj, schema_name)
    # while True:
    #     selected_provider_id = int(input("Enter the Provider ID to delete: "))
    #     sp_obj.delete_sp(schema_name, selected_provider_id) # delete parent first
    #     for offspring_id in offspring_ids:
    #         sp_obj.delete_sp(schema_name, offspring_id)
    
   
           

    
    # offspring = sp_obj.get_children_and_grandchildren(schema_name, 3)
    # for child in offspring:
    #     sp_id = child[0]
    #     child_provider_name = child[1]
    #     p_id = child[2]
    #     sp_name = sp_obj.func_get_provider_from_sp_id(child_provider_name, 3)
    #     print(f'{sp_name} : {offspring}')
    # # sp_obj.func_delete_service_provider(name, 2)
    # #TOSO: delete children before deleting parent..or leave orphans in table and remove all orphans seperately

