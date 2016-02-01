# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# Personalización de la contabilidad de OpenERP para Mecanizados Unión.
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Mecanizados Unión - Contabilidad",
        "version" : "0.2",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
            Personalización de la contabilidad de OpenERP para Mecanizados Unión.

            - Muestra el campo Origen (pedido/albarán), de las líneas de detalle de la factura, en la vista formulario de factura.
            - Extiende las órdenes de pago para permitir volver a borrador una orden confirmada.
            - Añade la cantidad pendiente de pago a la vista de efectos a pagar/cobrar.
            - Añade menús de facturas del año actual.
            - Personaliza las vistas de factura y factura de proveedor.
            """,
        "depends" : [ 'base', 'account', 'account_payment_extension',
                     'account_payment_sepa_direct_debit'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : [
                        'account_invoice_view.xml',
                        'payment_view.xml',
                        'account_invoice_menus.xml'
                        ],
        "installable": True
}
