# coding: latin-1
import sys
import logging
import pymysql
import json
import os, base64, datetime, hashlib, hmac

urlbase = "https://utad-tube.s3.amazonaws.com/htmls/templates/"

# Variables de sql
rds_host = "macascript.com"

username = "user"
password = "password"

dbname = "utadtubedb"

# Variables de S3
access_key = 'ASIAXBQ2N3L47ACMKZAX'
secret_key = 'UJ0Wz0yT+fXKP7yEuXU82A3+FBkQY0x9wwqu758g'
securityToken= 'FwoGZXIvYXdzEEwaDF9Ye1L4h10rRXsq/yK8AeUd9mPvRlBM+4mRh4tbjyIY/5d6m9BWjC/Mkqs6jdzxt9mZOj2wL9KaKaaRXS2EuSeEzLGJsHE0eBk/cb9RZdW70YlZVfUHbdOU5pYFtpVfx2hNLDsP3XGYC65p1w+4HySquaw2QKhTCl4wX2Ed1iM+8Tri/g92YXnyxNGv5V9IVM1skSuZl+SOynzhC3dgIjQ2NUAtMkwpHA5NZhTVbblsV6qoymwlFer6dHi0fH0JrudRsN7LlfX2wSEKKLPMto8GMi3Wnji9OVq2rO5QDsBLlF7GNZ9quFaVzjOb920t0gzmO1F7PWd6zr6tRIBAa1I='

bucket = "utad-tube"
bucketUrl = "https://utad-tube.s3.amazonaws.com/"
region = 'us-east-1'
service = 's3'

t = datetime.datetime.utcnow()
amzDate = t.strftime('%Y%m%dT%H%M%SZ')
dateStamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

policy = """{"expiration": "2023-12-30T12:00:00.000Z",
"conditions": [
{"bucket": \""""+bucket+"""\"},
["starts-with", "$key", ""],
{"acl": "public-read"},
["starts-with","$success_action_redirect", \"\"],
    {"x-amz-credential": \""""+ access_key+"/"+dateStamp+"/"+region+"""/s3/aws4_request"},
    {"x-amz-algorithm": "AWS4-HMAC-SHA256"},
    {"x-amz-date": \""""+amzDate+"""\" },
    {"x-amz-security-token": \"""" + securityToken +"""\"  }
  ]
}"""

# FUNCIONES AUXILIARES

def connect():
    try:
        return pymysql.connect(host=rds_host, user=username, password=password, database=dbname, connect_timeout=10, port=3306)
    except pymysql.MySQLError as e:
        print(e)
        sys.exit()

def tagsDeVideo(conn,videoId):
    tags = []
    try:
        with conn.cursor() as cur:
            cur.execute("select tag from Video_Tags where videoId = "+str(videoId))
            conn.commit()
            for tag in cur.fetchall():
                tags.append(tag[0])
    except pymysql.MySQLError as e:
        print(e)
    return tags

def votosNegativos(conn,videoId):
    suma = 0
    try:
        with conn.cursor() as cur:
            cur.execute("select count(valor) from Voto where videoId = "+str(videoId)+" and valor=-1")
            row = cur.fetchone()
            if (row is not None):
                suma = abs(int(row[0]))
    except pymysql.MySQLError as e:
        print(e)
    return suma

def votosPositivos(conn,videoId):
    suma = 0
    try:
        with conn.cursor() as cur:
            cur.execute("select count(valor) from Voto where videoId = "+str(videoId)+" and valor=1")
            row = cur.fetchone()
            if (row is not None):
                suma = int(row[0])
    except pymysql.MySQLError as e:
        print(e)
    return suma

def comentariosDeComentarios(conn,comentarioPadreId):
    comentarios = []
    try:
        with conn.cursor() as cur:
            cur.execute("select c.id, u.id, u.nombreUsuario, c.contenido "+
                        "from Comentario c join Usuario u on c.usuarioId = u.id "+
                        "where comentarioPadreId="+str(comentarioPadreId))
            conn.commit()
            row = cur.fetchall()
            if (row is not None):
                for comentario in row:
                    comentarios.append({
                        "id": comentario[0],
                        "usuarioId": comentario[1],
                        "nombreUsuario": comentario[2],
                        "contenido": comentario[3]
                    })
    except pymysql.MySQLError as e:
        print(e)
    return comentarios

