En este repositorio el fichero de configuración de buildout es buildout.cfg nos instala postgres dentro del entorno virtual y no lo gestiona bajo supervisor. En este caso es necsario entrar modificar el script para  adecuarlo al postgres al que se debe conectar. ATENCIÓN: Las modificaciones en este sript no deben subirse posteriormente a este repositorio

# Buildout base para proyectos con OpenERP y PostgreSQL
OpenERP master en el base, PostgreSQL 9.3.4 y Supervisord 3.0
- Buildout crea cron para iniciar Supervisord después de reiniciar (esto no lo he probado)
- Supervisor ejecuta PostgreSQL, más info http://supervisord.org/
- También ejecuta la instancia de PostgreSQL
- Si existe un archivo dump.sql, el sistema generará la base de datos con ese dump
- Si existe  un archivo frozen.cfg es el que se debeía usar ya que contiene las revisiones aprobadas
- PostgreSQL se compila y corre bajo el usuario user (no es necesario loguearse como root), se habilita al autentificación "trust" para conexiones locales. Más info en: http://www.postgresql.org/docs/9.3/static/auth-methods.html
- Existen plantillas para los archivo de configuración de Postgres que se pueden modificar para cada proyecto.
 

# Uso
En caso de no haberse hecho antes en la máquina en la que se vaya a realizar, instalar las dependencias que marca Anybox
- Añadir el repo a /etc/apt/sources.list:
```
$ deb http://apt.anybox.fr/openerp common main
```
- Si se quiere añadir la firma. Esta a veces tarda mucho tiempo o incluso da time out. Es opcional meterlo
```
$ sudo apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 0xE38CEB07
```
- Actualizar e instalar
```
$ sudo apt-get update
$ sudo apt-get install openerp-server-system-build-deps
```
- Para poder compilar e instalar postgres (debemos valorar si queremos hacerlo siempre), es necesario instalar el siguiente paquete (no es la solución ideal, debería poder hacerlo el propio buildout, pero de momento queda así)
```
$ sudo apt-get install libreadline-dev
```
- Descargar el  repositorio de buildouts :
```
$ git clone https://github.com/Pexego/Odoo_8_base.git <ubicacion_local_repo>
```
- Crear un virtualenv dentro de la carpeta del respositorio. Esto podría ser opcional, obligatorio para desarrollo o servidor de pruebas, tal vez podríamos no hacerlo para un despliegue en producción. Si no está instalado, instalar el paquete de virtualenv
```
$ sudo apt-get install python-virtualenv
$ cd <ubicacion_local_repo>
$ virtualenv sandbox --no-setuptools
```
- Crear la carpeta eggs (no se crea al vuelo, ¿debería?)
```
$ mkdir eggs
```
- Ahora procedemos a ejecutar el buildout en nuestro entorno virtual
```
$ sandbox/bin/python bootstrap.py -c <configuracion_elegida>
$ bin/buildout -c <configuracion_elegida>
```
- Al terminar dará un error porque no encuentra el postgresql arrancado, tendremos que lanzarlo manualmente.
- Ejecutar Supervisor, encargado de lanzar los servicios postgresql y odoo
```
$ bin/supervisord
```
- Y por último de nuevo:
```
$ bin/buildout -c <configuracion_elegida>
```
- Urls
- Supervisor : http://localhost:9005
- Odoo: http://localhost:9469
      admin//admin

## Configurar OpenERP
Archivo de configuración: etc/openerp.cfg, si sequieren cambiar opciones en  openerp.cfg, no se debe editar el fichero,
si no añadirlas a la sección [openerp] del buildout.cfg
y establecer esas opciones .'add_option' = value, donde 'add_option'  y ejecutar buildout otra vez.

Por ejmplo: cambiar el nivel de logging de OpenERP
```
'buildout.cfg'
...
[openerp]
options.log_handler = [':ERROR']
...
```

Si se quiere ejecutar más de una instancia de OpenERP, se deben cambiar los puertos:
```
openerp_xmlrpc_port = 8069  (8069 default openerp)
openerp_xmlrpcs_port = 8071 (8071 default openerp)
supervisor_port = 9002      (9001 default supervisord)
postgres_port = 5434        (5432 default postgres)
```

# TODO
- Generar Apache and Nginx config for virualhost with Buildout

# Contributors

Marcos Ybarra - Pharmadus
Pexego

## Creators

Rastislav Kober, http://www.kybi.sk

