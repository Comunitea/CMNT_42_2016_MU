#!/bin/bash

DB=demo
USER=admin
PASSWD=union

echo Importando clientes...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/CLIENTES.dbf ignore

echo Importando direcciones de clientes...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/DIRCLI.DBF ignore

echo Importando proveedores...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/PROVEEDO.dbf ignore

echo Importando articulos...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/ARTICULO.dbf ignore

echo Importando cuentas contables...
nice python fplus2oe.py $DB $USER $PASSWD ./ContaEli/EMPA9/SubCta.DBF ignore

echo Importando cuenta contable clientes...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/CLIENTES.dbf ignore account_only

echo Importando cuenta contable proveedores...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/PROVEEDO.dbf ignore account_only

echo Importando cuenta contable articulos...
nice python fplus2oe.py $DB $USER $PASSWD ./FactuE.1/DBF10/ARTICULO.dbf ignore account_only

