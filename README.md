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