def comentarios(conn,videoId):
    comentarios = []
    try:
        with conn.cursor() as cur:
            cur.execute("select c.id, u.id, u.nombreUsuario, c.contenido "+
                        "from Comentario c join Usuario u on c.usuarioId = u.id "+
                        "where videoId="+str(videoId)+" and comentarioPadreId is null order by c.id asc")
            conn.commit()
            row = cur.fetchall()
            if (row is not None):
                for comentario in row:
                    comentarios.append({
                        #"id": comentario[0],
                        "usuarioId": comentario[1],
                        "nombreUsuario": comentario[2],
                        "contenido": comentario[3]#,
                        #"hilo": comentariosDeComentarios(conn,comentario[0])
                    })
    except pymysql.MySQLError as e:
        print(e)
    return comentarios


# FUNCIONES DE inicio.html

def inicio():
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:

            cur.execute("select v.id,u.id,v.nombre,u.nombreUsuario,fechaSubida,rutaAWSMiniatura "+
                        "from Video v join Usuario u on v.usuarioId = u.id "+
                        "order by fechaSubida desc limit 30")
            conn.commit()
            body["videos"] = []
            for video in cur.fetchall():
                body["videos"].append({
                    "id": video[0],
                    "usuarioId": video[1],
                    "nombre": video[2],
                    "nombreUsuario": video[3],
                    "fechaSubida": video[4].strftime("%m/%d/%Y, %H:%M:%S"),
                    "imagen": video[5],
                    "tags": tagsDeVideo(conn,video[0])
                    })
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def login(user,password):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("select id,nombreUsuario,habilitado from Usuario where (email=%s or nombreUsuario=%s) and contrasenya=%s",(user,user,password))
            conn.commit()
            row = cur.fetchone()
            if row is not None and row[2]:
                body["id"] = row[0]
                body["nombreUsuario"] = row[1]
                body["redirectPage"] = urlbase+"misvideos.html"
            else:
                body["id"] = 0
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def registrarse(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("select 1 from Usuario where nombreUsuario='"+nombreUsuario+"'")
            conn.commit()
            ok = 0
            if cur.fetchone() is not None:
                ok += 1
                body["nombreUsuario"] = False
            else:
                body["nombreUsuario"] = True
            cur.execute("select 1 from Usuario where email='"+email+"'")
            if cur.fetchone() is not None:
                ok += 1
                body["email"] = False
            else:
                body["email"] = True
            conn.commit()
            if ok == 0:
                cur.execute("insert into Usuario(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion) values('"+nombreUsuario+"','"+nombreCompleto+"','"+email+"','"+contrasenya+"','"+fraseRecuperacion+"')")
                conn.commit()
                cur.execute("select id from Usuario where nombreUsuario=%s",nombreUsuario)
                conn.commit()
                body["id"] = cur.fetchone()[0]
                body["redirectPage"] = urlbase+"misvideos.html"

    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def recuperarContrasenya(user,nuevaContrasenya,fraseRecuperacion):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("select id,fraseRecuperacion from Usuario "+
                        "where nombreUsuario='"+user+"' or email='"+user+"'")
            conn.commit()
            row = cur.fetchone()
            if row is not None:
                body["usuario"] = True
                if fraseRecuperacion.casefold() == row[1].casefold():
                    cur.execute("update Usuario set contrasenya='"+nuevaContrasenya+"' where id="+str(row[0]))
                    conn.commit()
                    body["fraseRecuperacion"] = True
                    body["id"] = row[0]
                    body["redirectPage"] = urlbase+"misvideos.html"
                else:
                    body["fraseRecuperacion"] = False
            else:
                body["usuario"] = False

    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def cambiarContrasenya(id,nuevaContrasenya):
    print(id+" quiere cambiar su contraseña a "+nuevaContrasenya)
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("update Usuario set contrasenya='"+nuevaContrasenya+"' where id="+str(id))
            conn.commit()
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def banear(user):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("update Usuario set habilitado=FALSE where nombreUsuario='"+user+"' or email='"+user+"'")
            conn.commit()
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def buscarVideos(busqueda,tags,limit):
    busqueda = busqueda.strip()
    print("'%"+busqueda+"%'")
    conn = connect()
    body = {}
    tagsOpcionales = busqueda.split()
    if busqueda != "":
        condicionBusqueda = "v.nombre like '%"+busqueda+"%'"
        condicionTagsOpcionales = "t.tag in ("+str(tagsOpcionales)[1:-1]+")"
    else:
        condicionBusqueda = "true"
        condicionTagsOpcionales = "false"

    try:
        with conn.cursor() as cur:
            if len(tags) > 0:
                sql = "select distinct v.id,u.id,v.nombre,u.nombreUsuario,v.fechaSubida from Video v join Usuario u on v.usuarioId = u.id left join Video_Tags t on v.id = t.videoId where ("+condicionBusqueda+" or "+condicionTagsOpcionales+") and t.tag in ("+str(tags)[1:-1]+") order by v.fechaSubida desc limit "+str(limit)
            else:
                sql = "select distinct v.id,u.id,v.nombre,u.nombreUsuario,v.fechaSubida from Video v join Usuario u on v.usuarioId = u.id left join Video_Tags t on v.id = t.videoId where "+condicionBusqueda+" or "+condicionTagsOpcionales+" order by v.fechaSubida desc limit "+str(limit)
            print(sql)
            cur.execute(sql)
            conn.commit()
            body["videos"] = []
            for video in cur.fetchall():
                print(video)
                body["videos"].append({
                    "id": video[0],
                    "usuarioId": video[1],
                    "nombre": video[2],
                    "nombreUsuario": video[3],
                    "fechaSubida": video[4].strftime("%m/%d/%Y, %H:%M:%S"),
                    "tags": tagsDeVideo(conn,video[0])
                    })

    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }
