# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# Personalización de las ventas en OpenERP para Mecanizados Unión.
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Mecanizados Unión - Ventas",
        "version" : "0.1",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
            Personalización de las ventas en OpenERP para Mecanizados Unión.

            - Establece opciones por defecto para los pedidos (facturar según pedido, y no generar factura automáticamente sino en el envío).
            - Simplifica el flujo de ventas, aprobando automáticamente los abastecimientos (procurements) de servicios.
            - Crea plazos de pago (10, 15, 45 y 180 días) y tarifas personalizadas (20% y 25% desc.).
            - Establece opciones por defecto para las líneas de pedidos (unidad de medida e IVA predeterminados).
            - Incluye reportes personalizados para ventas y facturas, y para la cabecera de los informes.
            - Configura las sequencias (series) de ventas/pedidos y picking/albaranes.
            - Añade menús de órdenes de venta del año actual.
            """,
        "depends" : [ 'base', 'sale', 'account'],
        "init_xml" : [
                        "default_data.xml",
                        "sale_sequence.xml",
                        "sale_report.xml",
                        "account_report.xml",
                        "res_partner_report.xml"
                    ],
        "demo_xml" : [ ],
        "update_xml" : [
                        'res_partner_view.xml',
                        ],
        "installable": True
}
