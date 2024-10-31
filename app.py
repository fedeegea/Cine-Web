from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta

# Variables globales
peliculas_adultos = ["Venom El Ultimo Baile", "Terrifier 3 El Payaso Siniestro", "Sonrie 2"]
peliculas_todo_publico = ["Robot Salvaje", "La Leyenda Del Dragon"]
asientos_ocupados = 30                      
PRECIO_ENTRADA = 8000

# Inicializar asientos
def inicializar_asientos(filas, columnas):
    return [["O" for _ in range(columnas)] for _ in range(filas)]

def ocupar_asientos_aleatoriamente(matriz, num_asientos_ocupados):
    filas = len(matriz)
    columnas = len(matriz[0])
    asientos_disponibles = [(fila, col) for fila in range(filas) for col in range(columnas)]
    asientos_ocupados = random.sample(asientos_disponibles, num_asientos_ocupados)
    for fila, col in asientos_ocupados:
        matriz[fila][col] = "X"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ingresar_datos', methods=['POST'])
def ingresar_datos():
    nombre = request.form['nombre']
    edad = request.form['edad']
    if not nombre or not edad:
        flash('Por favor, complete todos los campos.')
        return redirect(url_for('index'))
    
    return redirect(url_for('seleccionar_fecha', nombre=nombre, edad=edad))

@app.route('/seleccionar_fecha')
def seleccionar_fecha():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    return render_template('seleccionar_fecha.html', nombre=nombre, edad=edad)

@app.route('/confirmar_fecha', methods=['POST'])
def confirmar_fecha():
    fecha_str = request.form['fecha']
    nombre = request.form['nombre']
    edad = request.form['edad']
    fecha_seleccionada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return redirect(url_for('seleccionar_horario', nombre=nombre, edad=edad, fecha=fecha_seleccionada))

@app.route('/seleccionar_horario')
def seleccionar_horario():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    fecha = request.args.get('fecha')
    return render_template('seleccionar_horario.html', nombre=nombre, edad=edad, fecha=fecha)

@app.route('/seleccionar_pelicula', methods=['POST'])
def seleccionar_pelicula():
    nombre = request.form['nombre']
    edad = int(request.form['edad'])
    fecha = request.form['fecha']
    peliculas = peliculas_adultos + peliculas_todo_publico if edad >= 18 else peliculas_todo_publico
    return render_template('seleccionar_pelicula.html', nombre=nombre, edad=edad, fecha=fecha, peliculas=peliculas)

@app.route('/confirmar_pelicula', methods=['POST'])
def confirmar_pelicula():
    nombre = request.form['nombre']
    edad = request.form['edad']
    fecha = request.form['fecha']
    pelicula_seleccionada = request.form['pelicula']
    return redirect(url_for('seleccionar_asientos', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula_seleccionada))

@app.route('/seleccionar_asientos')
def seleccionar_asientos():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    fecha = request.args.get('fecha')
    pelicula = request.args.get('pelicula')

    # Inicializar asientos
    filas, columnas = 16, 14
    matriz = inicializar_asientos(filas, columnas)
    ocupar_asientos_aleatoriamente(matriz, asientos_ocupados)

    return render_template('seleccionar_asientos.html', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula, matriz=matriz)

@app.route('/realizar_pago', methods=['POST'])
def realizar_pago():
    nombre = request.form['nombre']
    edad = request.form['edad']
    fecha = request.form['fecha']
    pelicula = request.form['pelicula']
    cantidad_entradas = int(request.form['cantidad_entradas'])  # Agregando este campo
    total = cantidad_entradas * PRECIO_ENTRADA  # Asegúrate de definir PRECIO_ENTRADA

    return render_template('realizar_pago.html', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula, cantidad_entradas=cantidad_entradas, total=total)

@app.route('/confirmar_pago', methods=['POST'])
def confirmar_pago():
    nombre = request.form['nombre']
    edad = request.form['edad']
    pelicula = request.form['pelicula']
    fecha = request.form['fecha']
    cantidad_entradas = request.form['cantidad_entradas']
    total = request.form['total']
    metodo_pago = request.form['tipo_pago']  # Ajustado para recoger el método de pago

    # Lógica de confirmación del pago puede ir aquí

    flash('¡Pago realizado con éxito!')
    return redirect(url_for('imprimir_entrada', nombre=nombre, edad=edad, pelicula=pelicula, fecha=fecha, cantidad_entradas=cantidad_entradas, total=total))

@app.route('/imprimir_entrada')
def imprimir_entrada():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    pelicula = request.args.get('pelicula')
    fecha = request.args.get('fecha')
    cantidad_entradas = request.args.get('cantidad_entradas')
    total = request.args.get('total')

    nombre_archivo = f"entrada_{nombre}_{pelicula}.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Entrada de Cine")
    c.drawString(100, 730, f"Nombre: {nombre}")
    c.drawString(100, 710, f"Edad: {edad}")
    c.drawString(100, 690, f"Película: {pelicula}")
    c.drawString(100, 670, f"Fecha: {fecha}")
    c.drawString(100, 650, f"Cantidad de Entradas: {cantidad_entradas}")
    c.drawString(100, 630, f"Total: ${total}")
    c.save()

    flash("Entrada impresa con éxito")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
