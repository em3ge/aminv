from time import sleep
from flask import Flask, session
from flask import render_template, request, redirect
from flaskext.mysql import MySQL

from funciones import *

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

app.secret_key = '123456'

@app.route('/')
def index():

    logueado = esta_logueado()
    if logueado:
        clave = session["user"]
        if clave != '':
            [fecha, hora, contador] = fecha_hora_contador(clave,mysql)
            amigos = recuperar_amigos(clave,mysql)
            return render_template('prueba/index.html', clave = clave, fecha = fecha, hora = hora, contador = contador, amigos = amigos, logueado = logueado)
        else:
            return render_template('prueba/index.html')
    else:
        return render_template('prueba/index.html', logueado = logueado)

@app.route('/logout', methods=['POST'])
def logout_usuario():
    logout()
    return redirect('/')

@app.route('/entrar', methods=['POST'])
def entrar():

    logueado = esta_logueado()
    if not logueado:
        clave = request.form['clave']
        login(clave)
    return redirect('/')


@app.route('/nuevo', methods=['POST'])
def nuevo():

    clave = randomPass();
    login(clave)
    insertar_usuario(clave,mysql)
    return redirect('/')



@app.route('/store', methods=['POST'])
def storage():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _clave = request.form['clave']

    insertar_amigo(_clave,mysql,_nombre,_correo)
    
    return redirect('/')

@app.route('/editar', methods=['POST'])
def editar():

    clave = request.form['clave']
    id = request.form['id']
    [fecha, hora, contador] = fecha_hora_contador(clave,mysql)
    amigo = datos_amigo(clave,id,mysql)
    logueado = esta_logueado()
    return render_template('prueba/editar.html', clave = clave, fecha = fecha, hora = hora, contador = contador, amigo = amigo, logueado = logueado)

@app.route('/destroy/<int:id>', methods=['POST'])
def destroy(id):

    clave = request.form['clave']
    borrar_amigo(id,clave,mysql)

    return redirect('/')

@app.route('/no_regalo', methods=['POST'])
def no_regalo():

    clave = request.form['clave']
    id = request.form['id']
    id_nuevo = request.form['nuevo_no_regalo']
    if id_nuevo != '':
        insertar_no_amigo(clave,mysql,id,id_nuevo)

    return redirect('/')

@app.route('/reset_no_regalo', methods=['POST'])
def reset_no_regalo():

    clave = request.form['clave']
    id = request.form['id']
    borrar_no_amigos(id,clave,mysql)

    return redirect('/')

@app.route('/prueba')
def prueba():

    clave = session["user"]
    insertar_amigo(clave,mysql,"Mikel","gilfernandezmikel@gmail.com")
    insertar_amigo(clave,mysql,"Azahara","em3ge@hotmail.com")
    insertar_amigo(clave,mysql,"Miry","em13ge@gmail.com")
    insertar_amigo(clave,mysql,"Antonio","mikel@windline.es")
    insertar_amigo(clave,mysql,"Melany","ee@ee.ee")
    insertar_amigo(clave,mysql,"Rubén","ff@ff.ff")

    return redirect('/')

@app.route('/estudio')
def estudio():
    for x in range(200):
        asignar()
    return redirect('/')

@app.route('/confirmar_edicion', methods=['POST'])
def confirmar_edicion():

    clave = session["user"]
    nuevo_nombre = request.form['txtNombre']
    nuevo_correo = request.form['txtCorreo']
    id = request.form['id']
    actualizar_datos_amigo(clave,id,nuevo_nombre,nuevo_correo,mysql)

    return redirect('/')

@app.route('/asignar', methods=['POST'])
def asignar():

    clave = session["user"]
    ids = id_posibles(clave,mysql)
    intentos = 1
    sorteo_ok = False
    while sorteo_ok == False:
        borrar_asignados(clave,mysql)
        if intentos < 30:
            for i in range(len(ids)):
                asignar_amigo(ids[i],ids,clave,mysql)
                ids = id_posibles(clave,mysql)

            if asignacion_valida(clave,mysql):
                sorteo_ok = True
                asignados = lista_asignados(clave,mysql)
                cad_asignados = de_lista_a_cadena(asignados)
                cad_participantes = de_lista_a_cadena(ids)
                agregar_asignaciones(clave,cad_participantes,cad_asignados,intentos,mysql)
            else:
                intentos = intentos + 1
        else:
            return redirect('/')
    return redirect('/') 

@app.route('/mandar_correos', methods=['POST'])
def mandar_correos():

    clave = session["user"]
    ids = id_posibles(clave,mysql)
    for i in range(len(ids)):
        nombre = recuperar_nombre(clave,ids[i],mysql)
        correo = recuperar_correo(clave,ids[i],mysql)
        amigo = recuperar_asignado(clave,ids[i],mysql)
        nombreAmigo = recuperar_nombre(clave,amigo,mysql)
        print("Hola, ", nombre, "(",correo, ") Regala a: ", nombreAmigo)
        mandar_email(clave,nombre,correo,nombreAmigo)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

