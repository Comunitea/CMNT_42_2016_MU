#!/bin/bash


# ------------------------------------------------------------------------------
# Opciones editables
# ------------------------------------------------------------------------------

#
# Destino de las copias
#
DIRECTORIO_DESTINO="/home/backups/openerp"
[ -d $DIRECTORIO_DESTINO ] || mkdir ${DIRECTORIO_DESTINO}

# Días a conservar las copias de seguridad. Las copias más viejas se borrarán
DIAS_A_CONSERVAR_COPIAS=40

# Afijo fecha (cadena variable en función de la fecha a incluir en el nombre de los archivos)
AFIJO_FECHA=`date "+%F-%H%M%S"`
# Prefijo de las copias de seguridad
PREFIJO_ARCHIVO_BACKUP="backup-openerp"

# ------------------------------------------------------------------------------
# Cuerpo del script
# ------------------------------------------------------------------------------

# Copia de seguridad de la base de datos
sudo -u postgres nice pg_dumpall | nice gzip > $DIRECTORIO_DESTINO/${PREFIJO_ARCHIVO_BACKUP}.postgres_dumpall.$AFIJO_FECHA.sql.gz

# Copia de seguridad de los programas y configuracion
nice tar zcf $DIRECTORIO_DESTINO/${PREFIJO_ARCHIVO_BACKUP}.openerp.$AFIJO_FECHA.tgz /opt/openerp /etc/openerp-* /etc/init.d/openerp-* 2>&1 | grep -v "tar: Eliminando la"

# Borrar archivos antiguos
find ${DIRECTORIO_DESTINO}/* -maxdepth 0 -name "${PREFIJO_ARCHIVO_BACKUP}*" -mtime +$DIAS_A_CONSERVAR_COPIAS -delete




