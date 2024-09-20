import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def cerrar_sesion(ventana_actual):
    ventana_actual.destroy()
    ventana.deiconify()

# Función para encriptar contraseñas
def encriptar_contraseña(contraseña):
    return hashlib.sha256(contraseña.encode()).hexdigest()

# Función para verificar credenciales desde un archivo de texto
def verificar_credenciales(usuario, contraseña):
    contraseña_encriptada = encriptar_contraseña(contraseña)
    try:
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) >= 8:
                    if datos[7] == usuario and datos[8].strip() == contraseña_encriptada:
                        return datos[0]  # Retorna el rol
        return None
    except FileNotFoundError:
        print("El archivo usuarios.txt no existe")
        return None
    
def verificar_credenciales_Profesor(usuario, contraseña):
    contraseña_encriptada = encriptar_contraseña(contraseña)
    try:
        with open("profesores.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) >= 5:
                    if datos[4] == usuario and datos[5].strip() == contraseña_encriptada:
                        return datos[0]  # Retorna el rol
        return None
    except FileNotFoundError:
        print("El archivo profesores.txt no existe")
        return None

# Función para iniciar sesión
def iniciar_sesion():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()

    tipo_usuario = verificar_credenciales(usuario, contraseña)
    profesor = verificar_credenciales_Profesor(usuario, contraseña)

    if tipo_usuario == "Estudiante":
        messagebox.showinfo("Inicio de Sesión", "Bienvenido Estudiante")
        ventana.withdraw()
        abrir_ventana_estudiante()
    elif usuario == "Admin123" and contraseña == "!Admin123":
        messagebox.showinfo("Inicio de Sesión", "Bienvenido Administrador")
        ventana.withdraw()
        abrir_panel_administracion()
    elif profesor == "profesor":
        messagebox.showinfo("Inicio de Sesión", "Bienvenido profesor")
        ventana.withdraw()
        abrir_panel_profesor()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def verificar_usuario_existente(usuario):
    try:
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) >= 8 and datos[7] == usuario:  # El nombre de usuario está en la posición 4
                    return True
        return False
    except FileNotFoundError:
        return False

def enviar_correo(destinatario, asunto, cuerpo):
    remitente = "rodrigo.ortizcordova@gmail.com"  # Cambia esto por tu correo electrónico
    contraseña_remitente = "pokg ufzh dgby ikhh"  # Cambia esto por la contraseña de tu correo

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, contraseña_remitente)
        texto = msg.as_string()
        server.sendmail(remitente, destinatario, texto)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
        return False

def recuperar_contraseña(usuario):
    try:
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) >= 9:
                    if datos[7] == usuario:  # Verificar si el usuario coincide
                        correo = datos[4]
                        contraseña_original = datos[9]  # La contraseña original está en la posición 9

                        # Enviar correo
                        asunto = "Recuperación de contraseña"
                        cuerpo = f"Hola {datos[1]}, tu contraseña es: {contraseña_original}"
                        if enviar_correo(correo, asunto, cuerpo):
                            messagebox.showinfo("Éxito", f"Contraseña enviada al correo: {correo}")
                        else:
                            messagebox.showerror("Error", "No se pudo enviar el correo")
                        return
            messagebox.showerror("Error", "Usuario no encontrado")
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo de usuarios no existe")

