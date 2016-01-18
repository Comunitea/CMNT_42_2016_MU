# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# Personalización de las compras en OpenERP para Mecanizados Unión.
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Mecanizados Unión - Compras",
        "version" : "0.1",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
            Personalización de las compras en OpenERP para Mecanizados Unión.

            - Configura las sequencias (series) de compras/pedidos.
            """,
        "depends" : [ 'base', 'purchase'],
        "init_xml" : [
                        "purchase_sequence.xml"
                    ],
        "demo_xml" : [ ],
        "update_xml" : [  ],
        "installable": True
}
