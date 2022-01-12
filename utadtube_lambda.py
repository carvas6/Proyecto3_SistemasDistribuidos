import sys
import logging
import pymysql
import json
import os, base64, datetime, hashlib, hmac

urlbase = "http://localhost/"

# Variables de sql
rds_host = "44.200.72.15"

username = "admin"
password ="password"

dbname = "utadtubedb"

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
        return pymysql.connect(rds_host, user=username, passwd=password, db=dbname, connect_timeout=10, port=3306)
    except pymysql.MySQLError as e:
        print (e)
        sys.exit()


def login(user,password):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            ok = cur.execute("select id,nombreUsuario from Usuario where (email="+user+" or nombreUsuario="+user+") and contrasenya="+password)
            conn.commit()
            if ok > 0:
                id = cur.fetchone()[0]
                body["id"] = cur.fetchone()[0]
                body["nombreUsuario"] = cur.fetchone()[1]
                cur.execute("select nombre,descripcion,rutaAWS,fechaSubida,ultimaModificacion from Video where usuarioId="+id+" order by fechaSubida")
                conn.commit()
                body["videos"] = ()
                for video in cur.fetchall():
                    body["videos"].append({
                        "nombre": video[0],
                        "descripcion": video[1],
                        "rutaAWS": video[2],
                        "fechaSubida": video[3],
                        "ultimaModificacion": video[4]
                        })
                body["redirectPage"] = urlbase+"principal.html"
            else:
                body["redirectPage"] = urlbase+"fallo_login.html"
            
    except pymysql.MySQLError as e:    
        print (e)
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
            ok = cur.execute("select id,nombreUsuario from Usuario where nombreUsuario="+nombreUsuario)
            conn.commit()
            if ok > 0:
                body["nombreUsuario"] = False
            else:
                body["nombreUsuario"] = True
            
            
            if cur.execute("select id,nombreUsuario from Usuario where email="+email) > 0:
                ok+=1
                body["email"] = False
            else:
                body["email"] = True
            conn.commit()
            if ok == 0:
                cur.execute("insert into Usuario(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion) values("+nombreUsuario+","+email+","+contrasenya+","+fraseRecuperacion+")")
                conn.commit()
                
                body["redirectPage"] = urlbase+"login.html"
            else:
                body["redirectPage"] = urlbase+"fallo_registro.html"
            
    except pymysql.MySQLError as e:    
        print (e)
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

def nuevoVideo(usuarioId,tamanyo,nombre,descripcion):
    conn = connect()
    body = {}
    try:
        with conn.cursor() as cur:
            cur.execute("insert into Video(usuarioId,tamanyo,nombre,descripcion) values("+usuarioId+","+tamanyo+","+nombre+","+descripcion+")")
            conn.commit()
            ok = cur.execute("select id from Video order by id desc limit 1")
            conn.commit()
            if (ok == 1):
                body["id"] = cur.fetchone()[0]
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
            ok = cur.execute("update Video set nombre="+nombre+", descripcion="+descripcion+" where id="+id)
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
                cur.execute("insert into Comentario(usuarioId,videoId,contenido,comentarioPadreId) values("+usuarioId+","+videoId+","+contenido+","+comentarioPadreId+")")
            else:
                cur.execute("insert into Comentario(usuarioId,videoId,contenido) values("+usuarioId+","+videoId+","+contenido+")")
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

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


def lambda_handler(event , context):
    op=event["queryStringParameters"]["op"]
    
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
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps({ "redirectPage": urlbase+"error.html" })
    }
#      
