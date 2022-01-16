# coding: latin-1
import sys
import logging
import pymysql
import json
import os, base64, datetime, hashlib, hmac

urlbase = "http://localhost/"

# Variables de sql
rds_host = "127.0.0.1"

username = "root"
password = ""

dbname = "macatubedb"

# Variables de S3
access_key = ''
secret_key = ''
securityToken= ''

bucket = ""
bucketUrl = ""
region = 'us-east-1'
service = 's3'

t = datetime.datetime.utcnow()
amzDate = t.strftime('%Y%m%dT%H%M%SZ')
dateStamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

policy = """{"expiration": "2020-12-30T12:00:00.000Z",
"conditions": [
{"bucket": \"""" + bucket +"""\"},
["starts-with", "$key", ""],
{"acl": "public-read"},
{"success_action_redirect": \""""+ bucketUrl+"""success.html"},
    {"x-amz-credential": \""""+ access_key+"/"+dateStamp+"/"+region+"""/s3/aws4_request"},
    {"x-amz-algorithm": "AWS4-HMAC-SHA256"},
    {"x-amz-date": \""""+amzDate+"""\" },
    {"x-amz-security-token": \"""" + securityToken +"""\"  }
  ]
}"""

def connect():
    try:
        return pymysql.connect(host=rds_host, user=username, password=password, database=dbname, connect_timeout=10, port=3306)
    except pymysql.MySQLError as e:
        print (e)
        sys.exit()

def tagsDeVideo(conn,videoId):
    tags = []
    try:
        with conn.cursor() as cur:

            cur.execute("select tag from Video_Tags where videoId = "+videoId)
            conn.commit()
            for tag in cur.fetchall():
                tags.append(tag[0])
    except pymysql.MySQLError as e:
        print (e)
    return tags

# FUNCIONES DE inicio.html

def inicio():
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:

            cur.execute("select v.id,u.id,v.nombre,u.nombreUsuario,fechaSubida from Video v join Usuario u on v.usuarioId = u.id order by fechaSubida desc limit 30")
            conn.commit()
            body["videos"] = []
            for video in cur.fetchall():
                body["videos"].append({
                    "id": video[0],
                    "usuarioId": video[1],
                    "nombre": video[2],
                    "nombreUsuario": video[3],
                    "fechaSubida": video[4].strftime("%m/%d/%Y, %H:%M:%S"),
                    "tags": tagsDeVideo(video[0])
                    })
    except pymysql.MySQLError as e:
        print (e)
        body["redirectPage"] = urlbase+"error.html"
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
            ok = cur.execute("select id,nombreUsuario from Usuario where (email='"+user+"' or nombreUsuario='"+user+"') and contrasenya='"+password+"'")
            conn.commit()
            if ok > 0:
                body["id"] = cur.fetchone()[0]
                body["nombreUsuario"] = cur.fetchone()[1]
                body["redirectPage"] = urlbase+"misvideos.html"

    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
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
            print("select 1 from Usuario where nombreUsuario='"+nombreUsuario+"'")
            ok = cur.execute("select 1 from Usuario where nombreUsuario='"+nombreUsuario+"'")
            print(ok)
            conn.commit()
            if ok > 0:
                body["nombreUsuario"] = False
            else:
                body["nombreUsuario"] = True

            print("select 1 from Usuario where email='"+email+"'")
            if cur.execute("select 1 from Usuario where email='"+email+"'") > 0:
                ok+=1
                print(ok)
                body["email"] = False
            else:
                body["email"] = True
            conn.commit()
            if ok == 0:
                print("insert into Usuario(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion) values('"+nombreUsuario+"','"+nombreCompleto+"','"+email+"','"+contrasenya+"','"+fraseRecuperacion+"')")
                cur.execute("insert into Usuario(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion) values('"+nombreUsuario+"','"+nombreCompleto+"','"+email+"','"+contrasenya+"','"+fraseRecuperacion+"')")
                conn.commit()
                cur.execute("select id from Usuario where nombreUsuario='"+nombreUsuario+"'")
                conn.commit()
                body["id"] = cur.fetchone()[0]
                body["redirectPage"] = urlbase+"misvideos.html"

    except pymysql.MySQLError as e:
        print (e)
        body["redirectPage"] = urlbase+"error.html"
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def buscarVideos(busqueda,tags,limit):
    conn = connect()
    body = {}
    tagsOpcionales = busqueda.split()
    try:
        with conn.cursor() as cur:
            if len(tags) > 0:
                cur.execute("select v.id,u.id,v.nombre,u.nombreUsuario,v.fechaSubida "+
                            "from Video v join Usuario u on v.usuarioId = u.id join Video_Tags t on v.id = t.videoId "+
                            "where (v.nombre like '%"+busqueda+"%' or t.tag in ("+str(tagsOpcionales)[1:-1]+")) and t.tag in ("+str(tags)[1:-1]+") "+
                            "order by v.fechaSubida desc limit "+limit)
            else:
                cur.execute("select v.id,u.id,v.nombre,u.nombreUsuario,v.fechaSubida "+
                            "from Video v join Usuario u on v.usuarioId = u.id "+
                            "where v.nombre like '%"+busqueda+"%' or t.tag in ("+str(tagsOpcionales)[1:-1]+") " +
                            "order by v.fechaSubida desc limit "+limit)
            conn.commit()
            for video in cur.fetchall():
                body["videos"].append({
                    "id": video[0],
                    "usuarioId": video[1],
                    "nombre": video[2],
                    "nombreUsuario": video[3],
                    "fechaSubida": video[4],
                    "tags": tagsDeVideo(video[0])
                    })

    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
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
    try:
        with conn.cursor() as cur:
            cur.execute("select id,nombre,fechaSubida from Video where usuarioId="+body["id"]+" order by fechaSubida")
            conn.commit()
            for video in cur.fetchall():
                body["videos"].append(
                    {
                        "id": video[0],
                        "nombre": video[0],
                        "fechaSubida": video[3],
                        "tags": tagsDeVideo(video[0])
                    }
                )
    except pymysql.MySQLError as e:
        print(e)
        body["redirectPage"] = urlbase+"error.html"
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
        'body':json.dumps({ 'stringSigned' :  signature , 'stringToSign' : stringToSign.decode('utf-8') , 'xAmzCredential' : access_key+"/"+dateStamp+"/"+region+ "/s3/aws4_request" , 'dateStamp' : dateStamp , 'amzDate' : amzDate , 'securityToken' : securityToken })
    }

