# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# Configura los contratos de mantenimiento para reportar directamente a Pexego
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Pexego - Mantenimiento",
        "version" : "0.1",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
Sustituye el comportamiento por defecto de los contratos de mantenimiento,
para permitir siempre envíar reportes de error,
y que estos reportes se envíen directamente a Pexego.

Nota: Requiere un servidor de correo local.
            """,
        "depends" : ['base'],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [],
        "installable": True
}
