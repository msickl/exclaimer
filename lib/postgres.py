import psycopg2
from psycopg2.extras import RealDictCursor
from lib import config

class init:
    def __init__(self):
        dbconfig = config.get('postgres')
        try:
            self.connection = psycopg2.connect(
                host=dbconfig['host'],
                database=dbconfig['dbname'],
                user=dbconfig['user'],
                password=dbconfig['pass'],
                port=dbconfig['port']
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor) 
            print("Connected to PostgreSQL database successfully.")
        
        except (Exception, psycopg2.Error) as error:
            print("Error connecting to PostgreSQL:", error)
            self.connection = None

    def select(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchall() 
            return result

        except (Exception, psycopg2.Error) as error:
            print(f"Error executing SELECT query: {error}")
            return None

    def insert(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()  
            return self.cursor.rowcount  
        
        except (Exception, psycopg2.Error) as error:
            print(f"Error executing INSERT query: {error}")
            self.connection.rollback()  
            return None

    def update(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()  
            return self.cursor.rowcount  

        except (Exception, psycopg2.Error) as error:
            print(f"Error executing UPDATE query: {error}")
            self.connection.rollback() 
            return None

    def delete(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()  
            return self.cursor.rowcount 
        
        except (Exception, psycopg2.Error) as error:
            print(f"Error executing DELETE query: {error}")
            self.connection.rollback() 
            return None

    def close(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")



    

    # SELECT example
    #select_query = "SELECT * FROM your_table_name WHERE id = %s"
    #rows = db.select(select_query, (1,))
    #print("Select Query Result:", rows)

    # INSERT example
    #insert_query = "INSERT INTO your_table_name (column1, column2) VALUES (%s, %s)"
    #rows_affected = db.insert(insert_query, ("value1", "value2"))
    #print(f"{rows_affected} row(s) inserted.")

    # UPDATE example
    #update_query = "UPDATE your_table_name SET column1 = %s WHERE id = %s"
    #rows_affected = db.update(update_query, ("new_value", 1))
    #print(f"{rows_affected} row(s) updated.")

    # DELETE example
    #delete_query = "DELETE FROM your_table_name WHERE id = %s"
    #rows_affected = db.delete(delete_query, (1,))
    #print(f"{rows_affected} row(s) deleted.")

    # Close the connection when done
    #db.close()
