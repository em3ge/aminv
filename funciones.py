from flask import Flask, session
import string, random
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def login(clave):
    session.clear()
    session["user"] = clave
    session["auth"] = 1

def logout():
    session.clear()
    session["user"] = ""
    session["auth"] = 0

def esta_logueado():
    if session["user"] != '':
        return True
    else:
        return False

def randomPass():
    clave= ''
    for a in range(6):
        clave = clave + random.choice(string.ascii_letters)
    return clave

def esta_usuario(clave,mysql):
    sql = "SELECT COUNT(*) FROM usuarios WHERE clave=%s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    esta = resultado[0][0]
    if esta:
        return True
    else:
        return False

def fecha_hora_contador(clave,mysql):
    sql2 = "SELECT fecha, hora, contador FROM usuarios WHERE clave=%s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql2,datos)
    resultado = cursor.fetchall()
    conn.commit()
    fecha = resultado[0][0]
    hora = resultado[0][1]
    contador = resultado[0][2]
    return [fecha, hora, contador]

def recuperar_amigos(clave,mysql):
    sql = "SELECT * FROM amigos WHERE clave = %s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    amigos = cursor.fetchall()
    conn.commit()
    return amigos

def insertar_usuario(clave,mysql):
    sql = "INSERT INTO usuarios (`clave`, `contador`) VALUES (%s,%s);"
    datos = (clave,0)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def insertar_amigo(_clave,mysql,_nombre,_correo):
    sql = "INSERT INTO amigos (`id`, `nombre`, `correo`,  `no`, `clave`) VALUES (%s, %s, %s, %s, %s);"
    id = contador(_clave,mysql)
    actualizar_contador(_clave,mysql)
    datos = (id,_nombre,_correo,'',_clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def borrar_amigo(id,clave,mysql):
    sql = "DELETE FROM amigos WHERE id = %s AND clave = %s;"
    datos = (id,clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def recuperar_no_amigos(clave,id,mysql):
    sql = "SELECT no FROM amigos WHERE clave = %s AND id=%s;"
    datos = (clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    no_amigos = resultado[0][0]
    conn.commit()
    return no_amigos

def recuperar_ya_regalados(clave,mysql):
    sql = "SELECT asignado FROM amigos WHERE clave = %s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    final = [i[0] for i in cursor.fetchall()]
    conn.commit()
    return final

def lista_asignados(clave,mysql):
    sql = "SELECT asignado FROM amigos WHERE clave = %s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    final = [i[0] for i in cursor.fetchall()]
    conn.commit()
    return final

def insertar_no_amigo(_clave,mysql,id,id_nuevo):
    no_amigos_antes = recuperar_no_amigos(_clave,id,mysql)
    if no_amigos_antes!= '':
        no_amigos_nuevo = no_amigos_antes + ', ' + id_nuevo
    else:
        no_amigos_nuevo = id_nuevo
    sql =  "UPDATE amigos SET no=%s WHERE id=%s AND clave=%s;"
    datos = (no_amigos_nuevo,id,_clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def borrar_no_amigos(id,clave,mysql):
    sql = "UPDATE amigos SET no='' WHERE id=%s AND clave=%s;"
    datos = (id,clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def contador(clave,mysql):
    sql = "SELECT contador FROM usuarios WHERE clave=%s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    contador = resultado[0][0]
    return contador

def actualizar_contador(clave,mysql):
    sql = "UPDATE usuarios SET contador=%s WHERE clave=%s;"
    datos = (contador(clave,mysql)+1,clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def datos_amigo(clave,id,mysql):
    sql = "SELECT * FROM amigos WHERE clave=%s AND id=%s;"
    datos = (clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    return resultado

def actualizar_datos_amigo(clave,id,nuevoNombre,nuevoCorreo,mysql):
    sql = "UPDATE amigos SET nombre=%s, correo=%s WHERE clave=%s AND id=%s;"
    datos = (nuevoNombre,nuevoCorreo,clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    
def id_posibles(clave,mysql):
    sql = "SELECT id FROM amigos WHERE clave=%s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    final = [i[0] for i in cursor.fetchall()]
    conn.commit()
    return final

def asignar_amigo(id,ids,clave,mysql):
    
    ids.remove(id)

    no_regala_a = recuperar_no_amigos(clave,id,mysql)
    if no_regala_a!='':
        a = de_cadena_string_a_lista_int(no_regala_a)
    else:
        a = list()
    b = elementos_no_comunes_lista(ids,a)

    ya_regalados = recuperar_ya_regalados(clave,mysql)
    c = de_lista_int_a_lista_int_sin_ceros(ya_regalados)
    d = elementos_no_comunes_lista(b,c)

    if len(d)>0:
        aleatorio = random.randint(0, len(d)-1)
        amigo_invisible = d[aleatorio]
    else:
        aleatorio =999
        amigo_invisible = 999

    definir_amigo_invisible(id,amigo_invisible,clave,mysql)

    return ids

def definir_amigo_invisible(id,amigo_invisible,clave,mysql):
    sql = "UPDATE amigos SET asignado=%s WHERE clave=%s AND id=%s;"
    datos = (amigo_invisible,clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def de_cadena_string_a_lista_int(a):
    a = a.split(',')
    for i in range(len(a)):
        a[i] = int(a[i])
    return a

def de_lista_int_a_lista_int_sin_ceros(a):
    b = list()
    for i in range(len(a)):
        if a[i]!=0:
            b.append(a[i])
    return b

def de_lista_a_cadena(a):
    b = ''
    for x in range(len(a)):
        b = b + str(a[x]) + ", "
    return b

def elementos_no_comunes_lista(a,b):
    for i in range(len(b)):
        if b[i] in a:
            a.remove(b[i])
    return a

def borrar_asignados(clave,mysql):
    sql = "UPDATE amigos SET asignado=0 WHERE clave=%s;"
    datos = (clave)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

def asignacion_valida(clave,mysql):

    asignados = lista_asignados(clave,mysql)
    if 999 in asignados:
        return False
    else:
        return True

def mandar_email(clave,nombre,destinatario,nombreAmigo):

    username = "gilfernandezmikel@gmail.com"
    password = "wsidcauljpvcuoex"
    mail_from = "Desde Amigo Invisible Mik 1.0"
    mail_to = destinatario
    mail_subject = "Amigo Invisible [" + clave + "]"
    mail_body = "Hola, " + nombre + ". Te ha tocado " + nombreAmigo 

    mimemsg = MIMEMultipart()
    mimemsg['From']=mail_from
    mimemsg['To']=mail_to
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
    connection.starttls()
    connection.login(username,password)
    connection.send_message(mimemsg)
    connection.quit()

def recuperar_correo(clave,id,mysql):
    sql = "SELECT correo FROM amigos WHERE clave=%s AND id=%s;"
    datos = (clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    correo = resultado[0][0]
    return correo

def recuperar_asignado(clave,id,mysql):
    sql = "SELECT asignado FROM amigos WHERE clave=%s AND id=%s;"
    datos = (clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    asignado = resultado[0][0]
    return asignado

def recuperar_nombre(clave,id,mysql):
    sql = "SELECT nombre FROM amigos WHERE clave=%s AND id=%s;"
    datos = (clave,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    resultado = cursor.fetchall()
    conn.commit()
    nombre = resultado[0][0]
    return nombre
    
def agregar_asignaciones(clave,participantes,asignados,intentos,mysql):
    print(clave, " - ", participantes, " - ",asignados, " - ",intentos)
    sql = "INSERT INTO asignaciones (`clave`, `participantes`, `asignados`, `intentos`) VALUES (%s,%s,%s,%s);"
    datos = (clave,participantes,asignados,intentos)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()