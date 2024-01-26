import psycopg2

# class DBClass:
    # def __init__(self, host="localhost", port="5432", dbname="dsasea", user="postgres", password="password"):
    #     self.host = host
    #     self.port = port
    #     self.dbname = dbname
    #     self.user = user
    #     self.password = password
    
    # def connect(self):
    #     conn = psycopg2.connect(
    #         host=self.host,
    #         port=self.port,
    #         dbname=self.dbname,
    #         user=self.user,
    #         password=self.password
    #     )
    #     return conn
class DBClass:
    def __init__(self, config_file='C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_ini.txt'):
        with open(config_file, 'r') as f:
            config = {}
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('=')
                if len(parts) != 2:
                    continue
                key, value = parts
                config[key.strip()] = value.strip()
        
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', '5432')
        self.dbname = config.get('dbname', 'dsasea')
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', 'password')
    
    def connect(self):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        return conn

    def query(self, query_string):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query_string)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results


class ClassAnother:
    def __init__(self, db_class):
        self.db_class = db_class
        
    def query(self, query_string):
        conn = self.db_class.connect()
        cursor = conn.cursor()
        cursor.execute(query_string)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results




# # # # cstring = f'host="localhost", port="5432", dbname="dsasea", user="postgres", password="password"'
# # # ini_path = f'C:\\Users\\Denis\\Documents\\py_files - Copy\\my_service_project\\my_classes\\db_sys.txt'
# # # db_class = DBClass(ini_path)
# # # class_another = ClassAnother(db_class=db_class)

# # # results = class_another.query("SELECT * FROM index_table")
# # # print(results)

# # Example usage
# # get the current directory of the script
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# # get the path of the database.ini file
# ini_file = os.path.join(parent_dir, 'database_connection', 'database.ini')

# db = Db(ini_file)  # Instantiate the Db class with the ini file as a parameter
# another_class = AnotherClass(db)  # Instantiate AnotherClass with the Db instance
# another_class.method_with_db_connection()  # Call the method that needs the database connection