def nuevoVideo(usuarioId,tamanyo,rutaAWS,nombre,descripcion,tags):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("insert into Video(usuarioId,tamanyo,rutaAWS,nombre,descripcion) values("+usuarioId+","+tamanyo+",'"+rutaAWS+",'"+nombre+"','"+descripcion+"')")
            conn.commit()
            ok = cur.execute("select id from Video order by id desc limit 1")
            conn.commit()
            if (ok == 1):
                body["id"] = cur.fetchone()[0]
                for tag in tags:
                    cur.execute("insert into Video_Tags values("+body["id"]+","+tag+")")
            body["redirectPage"] = urlbase+"video.html"
    except pymysql.MySQLError as e:
        print (e)
        body["redirectPage"] = urlbase+"error.html"
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
            ok = cur.execute("update Video set nombre='"+nombre+"', descripcion='"+descripcion+"' where id="+id)
            conn.commit()
            if (ok == 1):
                body["redirectPage"] = urlbase+"video.html"
    except pymysql.MySQLError as e:
        print (e)
        body["redirectPage"] = urlbase+"error.html"
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
                cur.execute("insert into Comentario(usuarioId,videoId,contenido,comentarioPadreId) values("+usuarioId+","+videoId+",'"+contenido+"',"+comentarioPadreId+")")
            else:
                cur.execute("insert into Comentario(usuarioId,videoId,contenido) values("+usuarioId+","+videoId+",'"+contenido+"')")
            conn.commit()
            ok = cur.execute("select id from Comentario order by id desc limit 1")
            conn.commit()
            if (ok == 1):
                body["id"] = cur.fetchone()[0]
    except pymysql.MySQLError as e:
        print (e)
        body["redirectPage"] = urlbase+"error.html"
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serv'%"+busqueda+"%'iceName):
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
        contrasenya = event["queryStringParameters"]'%"+busqueda+"%'"contrasenya"]
        fraseRecuperacion = event["queryStringParameters"]["fraseRecuperacion"]
        return registrarse(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion)
    if op == "buscarVideos":
        busqueda = event["queryStringParameters"]["busqueda"]
        tags = json.loads(event["queryStringParameters"]["tags"])
        limit = event["queryStringParameters"]["limit"]
        return buscarVideos(busqueda,tags,limit)
    if op == "misvideos":
        id = event["queryStringParameters"]["usuarioId"]
        return misVideos(id)
    if op == "subir":
        return subir()
    if op == "nuevoVideo":
        usuarioId = event["queryStringParameters"]["usuarioId"]
        tamanyo = event["queryStringParameters"]["tamanyo"]
        nombre = event["queryStringParameters"]["nombre"]
        descripcion = event["queryStringParameters"]["descripcion"]
        return nuevoVideo(usuarioId,tamanyo,nombre,descripcion)
    if op == "comentar":
        usuarioId = event["queryStringParameters"]["usuarioId"]
        videoId = event["queryStringParameters"]["videoId"]
        contenido = event["queryStringParameters"]["contenido"]
        comentarioPadreId = event["queryStringParameters"]["comentarioPadreId"]
        return comentar(usuarioId,videoId,contenido,comentarioPadreId)
    return {'%"+busqueda+"%'
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps({ "redirectPage": urlbase+"error.html" })
    }
#
#response = inicio()
#print(response)
#print(response)
#response = registrarse("Macascript","jotaele.arrojo@gmail.com","Jose Luis Arrojo Abela","1234","¿Cual es tu color favorito?")
buscarVideos("",["patata"],30)
