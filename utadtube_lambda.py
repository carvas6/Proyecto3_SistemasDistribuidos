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
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin' : '*' },
        'body' : json.dumps(body)
    }

def registrarse(nombreUsuario,email,nombreCompleto,contrasenya,fraseRecuperacion):
    conn = connect()
    body = {"redirectPage": urlbase+"login.html"}
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
                
                body["redirectPage"] = urlbase+"principal.html"
            else:
                body["redirectPage"] = urlbase+"fallo_login.html"
            
    except pymysql.MySQLError as e:    
        print (e)
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
        user=float(event["queryStringParameters"]["user"])
        password=float(event["queryStringParameters"]["pass"])
        return login()
    if op == "registarse":
        return registrarse()
    if op == "subir":
        return {}
    return {}
#      