#-------------------------------

# FUNCIONES DE misvideos.html

def misVideos(usuarioId):
    conn = connect()
    body = {}
    print("here we go again...")
    try:
        with conn.cursor() as cur:
            cur.execute("select id,nombre,fechaSubida,rutaAWSMiniatura from Video where usuarioId="+str(usuarioId)+" order by fechaSubida desc")
            conn.commit()
            print("oh that was really cool")
            body["videos"] = []
            for video in cur.fetchall():
                body["videos"].append(
                    {
                        "id": video[0],
                        "nombre": video[1],
                        "fechaSubida": video[2].strftime("%m/%d/%Y, %H:%M:%S"),
                        "imagen": video[3],
                        "tags": tagsDeVideo(conn,video[0])
                    }
                )
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def subir():
    stringToSign= b""
    stringToSign=base64.b64encode(bytes((policy).encode("utf-8")))


    signing_key = getSignatureKey(secret_key, dateStamp, region, service)
    signature = hmac.new(signing_key, stringToSign, hashlib.sha256).hexdigest()

    #print(dateStamp)
    #print(signature)
    print(policy)
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body':json.dumps({'stringSigned' :  signature , 'stringToSign' : stringToSign.decode('utf-8') , 'xAmzCredential' : access_key+"/"+dateStamp+"/"+region+ "/s3/aws4_request" , 'dateStamp' : dateStamp , 'amzDate' : amzDate , 'securityToken' : securityToken })
    }

def nuevoVideo(usuarioId,rutaAWS,nombre,descripcion,tags):
    conn = connect()
    body = {}
    print(tags)
    try:
        with conn.cursor() as cur:
            sql = "insert into Video(usuarioId,rutaAWS,nombre,descripcion) values("+str(usuarioId)+",'"+rutaAWS+"','"+nombre+"','"+descripcion+"')"
            print(sql)
            cur.execute(sql)
            conn.commit()
            cur.execute("select id from Video order by id desc limit 1")
            conn.commit()
            row = cur.fetchone()
            if (row is not None):
                body["id"] = row[0]
                for tag in tags:
                    sql = "insert into Video_Tags values("+str(body["id"])+",'"+tag+"')"
                    print(sql)
                    cur.execute(sql)
            body["redirectPage"] = urlbase+"video.html"
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }
#-------------------------------

# FUNCIONES DE video.html

def video(id):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("select u.id,v.nombre,u.nombreUsuario,v.descripcion,v.rutaAWS,v.fechaSubida,v.ultimaModificacion "+
                        "from Video v join Usuario u on u.id = v.usuarioId "+
                        "where v.id = "+str(id))
            conn.commit()
            row = cur.fetchone()
            body["video"] = {
                "usuarioId": row[0],
                "nombreVideo": row[1],
                "nombreUsuario": row[2],
                "descripcion": row[3],
                "rutaAWS": row[4],
                "fechaSubida": row[5].strftime("%m/%d/%Y, %H:%M:%S"),
                "ultimaModificacion": row[6].strftime("%m/%d/%Y, %H:%M:%S"),
                "tags": tagsDeVideo(conn,id),
                "votosPositivos": votosPositivos(conn,id),
                "votosNegativos": votosNegativos(conn,id),
                "comentarios": comentarios(conn,id)
            }
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def editarVideo(id,nombre,descripcion):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("update Video set nombre='"+nombre+"', descripcion='"+descripcion+"' where id="+id)
            conn.commit()
            if (cur.fetchone() == 1):
                body["redirectPage"] = urlbase+"video.html"
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def comentar(usuarioId,videoId,contenido,comentarioPadreId):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            if comentarioPadreId != -1:
                cur.execute("insert into Comentario(usuarioId,videoId,contenido,comentarioPadreId) values("+str(usuarioId)+","+str(videoId)+",'"+contenido+"',"+str(comentarioPadreId)+")")
            else:
                cur.execute("insert into Comentario(usuarioId,videoId,contenido) values("+str(usuarioId)+","+str(videoId)+",'"+contenido+"')")
            conn.commit()
            cur.execute("select id from Comentario order by id desc limit 1")
            conn.commit()
            row = cur.fetchone()
            if (row is not None):
                body["id"] = row[0]
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def votar(usuarioId,videoId,valor):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("select 1 from Voto where usuarioId="+str(usuarioId)+" and videoId="+str(videoId))
            conn.commit()
            row = cur.fetchone()
            print(row)
            if (row is None):
                
                cur.execute("insert into Voto(usuarioId,videoId,valor) values("+str(usuarioId)+","+str(videoId)+","+str(valor)+")")
                conn.commit()
                cur.execute("select id from Voto order by id desc limit 1")
                conn.commit()
                row = cur.fetchone()
                print(row)
                if (row is not None):
                    body["id"] = row[0]
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin' : '*' },
            'body' : json.dumps(body)
        }
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

