import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'obligatorio')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        
        # Crear base de datos y tablas si no existen
        self.initialize_database()
    
    def initialize_database(self):
        """Crear la base de datos y tablas si no existen"""
        try:
            # Primero conectar sin especificar base de datos
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            
            cursor = connection.cursor()
            
            # Leer y ejecutar schema.sql
            with open('database/schema.sql', 'r', encoding='utf-8') as file:
                schema_sql = file.read()
                
            # Ejecutar cada sentencia por separado
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            connection.commit()
            print("✅ Base de datos y tablas creadas exitosamente")
            
            # Cargar datos de prueba
            self.seed_database()
            
        except Error as e:
            print(f"❌ Error inicializando base de datos: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    
    def seed_database(self):
        """Cargar datos de prueba"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Leer y ejecutar seed_data.sql
            with open('database/seed_data.sql', 'r', encoding='utf-8') as file:
                seed_sql = file.read()
                
            for statement in seed_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            connection.commit()
            print("✅ Datos de prueba cargados exitosamente")
            
        except Error as e:
            print(f"⚠️  Error cargando datos de prueba: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                connection.commit()
                return result
            except Error as e:
                print(f"❌ Error ejecutando query: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
    
    def execute_insert(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                connection.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"❌ Error ejecutando insert: {e}")
                return None
            finally:
                cursor.close()
                connection.close()