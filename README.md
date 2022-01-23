# Puesta en marcha

cambiar ip de la ec2 en godaddy

reiniciar mariadb en kubernetes en la ec2:

1. kubectl delete pod mariadb
2. kubectl apply -f mariadb.yaml
2. comprobar si la ip del pod ya esta redireccionada: sudo iptables -t nat -L PREROUTING -n -v
3. en caso de que el pod tenga otra ip: sudo iptables -t nat -A PREROUTING -p tcp --dport 3306 -j DNAT --to-destination 10.32.0.4:3306
4. ejecutar sql en dbeaver

cambiar keys aws en lambda

cambiar keys en php

El servidor apache en la EC2 tiene asignado un certificado SSL por lo que solo se puede acceder a el desde https, además cuenta con un dominio en godaddy así que para acceder a la web el link sería este: https://www.macascript.com

La EC2 tiene, gestionado por kubernetes, un pod mariadb con la base de datos de la página web. El servidor apache está en la propia EC2 no en un pod. El index.html simplemente redirecciona a Inicio.html que reside en la s3. El bucket de s3 tiene 2 carpetas: htmls/ y users/, en users hay una carpeta por usuario que haya subido por lo menos un video y en cada carpeta de usuario están todos sus videos y miniaturas de videos en la raiz.