#-------------------------------------

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


def lambda_handler(event , context):
    op=event["queryStringParameters"]["op"]

    if op == "inicio":
        return inicio()
    if op == "login":
        usuario = event["queryStringParameters"]["usuario"]
        contrasenya = event["queryStringParameters"]["contrasenya"]
        return login(usuario,contrasenya)
    if op == "registarse":
        nombreUsuario = event["queryStringParameters"]["nombreUsuario"]
        email = event["queryStringParameters"]["email"]
        nombreCompleto = event["queryStringParameters"]["nombreCompleto"]
        contrasenya = event["queryStringParameters"]["contrasenya"]
        fraseRecuperacion = event["queryStringParameters"]["fraseRecuperacion"]
        return registrarse(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion)
    if op == "recuperarContrasenya":
        user = event["queryStringParameters"]["usuario"]
        nuevaContrasenya = event["queryStringParameters"]["nuevaContrasenya"]
        fraseRecuperacion = event["queryStringParameters"]["fraseRecuperacion"]
        recuperarContrasenya(user,nuevaContrasenya,fraseRecuperacion)
    if op == "cambiarContrasenya":
        id = event["queryStringParameters"]["id"]
        nuevaContrasenya = event["queryStringParameters"]["nuevaContrasenya"]
        cambiarContrasenya(id,nuevaContrasenya)
    if op == "banear":
        user = event["queryStringParameters"]["user"]
        return banear(user)
    if op == "buscarVideos":
        busqueda = event["queryStringParameters"]["busqueda"]
        tags = event["queryStringParameters"]["tags"].split()
        #limit = event["queryStringParameters"]["limit"]
        return buscarVideos(busqueda,tags,30)
    if op == "misvideos":
        id = event["queryStringParameters"]["usuarioId"]
        return misVideos(id)
    if op == "subir":
        return subir()
    if op == "nuevoVideo":
        usuarioId = event["queryStringParameters"]["usuarioId"]
        rutaAWS = event["queryStringParameters"]["rutaAWS"]
        nombre = event["queryStringParameters"]["nombre"]
        descripcion = event["queryStringParameters"]["descripcion"]
        tags = event["queryStringParameters"]["tags"].split()
        return nuevoVideo(usuarioId,rutaAWS,nombre,descripcion,tags)
    if op == "video":
        id = event["queryStringParameters"]["id"]
        return video(id)
    if op == "editarVideo":
        id = event["queryStringParameters"]["videoId"]
        nombre = event["queryStringParameters"]["nombre"]
        descripcion = event["queryStringParameters"]["descripcion"]
        editarVideo(id,nombre,descripcion)
    if op == "comentar":
        usuarioId = event["queryStringParameters"]["usuarioId"]
        videoId = event["queryStringParameters"]["videoId"]
        contenido = event["queryStringParameters"]["contenido"]
        #comentarioPadreId = event["queryStringParameters"]["comentarioPadreId"]
        return comentar(usuarioId,videoId,contenido,-1)
    if op == "votar":
        usuarioId = event["queryStringParameters"]["usuarioId"]
        videoId = event["queryStringParameters"]["videoId"]
        valor = event["queryStringParameters"]["valor"]
        votar(usuarioId,videoId,valor)
    return {
        'statusCode': 500,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps({ "redirectPage": urlbase+"error.html" })
    }
#
# PARA PROBARLO EJECUTE ESTA FUNCION EN PYTHON3: exec(open("utadtube_lambda.py").read())
