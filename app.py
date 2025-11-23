from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import pymysql

# Cargar variables de entorno (Debe ser lo primero)
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia esto en producción

# Configuración de MySQL (Nombres de variables sincronizados con tu .env)
DB_USER = os.getenv("DB_USERNAME")  # Coincide con DB_USERNAME en .env
DB_PASS = os.getenv("DB_PASSWORD")  # Coincide con DB_PASSWORD en .env
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_DATABASE") # Coincide con DB_DATABASE en .env
DB_PORT = os.getenv("DB_PORT")     # Opcional, pero bueno incluirlo

# URI de SQLAlchemy
# Usamos f-string para construir la URI con los valores cargados
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelo de Contacto
class Contact(db.Model):
    __tablename__ = 'contactos' # Asegura que use el nombre de tabla correcto
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tablas si no existen
with app.app_context():
    # Intenta crear las tablas. Si falla aquí, significa que la conexión sigue mal.
    try:
        db.create_all()
        print("INFO: Tablas de base de datos creadas o verificadas correctamente.")
    except Exception as e:
        print("FATAL ERROR: Fallo al conectar o crear tablas. Revisa la URI y permisos.")
        print(e)


# Ruta principal (formulario)
@app.route("/")
def index():
    return render_template("index.html")

# Guardar contacto
@app.route("/save", methods=["POST"])
def save():
    try:
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")

        # Validación básica
        if not nombre or not correo:
            flash("Nombre y correo son obligatorios.")
            return redirect("/")

        # Verificar duplicado
        if Contact.query.filter_by(correo=correo).first():
            flash("El correo ya existe en tus contactos.")
            return redirect("/")

        # Guardar contacto
        nuevo = Contact(nombre=nombre, correo=correo, telefono=telefono)
        db.session.add(nuevo)
        db.session.commit()

        flash("Contacto guardado correctamente.")
        return redirect("/")

    except Exception as e:
        # Mostrar error en consola y en flash
        print("Error al guardar contacto:", e)
        flash("Ocurrió un error al guardar el contacto. Revisa la configuración del servidor web.")
        return redirect("/")

# Lista de contactos
@app.route("/contacts")
def contacts():
    try:
        all_contacts = Contact.query.order_by(Contact.fecha_registro.desc()).all()
        return render_template("contacts.html", contacts=all_contacts)
    except Exception as e:
        print("Error al cargar contactos:", e)
        flash("No se pudieron cargar los contactos.")
        return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)