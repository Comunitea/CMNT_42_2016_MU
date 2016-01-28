# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# Personalización base de OpenERP para Mecanizados Unión.
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Mecanizados Unión - Base",
        "version" : "0.2",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
            Personalización base para Mecanizados Unión.

            - Añade columnas de teléfono y fax a empresas.
            - Añade asistente para imprimir cartas a direcciones.
            """,
        "depends" : ['base', 'mail', 'account_financial_report_webkit',
                     'account_financial_report_webkit_xls'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : [
                        'res_partner_view.xml',
                        'res_partner_address_report.xml',
                        ],
        "installable": True
}
