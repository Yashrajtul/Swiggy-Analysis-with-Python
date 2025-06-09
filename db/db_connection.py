import atexit
import mysql.connector
from mysql.connector import Error

# Database connection class
# This class handles the connection to the MySQL database and provides methods to connect and disconnect.
# It also includes error handling for connection issues.
class SwiggyDBConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self._connect()
        atexit.register(self.disconnect)  # Ensure disconnection on exit

    # def __del__(self):
    #     self.disconnect()
        
    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error connecting to database: {e}")
            # throw exception for the ui    
            raise Exception(f"Error connecting to database: {e}")
            # return None

    def disconnect(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("Disconnected from MySQL database")
    
    # Method to create the database and tables
    def create_tables(self):
        self.create_restaurants_table()
        self.create_city_table()
        self.create_swiggy_source_table()
        self.create_ratings_table()
        self.create_cuisines_table()
        self.create_delivery_table()
        self.create_locality_table()
        self.create_booking_table()
        self.create_fact_swiggy_table()
        
    def create_restaurants_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS restaurants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Restaurants table created successfully")
        except Error as e:
            print(f"Error creating restaurants table: {e}")
            raise Exception(f"Error creating restaurants table: {e}")
    
    def create_city_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS city (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Cities table created successfully")
        except Error as e:
            print(f"Error creating cities table: {e}")
            raise Exception(f"Error creating cities table: {e}")
            
    def create_swiggy_source_table(self):
        try:
            query = """
            CREATE TABLE swiggy_source (
                restaurant_name VARCHAR(255),
                city VARCHAR(100),
                locality VARCHAR(150),
                cuisines VARCHAR(100),
                average_cost_for_two INT,
                has_table_booking VARCHAR(3),
                has_online_delivery VARCHAR(3),
                rating_stars_out_of_5 DOUBLE,
                rating_in_text VARCHAR(20),
                price_range INT,
                votes INT
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Swiggy_source table created successfully")
        except Error as e:
            print(f"Error creating swiggy source table: {e}")
            raise Exception(f"Error creating swiggy source table: {e}")
        
    def create_ratings_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS ratings (
                id INT PRIMARY KEY AUTO_INCREMENT, 
                star DOUBLE NOT NULL, 
                text VARCHAR(20) NOT NULL
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Ratings table created successfully")
        except Error as e:
            print(f"Error creating ratings table: {e}")
            raise Exception(f"Error creating ratings table: {e}")

    def create_cuisines_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS cuisines (
                id INT PRIMARY KEY AUTO_INCREMENT, 
                name VARCHAR(100) NOT NULL
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Cuisines table created successfully")
        except Error as e:
            print(f"Error creating cuisines table: {e}")
            raise Exception(f"Error creating cuisines table: {e}")

    def create_delivery_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS delivery (
                id INT PRIMARY KEY AUTO_INCREMENT, 
                availability VARCHAR(3) NOT NULL
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Delivery table created successfully")
        except Error as e:
            print(f"Error creating delivery table: {e}")
            raise Exception(f"Error creating delivery table: {e}")

    def create_locality_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS locality (
                id INT PRIMARY KEY AUTO_INCREMENT, 
                name VARCHAR(150) NOT NULL
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Locality table created successfully")
        except Error as e:
            print(f"Error creating locality table: {e}")
            raise Exception(f"Error creating locality table: {e}")

    def create_booking_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS booking (
                id INT PRIMARY KEY AUTO_INCREMENT, 
                availability VARCHAR(3) NOT NULL
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Booking table created successfully")
        except Error as e:
            print(f"Error creating booking table: {e}")
            raise Exception(f"Error creating booking table: {e}")

    def create_fact_swiggy_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS fact_swiggy (
                fact_id INT PRIMARY KEY AUTO_INCREMENT, 
                city_id INT NOT NULL, 
                locality_id INT NOT NULL,
                rest_id INT NOT NULL,
                cuisine_id INT NOT NULL, 
                rating_id INT NOT NULL,
                delivery_id INT NOT NULL, 
                booking_id INT NOT NULL,
                avg_cost_for_two INT NOT NULL,
                votes INT NOT NULL,
                price_range INT NOT NULL,
                FOREIGN KEY (city_id) REFERENCES city(id),
                FOREIGN KEY (locality_id) REFERENCES locality(id),
                FOREIGN KEY (rest_id) REFERENCES restaurants(id),
                FOREIGN KEY (cuisine_id) REFERENCES cuisines(id),
                FOREIGN KEY (rating_id) REFERENCES ratings(id),
                FOREIGN KEY (delivery_id) REFERENCES delivery(id),
                FOREIGN KEY (booking_id) REFERENCES booking(id)
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Fact_swiggy table created successfully")
        except Error as e:
            print(f"Error creating fact_swiggy table: {e}")
            raise Exception(f"Error creating fact_swiggy table: {e}")
    
    # Initialize the tables
    def load_from_csv(self, csv_file_path):
        import pandas as pd
        try:
            data = pd.read_csv(csv_file_path, encoding='latin1')  # or try 'ISO-8859-1'
            for index, row in data.iterrows():
                query = """
                INSERT INTO swiggy_source (restaurant_name, city, locality, cuisines, average_cost_for_two,
                                            has_table_booking, has_online_delivery, rating_stars_out_of_5,
                                            rating_in_text, price_range, votes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, tuple(row))
            self.connection.commit()
            print("Data loaded successfully from CSV")
        except Error as e:
            print(f"Error loading data from CSV: {e}")
            raise Exception(f"Error loading data from CSV: {e}")
        
    def initialize_database(self):
        self.create_tables()
        
        # Load data from CSV file
        csv_file_path = "./data/Swiggy_Analysis_Source_File.csv"
        self.load_from_csv(csv_file_path)
        
        # initialize other tables from the swiggy_source table
        self.initialize_other_tables()
    
    def reinitialize_database(self):
        # Drop all tables
        self.drop_tables()
        
        # Recreate tables
        self.initialize_database()
    
    def initialize_other_tables(self):
        # initialize other tables from the swiggy_source table without using loop
        try:
            # Insert unique cities
            query = "INSERT IGNORE INTO city (name) SELECT DISTINCT city FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique localities
            query = "INSERT IGNORE INTO locality (name) SELECT DISTINCT locality FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique cuisines
            query = "INSERT IGNORE INTO cuisines (name) SELECT DISTINCT cuisines FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique ratings
            query = "INSERT IGNORE INTO ratings (star, text) SELECT DISTINCT rating_stars_out_of_5, rating_in_text FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique delivery options
            query = "INSERT IGNORE INTO delivery (availability) SELECT DISTINCT has_online_delivery FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique booking options
            query = "INSERT IGNORE INTO booking (availability) SELECT DISTINCT has_table_booking FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert unique restaurants
            query = "INSERT IGNORE INTO restaurants (name) SELECT DISTINCT restaurant_name FROM swiggy_source"
            self.cursor.execute(query)
            self.connection.commit()
            
            # Insert into fact_swiggy table
            query = """
            INSERT INTO fact_swiggy (city_id, locality_id, rest_id, cuisine_id, rating_id, delivery_id, booking_id, avg_cost_for_two, votes, price_range)
            SELECT 
                c.id, l.id, r.id, cu.id, ra.id, d.id, b.id, s.average_cost_for_two, s.votes, s.price_range
            FROM swiggy_source s
            JOIN city c ON s.city = c.name
            JOIN locality l ON s.locality = l.name
            JOIN restaurants r ON s.restaurant_name = r.name
            JOIN cuisines cu ON s.cuisines = cu.name
            JOIN ratings ra ON s.rating_stars_out_of_5 = ra.star AND s.rating_in_text = ra.text
            JOIN delivery d ON s.has_online_delivery = d.availability
            JOIN booking b ON s.has_table_booking = b.availability
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Other tables initialized successfully")
            
        except Error as e:
            print(f"Error initializing other tables: {e}")     
            raise Exception(f"Error initializing other tables: {e}")       
        
    # Drop all tables in the database
    def drop_tables(self):
        try:
            tables = [
                "fact_swiggy", "booking", "delivery", "locality", "cuisines",
                "ratings", "swiggy_source", "restaurants", "city"
            ]
            for table in tables:
                query = f"DROP TABLE IF EXISTS {table}"
                self.cursor.execute(query)
            self.connection.commit()
            print("All tables dropped successfully")
        except Error as e:
            print(f"Error dropping tables: {e}")
            raise Exception(f"Error dropping tables: {e}")
        
    # Insert data
    def insert_into_restaurants_table(self, name):
        query = "INSERT INTO restaurants (name) VALUES (%s)"
        try:
            self.cursor.execute(query, (name,))
            self.connection.commit()
            print("Data inserted into restaurants table successfully")
        except Error as e:
            print(f"Error inserting data into restaurants table: {e}")
            raise Exception(f"Error inserting data into restaurants table: {e}")
    
    def insert_into_city_table(self, name):
        query = "INSERT INTO city (name) VALUES (%s)"
        try:
            self.cursor.execute(query, (name,))
            self.connection.commit()
            print("Data inserted into city table successfully")
        except Error as e:
            print(f"Error inserting data into city table: {e}")
            raise Exception(f"Error inserting data into city table: {e}")
    
    def insert_into_ratings_table(self, star, text):
        query = "INSERT INTO ratings (star, text) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (star, text))
            self.connection.commit()
            print("Data inserted into ratings table successfully")
        except Error as e:
            print(f"Error inserting data into ratings table: {e}")
            raise Exception(f"Error inserting data into ratings table: {e}")
            
    def insert_into_cuisines_table(self, name):
        query = "INSERT INTO cuisines (name) VALUES (%s)"
        try:
            self.cursor.execute(query, (name,))
            self.connection.commit()
            print("Data inserted into cuisines table successfully")
        except Error as e:
            print(f"Error inserting data into cuisines table: {e}")
            raise Exception(f"Error inserting data into cuisines table: {e}")
            
    def insert_into_locality_table(self, name):
        query = "INSERT INTO locality (name) VALUES (%s)"
        try:
            self.cursor.execute(query, (name,))
            self.connection.commit()
            print("Data inserted into locality table successfully")
        except Error as e:
            print(f"Error inserting data into locality table: {e}")
            raise Exception(f"Error inserting data into locality table: {e}")
            
    def insert_into_fact_swiggy_table(self, avg_cost_for_two, votes, price_range, city_id=None, locality_id=None, rest_id=None, cuisine_id=None, rating_id=None, delivery_id=None, booking_id=None, city=None, locality=None, restaurant_name=None, cuisines=None, rating_stars_out_of_5=None, rating_in_text=None, has_online_delivery=None, has_table_booking=None):
        # if values of city, locality, restaurant_name, cuisines, rating_stars_out_of_5, rating_in_text, has_online_delivery, has_table_booking are provided, then fetch the corresponding ids from the respective tables
        # if all values are not present, then fetch the ids from the respective tables
        try:
            if city_id is None and city:
                query = "SELECT id FROM city WHERE name = %s"
                self.cursor.execute(query, (city,))
                city_id = self.cursor.fetchone()[0]
            if locality_id is None and locality:
                query = "SELECT id FROM locality WHERE name = %s"
                self.cursor.execute(query, (locality,))
                locality_id = self.cursor.fetchone()[0]
            if rest_id is None and restaurant_name:
                query = "SELECT id FROM restaurants WHERE name = %s"
                self.cursor.execute(query, (restaurant_name,))
                rest_id = self.cursor.fetchone()[0]
            if cuisine_id is None and cuisines:
                query = "SELECT id FROM cuisines WHERE name = %s"
                self.cursor.execute(query, (cuisines,))
                cuisine_id = self.cursor.fetchone()[0]
            if rating_id is None and rating_stars_out_of_5 and rating_in_text:
                query = "SELECT id FROM ratings WHERE star = %s AND text = %s"
                self.cursor.execute(query, (rating_stars_out_of_5, rating_in_text))
                rating_id = self.cursor.fetchone()[0]
            if delivery_id is None and has_online_delivery:
                query = "SELECT id FROM delivery WHERE availability = %s"
                self.cursor.execute(query, (has_online_delivery,))
                delivery_id = self.cursor.fetchone()[0]
            if booking_id is None and has_table_booking:
                query = "SELECT id FROM booking WHERE availability = %s"
                self.cursor.execute(query, (has_table_booking,))
                booking_id = self.cursor.fetchone()[0]
            if city_id is None or locality_id is None or rest_id is None or cuisine_id is None or rating_id is None or delivery_id is None or booking_id is None:
                print("Error: One or more required IDs are missing. Please provide valid values.")
                return
            
            query = """
            INSERT INTO fact_swiggy (city_id, locality_id, rest_id, cuisine_id, rating_id, delivery_id, booking_id, avg_cost_for_two, votes, price_range)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (city_id, locality_id, rest_id, cuisine_id, rating_id, delivery_id, booking_id, avg_cost_for_two, votes, price_range))
            self.connection.commit()
            print("Data inserted into fact_swiggy table successfully")
        except Error as e:
            print(f"Error inserting data into fact_swiggy table: {e}")
            raise Exception(f"Error inserting data into fact_swiggy table: {e}")
    
    # Select query methods
    def fetch_table_names(self):
        query = "SHOW TABLES"
        try:
            self.cursor.execute(query)
            tables = self.cursor.fetchall()
            return [table[0] for table in tables]
        except Error as e:
            print(f"Error fetching table names: {e}")
            raise Exception(f"Error fetching table names: {e}")
            return None
        
    def fetch_table_columns(self, table_name): 
        query = f"SHOW COLUMNS FROM {table_name}"
        try:
            self.cursor.execute(query)
            columns = self.cursor.fetchall()
            return [column[0] for column in columns]
        except Error as e:
            print(f"Error fetching columns for table {table_name}: {e}")
            raise Exception(f"Error fetching columns for table {table_name}: {e}")
            return None
        
    def fetch_table_description(self, table_name):
        query = f"DESCRIBE {table_name}"
        try:
            self.cursor.execute(query)
            description = self.cursor.fetchall()
            return description
        except Error as e:
            print(f"Error describing table {table_name}: {e}")
            raise Exception(f"Error describing table {table_name}: {e}")
            return None
    
    def fetch_table_data(self, table_name, columns=None, where_clause=None, group_by=None, having=None, order_by=None, limit=None, offset=None):
        query = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if group_by:
            query += f" GROUP BY {group_by}"
        
        if having:
            query += f" HAVING {having}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if offset:
            query += f" OFFSET {offset}"
        
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Error as e:
            print(f"Error executing select query: {e}")
            raise Exception(f"Error executing select query: {e}")
            return None
        
    def fetch_query_result(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            raise Exception(f"Error executing query: {e}")
            return None
        
    def print_output(self, query=None, table_name=None, columns=None, where_clause=None, group_by=None, having=None, order_by=None, limit=None, offset=None):
        if query:
            result = self.fetch_query_result(query)
        elif table_name:
            result = self.fetch_table_data(table_name, columns, where_clause, group_by, having, order_by, limit, offset)
        else:
            print("No query or table name provided")
            return
        
        if result:
            # for row in result:
            #     print(row)
            print(result)
        else:
            print("No data found or error executing query")
            
    
    def print_results(self, results):
        if results:
            for row in results:
                print(row)
        else:
            print("No data found or error executing query")
        

    


    


