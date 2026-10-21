## Generamos nuestra conexión con nuestra base de datos portable. 

import sqlite3
## Importamos las herramientas para el proyectin. 

## Nos guardamos en una variable global el nombre del archivo: 
NOMBRE_DB = "series.db"

## Función para conectarnos: 
def conectar(): 
    return sqlite3.connect(NOMBRE_DB)

## Tenemos que crear la base de datos. 
## Creamos la primer tabla: 

def crear_tabla(): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nombre TEXT NOT NULL, 
            genero TEXT NOT NULL, 
            rating TEXT NOT NULL, 
            imagen TEXT NOT NULL
        )
        """
    )
    conexion.commit()
    conexion.close()


## Creamos la función para guardar en favoritos: 
def agregar_favorito(nombre, genero, rating, imagen): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO favoritos (nombre, genero, rating, imagen) VALUES (?, ?, ?, ?)", (nombre, genero, rating, imagen),
    )
    conexion.commit()
    conexion.close()


## Creamos la función para obtener el listado completo de favoritos guardados. 

def obtener_favoritos(): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, genero, rating, imagen FROM favoritos ORDER BY id DESC"
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas

## Creamos una función que elimina un favorito: 

def eliminar_favorito(id_favorito): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM favoritos WHERE id = ?", (id_favorito,)
    )
    ## Ojo: el segundo parámetro tiene que ser una tupla, por eso la coma en (id_favorito,)
    eliminados = cursor.rowcount
    conexion.commit()
    conexion.close()
    ## Devolvemos True si realmente se borró una fila.
    return eliminados > 0


## Creamos una función que revisa si una serie ya está guardada (para no duplicarla): 

def existe_favorito(nombre): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT 1 FROM favoritos WHERE LOWER(nombre) = LOWER(?)", (nombre,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila is not None