# Función para registrar usuarios (solo estudiantes)
def registrar_usuario():
    global  entry_correo, entry_telefono, entry_nacimiento, entry_nombre, entry_apellido, entry_dpi, entry_usuario_reg, entry_contraseña_reg, entry_confirmacion

    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    dpi = entry_dpi.get()
    correo = entry_correo.get()
    telefono = entry_telefono.get()
    nacimiento = entry_nacimiento.get()
    usuario = entry_usuario_reg.get()
    contraseña = entry_contraseña_reg.get()
    confirmacion = entry_confirmacion.get()

    # Validación de nombre y apellido (sin números)
    if not re.match(r'^[a-zA-Z]+$', nombre):
        messagebox.showerror("Error", "El nombre no puede contener números ni caracteres especiales")
        return

    if not re.match(r'^[a-zA-Z]+$', apellido):
        messagebox.showerror("Error", "El apellido no puede contener números ni caracteres especiales")
        return

    # Validación de DPI (solo números)
    if not dpi.isdigit():
        messagebox.showerror("Error", "El DPI solo debe contener números")
        return

    # Validación de la contraseña (mínimo 8 caracteres, con al menos una minúscula, una mayúscula, un número y un carácter especial)
    if len(contraseña) < 8 or not re.search(r'[a-z]', contraseña) or not re.search(r'[A-Z]', contraseña) or not re.search(r'[0-9]', contraseña) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña):
        messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres, con una minúscula, una mayúscula, un número y un carácter especial")
        return

    # Verificación de que las contraseñas coincidan
    if contraseña != confirmacion:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return

    # Verificación de si el nombre de usuario ya existe
    if verificar_usuario_existente(usuario):
        messagebox.showerror("Error", "El nombre de usuario ya existe. Elija otro.")
        return

    if len(usuario.strip()) == 0 or len(contraseña.strip()) == 0:
        messagebox.showerror("Error", "Usuario o contraseña no pueden estar vacíos")
        return

    contraseña_encriptada = encriptar_contraseña(contraseña)

    # Guardar en archivo de texto
    with open("usuarios.txt", "a") as archivo:
        archivo.write(f"Estudiante;{nombre};{apellido};{dpi};{correo};{telefono};{nacimiento};{usuario};{contraseña_encriptada}\n")

    messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
    ventana_registro.destroy()
    ventana.deiconify()

