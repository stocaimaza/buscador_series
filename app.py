## Este es nuestro archivo principal.
## Buscador de series con Flask y una API externa.

## Importamos Flask:
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
## Requests nos permite hacer las peticiones a las APIS.
import database
## Nuestro propio modulo que gestiona nuestras bases de datos.

import re
## Expresiones regulares, lo usamos para limpiar el html del resumen de la serie.
import html
## Convierte entidades HTML (&amp; &quot; etc.) en sus caracteres reales.


app = Flask(__name__)
## Clave secreta: Flask la necesita para poder usar flash() (mensajes entre páginas).
app.secret_key = "cambiar-esta-clave-en-produccion"

## Esto se ejecuta una sola vez, apenas arranca el programa (no en cada visita a una ruta).

database.crear_tabla()
## La primera vez crea la tabla, en las siguientes no hace nada.

URL_TVMAZE = "https://api.tvmaze.com/singlesearch/shows"
## Segundos máximos que esperamos a la API antes de darnos por vencidos.
TIEMPO_ESPERA = 10
## Largo máximo que aceptamos para el nombre a buscar.
LARGO_MAXIMO_NOMBRE = 100

## Cuando usamos esta api TVMaze devuelve la descripción con etiquetas HTML (<p> <b> <etc>)


def quitar_html(texto):
    ## Si la serie no tiene descripción me envia un None en lugar de un string.
    if texto is None:
        return "Sin descripción disponible. "
    ## Usaremos una herramienta que elimina patrones en el texto:
    ## re.sub(patron, reemplazo, texto): busca un patron y lo reemplaza
    return html.unescape(re.sub(r"<[^>]+>", "", texto)).strip()


## Creamos la página de inicio: muestra el buscador.
@app.route("/")
def inicio():
    return render_template("index.html")

## Creamos la ruta para buscar la serie:

@app.route("/buscar")
def buscar():
    nombre = request.args.get("nombre", "").strip()
    if nombre == "":
        flash("Escribí el nombre de una serie para buscar.", "error")
        return redirect (url_for("inicio"))
    if len(nombre) > LARGO_MAXIMO_NOMBRE:
        flash(f"El nombre no puede superar los {LARGO_MAXIMO_NOMBRE} caracteres.", "error")
        return redirect (url_for("inicio"))
    return redirect (url_for("serie", nombre=nombre))


## Creamos una rutita dinamica:
@app.route("/serie/<nombre>")
def serie(nombre):
    ## Si la API no responde o no hay internet, requests lanza una excepción: la atrapamos.
    try:
        respuesta = requests.get(URL_TVMAZE, params={"q": nombre}, timeout=TIEMPO_ESPERA)
    except requests.RequestException:
        return render_template("series.html", encontrada = False, nombre=nombre,
                               error="No pudimos conectarnos con TVMaze. Probá de nuevo en unos minutos.")
    if respuesta.status_code != 200:
        return render_template("series.html", encontrada = False, nombre=nombre)
    datos = respuesta.json()
    info = {
        "nombre": datos.get("name", nombre),
        "imagen":datos["image"]["medium"] if datos.get("image") else None,
        "generos": datos.get("genres") or [],
        "rating": datos["rating"]["average"] if datos.get("rating") else None,
        "estado": datos.get("status") or "Desconocido",
        "resumen": quitar_html(datos.get("summary")),
    }
    ## Avisamos a la plantilla si ya la tenemos guardada, para no ofrecer agregarla de nuevo.
    ya_favorito = database.existe_favorito(info["nombre"])
    return render_template("series.html", encontrada = True, serie = info, ya_favorito = ya_favorito)


## Agregamos a favoritos:
@app.route("/favoritos/agregar", methods=["POST"])
def agregar_favorito():
    ## Usamos .get() en lugar de [] para que no explote si falta algún campo.
    nombre = request.form.get("nombre", "").strip()
    genero = request.form.get("genero", "").strip() or "Sin género"
    rating = request.form.get("rating", "").strip() or "Sin rating"
    imagen = request.form.get("imagen", "").strip()

    ## El nombre es obligatorio: sin él no tiene sentido guardar nada.
    if nombre == "":
        flash("No se pudo agregar: falta el nombre de la serie.", "error")
        return redirect(url_for("inicio"))

    ## Evitamos guardar la misma serie dos veces.
    if database.existe_favorito(nombre):
        flash(f"«{nombre}» ya está en tu lista de favoritos.", "info")
        return redirect(url_for("favoritos"))

    database.agregar_favorito(nombre, genero, rating, imagen)
    flash(f"«{nombre}» se agregó a tus favoritos.", "exito")
    return redirect(url_for("favoritos"))


## Creamos la función para mostrar los favoritos:
@app.route("/favoritos")
def favoritos():
    lista = database.obtener_favoritos()
    return render_template("favoritos.html", favoritos=lista)


## Eliminamos un favorito:
@app.route("/favoritos/eliminar/<int:id_favorito>", methods=["POST"])
def eliminar_favorito(id_favorito):
    if database.eliminar_favorito(id_favorito):
        flash("Favorito eliminado.", "exito")
    else:
        flash("Ese favorito no existe o ya fue eliminado.", "error")
    return redirect(url_for("favoritos"))


## Solo arrancamos el servidor si ejecutamos este archivo directamente (python app.py).
if __name__ == "__main__":
    app.run(debug=True)
