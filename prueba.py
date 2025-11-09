import mysql.connector
from mysql.connector import Error


class SistemaConsultas:
    def __init__(self):
        self.conexion = None
        self.conectar()

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(
                user='root',
                password='rootpassword',
                host='localhost',
                database='practico2'
            )
            print("Conexión exitosa")
        except Error as e:
            print(f"Error al conectar: {e}")
            return False
        return True

    def ejecutar_consulta(self, query, params=None):
        try:
            cursor = self.conexion.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Obtener resultados
            resultados = cursor.fetchall()

            # Obtener nombres de columnas
            columnas = [desc[0] for desc in cursor.description]

            cursor.close()
            return resultados, columnas

        except Error as e:
            print(f"Error en la consulta: {e}")
            return None, None

    def mostrar_resultados(self, resultados, columnas):
        if not resultados:
            print("No se encontraron resultados")
            return

        # Mostrar nombres de columnas
        print("\n" + " | ".join(columnas))
        print("-" * (len(" | ".join(columnas)) + 10))

        # Mostrar datos
        for fila in resultados:
            print(" | ".join(str(valor) for valor in fila))

        print(f"\nTotal de registros: {len(resultados)}")

    def consulta_1(self):
        """Salas más reservadas"""
        query = """
            SELECT r.nombre_sala, r.edificio, COUNT(*) as total_reservas
            FROM reserva r
            GROUP BY r.nombre_sala, r.edificio
            ORDER BY total_reservas DESC;
        """
        print("\nSalas más reservadas:")
        resultados, columnas = self.ejecutar_consulta(query)
        self.mostrar_resultados(resultados, columnas)

    def consulta_2(self):
        """Turnos más demandados"""
        query = """
            SELECT t.id_turno, t.hora_inicio, t.hora_fin, COUNT(*) as total_reservas
            FROM reserva r
            JOIN turno t ON r.id_turno = t.id_turno
            GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
            ORDER BY total_reservas DESC;
        """
        print("\nTurnos más demandados:")
        resultados, columnas = self.ejecutar_consulta(query)
        self.mostrar_resultados(resultados, columnas)

    def consulta_3(self):
        """Promedio de participantes por sala"""

        query = """
            SELECT
                r.nombre_sala,
                r.edificio,
                COUNT(rp.ci_participante) / COUNT(DISTINCT r.id_reserva) as promedio_participantes
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            GROUP BY r.nombre_sala, r.edificio
            ORDER BY promedio_participantes DESC;
        """
        print("\nPromedio de participantes por sala:")
        resultados, columnas = self.ejecutar_consulta(query)
        self.mostrar_resultados(resultados, columnas)

    def menu_principal(self):
        while True:
            print("\n" + "=" * 50)
            print("PROYECTO BDD - MENU PRINCIPAL")
            print("=" * 50)
            print("1. Gestion de registros")
            print("2. Consultas")
            print("3. Salir")

            opcion = input("Selecciona una opción (1-3): ").strip()

            if opcion == '1':
                self.consulta_1()
            elif opcion == '2':
                self.menu_consultas()
            elif opcion == '3':
                break
            else:
                print("Opción no válida. Intenta de nuevo.")

            input("\nPresiona Enter para continuar...")

    def cerrar_conexion(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("Conexión terminada")
            
    def menu_abm(self):
        while True:
            print("\n" + "=" * 50)
            print("PROYECTO BDD - SISTEMA ABM")
            print("=" * 50)
            print("1. Añadir entrada")
            print("2. Modicar entrada")
            print("3. Borrar entrada")
            print("4. Salir")
            
            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == '1':
                self.añadir_entrada()
            elif opcion == '2':
                self.modificar_entrada()
            elif opcion == '3':
                self.borrar_entrada()
            elif opcion == '4':
                break
            else:
                print("Opción no válida. Intenta de nuevo.")

            input("\nPresiona Enter para continuar...")
            
    def menu_consultas(self):
        while True:
            print("\n" + "=" * 50)
            print("PROYECTO BDD - SISTEMA DE CONSULTAS")
            print("=" * 50)
            print("1. Usuario con más pedidos")
            print("2. Producto más vendido")
            print("3. Costo total de un pedido")
            print("4. Salir")

            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == '1':
                self.consulta_1()
            elif opcion == '2':
                self.consulta_2()
            elif opcion == '3':
                self.consulta_3()
            elif opcion == '4':
                break
            else:
                print("Opción no válida. Intenta de nuevo.")

            input("\nPresiona Enter para continuar...")


# Ejecutar el programa
if __name__ == "__main__":
    sistema = SistemaConsultas()

    if sistema.conexion and sistema.conexion.is_connected():
        try:
            sistema.menu_principal()
        finally:
            sistema.cerrar_conexion()