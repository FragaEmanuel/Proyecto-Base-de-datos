import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import time

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'obligatorio')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.port = os.getenv('DB_PORT', '3306')
        
        # Primero esperar a que la BD esté disponible
        self.wait_for_db()
        
        # Luego inicializar la base de datos
        self.initialize_database()
    
    def wait_for_db(self, max_retries=30, delay=2):
        """Esperar a que la base de datos esté disponible"""
        print("⏳ Esperando a que la base de datos esté disponible...")
        for i in range(max_retries):
            try:
                # Intentar conexión sin especificar base de datos primero
                connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                if connection and connection.is_connected():
                    print("✅ Conectado a MySQL")
                    connection.close()
                    return True
            except Error as e:
                print(f"⏳ Intento {i+1}/{max_retries} - Base de datos no disponible aún: {e}")
                time.sleep(delay)
        
        print("❌ No se pudo conectar a la base de datos después de todos los intentos")
        return False
    
    def initialize_database(self):
        """Crear la base de datos y tablas si no existen"""
        try:
            # Conectar sin especificar base de datos para crear la BD
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            cursor = connection.cursor()
            
            # Verificar si la base de datos existe, si no crearla
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✅ Base de datos '{self.database}' verificada/creada")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Ahora conectar a la base de datos específica para crear tablas
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            cursor = connection.cursor()
            
            # Leer y ejecutar schema.sql
            if os.path.exists('database/init/schema.sql'):
                with open('database/init/schema.sql', 'r', encoding='utf-8') as file:
                    schema_sql = file.read()
                    
                # Ejecutar cada sentencia por separado
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Error as e:
                            print(f"⚠️  Error ejecutando statement: {e}")
                            continue
                
                connection.commit()
                print("✅ Tablas creadas exitosamente")
                
                # Cargar datos de prueba
                self.seed_database()
            else:
                print("❌ Archivo database/init/schema.sql no encontrado")
            
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
            if not connection:
                print("❌ No se pudo conectar para cargar datos de prueba")
                return
                
            cursor = connection.cursor()
            
            # Verificar si ya existen datos para no duplicar
            cursor.execute("SELECT COUNT(*) FROM participante")
            count = cursor.fetchone()[0]
            
            if count == 0 and os.path.exists('database/init/seed_data.sql'):
                print("📥 Cargando datos de prueba...")
                # Leer y ejecutar seed_data.sql
                with open('database/init/seed_data.sql', 'r', encoding='utf-8') as file:
                    seed_sql = file.read()
                    
                for statement in seed_sql.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Error as e:
                            print(f"⚠️  Error ejecutando datos de prueba: {e}")
                            continue
                
                connection.commit()
                print("✅ Datos de prueba cargados exitosamente")
            else:
                print("ℹ️  Datos ya existen o archivo seed_data.sql no encontrado")
            
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
                password=self.password,
                port=self.port
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
        return None
    
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
        return None