# Función para abrir la ventana de registro
def abrir_ventana_registrarse():
    global  entry_correo, entry_telefono, entry_nacimiento, entry_nombre, entry_apellido, entry_dpi, entry_usuario_reg, entry_contraseña_reg, entry_confirmacion, ventana_registro

    ventana_registro = tk.Toplevel(ventana)
    ventana_registro.title("Registro de Usuarios")
    ventana_registro.geometry("400x600")

    tk.Label(ventana_registro, text="Nombre:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_registro)
    entry_nombre.pack(pady=5)

    tk.Label(ventana_registro, text="Apellido:").pack(pady=5)
    entry_apellido = tk.Entry(ventana_registro)
    entry_apellido.pack(pady=5)

    tk.Label(ventana_registro, text="DPI:").pack(pady=5)
    entry_dpi = tk.Entry(ventana_registro)
    entry_dpi.pack(pady=5)

    tk.Label(ventana_registro, text="Correo:").pack(pady=5)
    entry_correo = tk.Entry(ventana_registro)
    entry_correo.pack(pady=5)

    tk.Label(ventana_registro, text="Telefono:").pack(pady=5)
    entry_telefono = tk.Entry(ventana_registro)
    entry_telefono.pack(pady=5)

    tk.Label(ventana_registro, text="Fecha de nacimiento en (dd/mm/ññññ):").pack(pady=5)
    entry_nacimiento = tk.Entry(ventana_registro)
    entry_nacimiento.pack(pady=5)

    tk.Label(ventana_registro, text="Usuario:").pack(pady=5)
    entry_usuario_reg = tk.Entry(ventana_registro)
    entry_usuario_reg.pack(pady=5)

    tk.Label(ventana_registro, text="Contraseña:").pack(pady=5)
    entry_contraseña_reg = tk.Entry(ventana_registro, show="*")
    entry_contraseña_reg.pack(pady=5)

    tk.Label(ventana_registro, text="Confirmar Contraseña:").pack(pady=5)
    entry_confirmacion = tk.Entry(ventana_registro, show="*")
    entry_confirmacion.pack(pady=5)
    

    tk.Button(ventana_registro, text="Registrar", command=registrar_usuario).pack(pady=20)
def cargar_cursos():
    cursos = []
    if os.path.exists("cursos.txt"):
        with open("cursos.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) > 0:
                    cursos.append(datos[0])  # Agregar solo el nombre del curso
    return cursos
def editar_cursos():
    global entry_nombre_curso, entry_costo_curso, entry_horario_curso, entry_codigo_curso, entry_cupo_curso

    ventana_editar_curso = tk.Toplevel(ventana)
    ventana_editar_curso.title("Editar Curso")

    tk.Label(ventana_editar_curso, text="Seleccionar Curso:").pack(pady=5)
    cursos = cargar_cursos()
    combo_cursos = ttk.Combobox(ventana_editar_curso, values=cursos)
    combo_cursos.pack(pady=5)

    def cargar_datos_curso(event):
        curso_seleccionado = combo_cursos.get()
        if curso_seleccionado:
            with open("cursos.txt", "r") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(";")
                    if datos[0] == curso_seleccionado:
                        entry_nombre_curso.delete(0, tk.END)
                        entry_nombre_curso.insert(0, datos[0])
                        entry_costo_curso.delete(0, tk.END)
                        entry_costo_curso.insert(0, datos[1])
                        entry_horario_curso.delete(0, tk.END)
                        entry_horario_curso.insert(0, datos[2])
                        entry_codigo_curso.delete(0, tk.END)
                        entry_codigo_curso.insert(0, datos[3])
                        entry_cupo_curso.delete(0, tk.END)
                        entry_cupo_curso.insert(0, datos[4])
                        break

    combo_cursos.bind("<<ComboboxSelected>>", cargar_datos_curso)

    tk.Label(ventana_editar_curso, text="Nombre del Curso:").pack(pady=5)
    entry_nombre_curso = tk.Entry(ventana_editar_curso)
    entry_nombre_curso.pack(pady=5)

    tk.Label(ventana_editar_curso, text="Costo:").pack(pady=5)
    entry_costo_curso = tk.Entry(ventana_editar_curso)
    entry_costo_curso.pack(pady=5)

    tk.Label(ventana_editar_curso, text="Horario:").pack(pady=5)
    entry_horario_curso = tk.Entry(ventana_editar_curso)
    entry_horario_curso.pack(pady=5)

    tk.Label(ventana_editar_curso, text="Código del Curso:").pack(pady=5)
    entry_codigo_curso = tk.Entry(ventana_editar_curso)
    entry_codigo_curso.pack(pady=5)

    tk.Label(ventana_editar_curso, text="Cupo:").pack(pady=5)
    entry_cupo_curso = tk.Entry(ventana_editar_curso)
    entry_cupo_curso.pack(pady=5)

    def guardar_cambios():
        curso_seleccionado = combo_cursos.get()
        if curso_seleccionado:
            nuevos_datos = [
                entry_nombre_curso.get(),
                entry_costo_curso.get(),
                entry_horario_curso.get(),
                entry_codigo_curso.get(),
                entry_cupo_curso.get()
            ]
            # Leer todos los cursos y reemplazar el curso editado
            cursos_actuales = []
            with open("cursos.txt", "r") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(";")
                    if datos[0] == curso_seleccionado:
                        cursos_actuales.append(";".join(nuevos_datos) + "\n")
                    else:
                        cursos_actuales.append(linea)
            
            # Guardar los cambios en el archivo
            with open("cursos.txt", "w") as archivo:
                archivo.writelines(cursos_actuales)

            messagebox.showinfo("Éxito", "Curso editado exitosamente")
            ventana_editar_curso.destroy()

    tk.Button(ventana_editar_curso, text="Guardar Cambios", command=guardar_cambios).pack(pady=20)
# Función para abrir la ventana de estudiante
def abrir_ventana_estudiante():
    ventana_estudiante = tk.Toplevel(ventana)
    ventana_estudiante.title("Panel de Estudiante")

    label_estudiante = tk.Label(ventana_estudiante, text="Cursos Disponibles", font=("Arial", 14))
    label_estudiante.pack(pady=10)

    cursos_disponibles = cargar_cursos()
    label_cursos = tk.Label(ventana_estudiante, text="\n".join(cursos_disponibles), font=("Arial", 12))
    label_cursos.pack(pady=5)

    boton_inscribirse = tk.Button(ventana_estudiante, text="Inscribirse en Curso", width=20)
    boton_inscribirse.pack(pady=5)
    
    boton_cerrar_sesion = tk.Button(ventana_estudiante, text="Cerrar Sesión", command=lambda: cerrar_sesion(ventana_estudiante))
    boton_cerrar_sesion.pack(pady=20)

# Función para abrir el panel de administración
def abrir_panel_administracion():
    ventana_admin = tk.Toplevel(ventana)
    ventana_admin.title("Panel de Administración")

    tk.Label(ventana_admin, text="Administración de Cursos", font=("Arial", 16)).pack(pady=10)

    tk.Button(ventana_admin, text="Registrar Profesor", command=abrir_ventana_registrar_profesor).pack(pady=5)
    tk.Button(ventana_admin, text="Crear Curso", command=abrir_ventana_crear_curso).pack(pady=5)
    
    boton_cerrar_sesion = tk.Button(ventana_admin, text="Cerrar Sesión", command=lambda: cerrar_sesion(ventana_admin))
    boton_cerrar_sesion.pack(pady=20)

# Función para abrir la ventana de registro de profesor
def abrir_ventana_registrar_profesor():
    global entry_nombre_profesor, entry_apellido_profesor, entry_dpi_profesor, entry_usuario_profesor, entry_contraseña_profesor, ventana_registro_profesor

    ventana_registro_profesor = tk.Toplevel(ventana)
    ventana_registro_profesor.title("Registro de Profesor")
    ventana_registro_profesor.geometry("400x500")

    tk.Label(ventana_registro_profesor, text="Nombre:").pack(pady=5)
    entry_nombre_profesor = tk.Entry(ventana_registro_profesor)
    entry_nombre_profesor.pack(pady=5)

    tk.Label(ventana_registro_profesor, text="Apellido:").pack(pady=5)
    entry_apellido_profesor = tk.Entry(ventana_registro_profesor)
    entry_apellido_profesor.pack(pady=5)

    tk.Label(ventana_registro_profesor, text="DPI:").pack(pady=5)
    entry_dpi_profesor = tk.Entry(ventana_registro_profesor)
    entry_dpi_profesor.pack(pady=5)

    tk.Label(ventana_registro_profesor, text="Usuario:").pack(pady=5)
    entry_usuario_profesor = tk.Entry(ventana_registro_profesor)
    entry_usuario_profesor.pack(pady=5)

    tk.Label(ventana_registro_profesor, text="Contraseña:").pack(pady=5)
    entry_contraseña_profesor = tk.Entry(ventana_registro_profesor, show="*")
    entry_contraseña_profesor.pack(pady=5)

    tk.Button(ventana_registro_profesor, text="Registrar Profesor", command=registrar_profesor).pack(pady=20)

# Función para registrar un profesor
def registrar_profesor():
    global entry_nombre_profesor, entry_apellido_profesor, entry_dpi_profesor, entry_usuario_profesor, entry_contraseña_profesor

    nombre = entry_nombre_profesor.get()
    apellido = entry_apellido_profesor.get()
    dpi = entry_dpi_profesor.get()
    usuario = entry_usuario_profesor.get()
    contraseña = entry_contraseña_profesor.get()

    if len(usuario.strip()) == 0 or len(contraseña.strip()) == 0:
        messagebox.showerror("Error", "Usuario o contraseña no pueden estar vacíos")
        return

    contraseña_encriptada = encriptar_contraseña(contraseña)

    # Guardar en archivo de texto
    with open("profesores.txt", "a") as archivo:
        archivo.write(f"profesor;{nombre};{apellido};{dpi};{usuario};{contraseña_encriptada}\n")

    messagebox.showinfo("Éxito", "Profesor registrado exitosamente")
    ventana_registro_profesor.destroy()

# Función para cargar la lista de profesores
def cargar_profesores():
    profesores = []
    if os.path.exists("profesores.txt"):
        with open("profesores.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) > 0:
                    profesores.append(datos[4])  # Agregar solo el usuario (nombre de usuario)
    return profesores
# Función para abrir el panel de administración del profesor
def abrir_panel_profesor():
    ventana_profesor = tk.Toplevel(ventana)
    ventana_profesor.title("Panel de Profesor")

    tk.Label(ventana_profesor, text="Administración de Cursos", font=("Arial", 16)).pack(pady=10)

    tk.Button(ventana_profesor, text="Editar Cursos", command=editar_cursos).pack(pady=5)
    tk.Button(ventana_profesor, text="Ver Registro de Notas", command=ver_registro_notas).pack(pady=5)
    tk.Button(ventana_profesor, text="Descargar Notas (.xlsx)", command=descargar_notas).pack(pady=5)

    boton_cerrar_sesion = tk.Button(ventana_profesor, text="Cerrar Sesión", command=lambda: cerrar_sesion(ventana_profesor))
    boton_cerrar_sesion.pack(pady=20)

def cargar_notas():
    notas = []
    if os.path.exists("notas.txt"):
        with open("notas.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) > 0:
                    notas.append(datos)  # Cada fila como una lista
    return notas

def ver_registro_notas():
    ventana_notas = tk.Toplevel(ventana)
    ventana_notas.title("Registro de Notas")

    tk.Label(ventana_notas, text="Seleccionar Estudiante:").pack(pady=5)

    estudiantes = cargar_estudiantes()  # Función que debe cargar la lista de estudiantes
    combo_estudiantes = ttk.Combobox(ventana_notas, values=estudiantes)
    combo_estudiantes.pack(pady=5)

    def cargar_datos_estudiante(event):
        estudiante_seleccionado = combo_estudiantes.get()
        if estudiante_seleccionado:
            # Cargar notas del estudiante
            for fila in cargar_notas():
                if fila[0] == estudiante_seleccionado:
                    entry_tarea.delete(0, tk.END)
                    entry_tarea.insert(0, fila[1])
                    entry_parcial1.delete(0, tk.END)
                    entry_parcial1.insert(0, fila[2])
                    entry_parcial2.delete(0, tk.END)
                    entry_parcial2.insert(0, fila[3])
                    entry_parcial3.delete(0, tk.END)
                    entry_parcial3.insert(0, fila[4])
                    entry_examen_final.delete(0, tk.END)
                    entry_examen_final.insert(0, fila[5])
                    break

    combo_estudiantes.bind("<<ComboboxSelected>>", cargar_datos_estudiante)

    # Entradas para las notas
    tk.Label(ventana_notas, text="Nota de Tarea:").pack(pady=5)
    entry_tarea = tk.Entry(ventana_notas)
    entry_tarea.pack(pady=5)

    tk.Label(ventana_notas, text="Nota Parcial 1:").pack(pady=5)
    entry_parcial1 = tk.Entry(ventana_notas)
    entry_parcial1.pack(pady=5)

    tk.Label(ventana_notas, text="Nota Parcial 2:").pack(pady=5)
    entry_parcial2 = tk.Entry(ventana_notas)
    entry_parcial2.pack(pady=5)

    tk.Label(ventana_notas, text="Nota Parcial 3:").pack(pady=5)
    entry_parcial3 = tk.Entry(ventana_notas)
    entry_parcial3.pack(pady=5)

    tk.Label(ventana_notas, text="Nota Examen Final:").pack(pady=5)
    entry_examen_final = tk.Entry(ventana_notas)
    entry_examen_final.pack(pady=5)

    def guardar_notas(): 
        estudiante_seleccionado = combo_estudiantes.get()
        
        try:
            # Obtener las notas y convertirlas a float
            tarea = float(entry_tarea.get())
            parcial1 = float(entry_parcial1.get())
            parcial2 = float(entry_parcial2.get())
            parcial3 = float(entry_parcial3.get())
            examen_final = float(entry_examen_final.get())
            
            # Validar que las notas no sean negativas
            if any(n < 0 for n in [tarea, parcial1, parcial2, parcial3, examen_final]):
                messagebox.showerror("Error", "Las notas no pueden ser negativas.")
                return
            
            # Validar que la suma de las notas no sea mayor a 100
            total_notas = tarea + parcial1 + parcial2 + parcial3 + examen_final
            if total_notas > 100:
                messagebox.showerror("Error", "La suma de las notas no puede ser mayor a 100.")
                return

            # Crear la lista de nuevas notas
            nuevas_notas = [
                estudiante_seleccionado,
                str(tarea),
                str(parcial1),
                str(parcial2),
                str(parcial3),
                str(examen_final)
            ]
            
            # Leer todas las notas y reemplazar las del estudiante editado
            notas_actuales = cargar_notas()
            for i in range(len(notas_actuales)):
                if notas_actuales[i][0] == estudiante_seleccionado:
                    notas_actuales[i] = nuevas_notas
                    break
            else:
                # Si el estudiante no tenía notas, añadirlas
                notas_actuales.append(nuevas_notas)

            # Guardar las notas actualizadas en el archivo
            with open("notas.txt", "w") as archivo:
                for fila in notas_actuales:
                    archivo.write(";".join(fila) + "\n")

            messagebox.showinfo("Éxito", "Notas guardadas exitosamente")
            ventana_notas.destroy()

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos para las notas.")

    # Agregar botón para guardar notas
    tk.Button(ventana_notas, text="Guardar Notas", command=guardar_notas).pack(pady=10)
def cargar_estudiantes():
    estudiantes = []
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(";")
                if len(datos) > 0:
                    estudiantes.append(datos[7])  # Suponiendo que el usuario está en la posición 7
    return estudiantes
# Función de ejemplo para descargar notas (deberás implementar la lógica de descarga)
def descargar_notas():
    messagebox.showinfo("Descargar Notas", "Aquí podrás descargar el registro de notas en .xlsx.")
# Función para abrir la ventana de crear curso
def abrir_ventana_crear_curso():
    global entry_nombre_curso, entry_costo_curso, entry_horario_curso, entry_codigo_curso, entry_cupo_curso, entry_catedratico_curso, ventana_crear_curso

    ventana_crear_curso = tk.Toplevel(ventana)
    ventana_crear_curso.title("Crear Curso")
    ventana_crear_curso.geometry("400x500")

    tk.Label(ventana_crear_curso, text="Nombre del Curso:").pack(pady=5)
    entry_nombre_curso = tk.Entry(ventana_crear_curso)
    entry_nombre_curso.pack(pady=5)

    tk.Label(ventana_crear_curso, text="Costo:").pack(pady=5)
    entry_costo_curso = tk.Entry(ventana_crear_curso)
    entry_costo_curso.pack(pady=5)

    tk.Label(ventana_crear_curso, text="Horario:").pack(pady=5)
    entry_horario_curso = tk.Entry(ventana_crear_curso)
    entry_horario_curso.pack(pady=5)

    tk.Label(ventana_crear_curso, text="Código del Curso:").pack(pady=5)
    entry_codigo_curso = tk.Entry(ventana_crear_curso)
    entry_codigo_curso.pack(pady=5)

    tk.Label(ventana_crear_curso, text="Cupo:").pack(pady=5)
    entry_cupo_curso = tk.Entry(ventana_crear_curso)
    entry_cupo_curso.pack(pady=5)

    tk.Label(ventana_crear_curso, text="Catedrático:").pack(pady=5)
    entry_catedratico_curso = ttk.Combobox(ventana_crear_curso, values=cargar_profesores())
    entry_catedratico_curso.pack(pady=5)

    tk.Button(ventana_crear_curso, text="Crear Curso", command=crear_curso).pack(pady=20)

# Función para crear un curso
def crear_curso():
    global entry_nombre_curso, entry_costo_curso, entry_horario_curso, entry_codigo_curso, entry_cupo_curso, entry_catedratico_curso

    nombre = entry_nombre_curso.get()
    costo = entry_costo_curso.get()
    horario = entry_horario_curso.get()
    codigo = entry_codigo_curso.get()
    cupo = entry_cupo_curso.get()
    catedratico = entry_catedratico_curso.get()

    if len(nombre.strip()) == 0 or len(costo.strip()) == 0 or len(horario.strip()) == 0 or len(codigo.strip()) == 0 or len(cupo.strip()) == 0 or len(catedratico.strip()) == 0:
        messagebox.showerror("Error", "Todos los campos deben ser completados")
        return

    # Guardar en archivo de texto
    with open("cursos.txt", "a") as archivo:
        archivo.write(f"{nombre};{costo};{horario};{codigo};{cupo};{catedratico}\n")

    messagebox.showinfo("Éxito", "Curso creado exitosamente")
    ventana_crear_curso.destroy()

# Configuración inicial de la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Gestión de Cursos - Academia USAC")
ventana.geometry("400x300")

label_bienvenida = tk.Label(ventana, text="Iniciar Sesión", font=("Arial", 16))
label_bienvenida.pack(pady=10)

label_usuario = tk.Label(ventana, text="Usuario:")
label_usuario.pack()

entry_usuario = tk.Entry(ventana)
entry_usuario.pack()

label_contraseña = tk.Label(ventana, text="Contraseña:")
label_contraseña.pack()

entry_contraseña = tk.Entry(ventana, show="*")
entry_contraseña.pack()

boton_iniciar_sesion = tk.Button(ventana, text="Iniciar Sesión", command=iniciar_sesion)
boton_iniciar_sesion.pack(pady=10)

boton_registrarse = tk.Button(ventana, text="Registrarse", command=abrir_ventana_registrarse)
boton_registrarse.pack(pady=10)

def abrir_recuperar_contraseña():
    usuario = entry_usuario.get()
    if not usuario:
        messagebox.showerror("Error", "Por favor, ingrese su usuario")
        return
    recuperar_contraseña(usuario)

boton_recuperar_contraseña = tk.Button(ventana, text="Olvidé mi contraseña", command=abrir_recuperar_contraseña)
boton_recuperar_contraseña.pack(pady=10)

# Verifica si los archivos necesarios existen, si no los crea
for archivo in ["usuarios.txt", "profesores.txt", "cursos.txt"]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            pass
if not os.path.exists("profesores.txt"):
    with open("profesores.txt", "w") as f:
        pass

if not os.path.exists("cursos.txt"):
    with open("cursos.txt", "w") as f:
        pass
ventana.mainloop()