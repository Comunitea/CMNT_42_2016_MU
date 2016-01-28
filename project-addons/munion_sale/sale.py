# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Pexego Sistemas Informáticos. All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
Extensión del objeto de ventas (pedidos) para establecer
ciertas opciones por defecto, y para simplificar el flujo de venta
(se ejecutan automáticamente los procurements de servicios).
"""
__author__ = "Borja López Soilán (Pexego)"

from osv import osv, fields
import netsvc
import re

class sale_order(osv.osv):
    """
    Extensión del objeto de ventas (pedidos) para establecer
    ciertas opciones por defecto, y para simplificar el flujo de venta
    (se ejecutan automáticamente los procurements de servicios).
    """
    _inherit = "sale.order"
    _order = "date_order desc"

    #
    # Modificamos los valores por defecto
    #
    _defaults = {
        'order_policy': lambda *a: 'manual',
        'invoice_quantity': lambda *a: 'order',
    }


    def action_ship_create(self, cr, uid, ids, *args):
        """
        Sobreescribe action_ship_create para que los servicios se marquen
        automáticamente como abastecidos
        (tras delegar el el action_ship_create original).
        """
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)

        for order in self.browse(cr, uid, ids):
            for line in order.order_line:
                if line.product_id and line.product_id.product_tmpl_id.type=='service' and line.procurement_id and line.state == 'confirmed':
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'mrp.procurement', line.procurement_id.id, 'button_check', cr)
        return result
sale_order()



class sale_order_line(osv.osv):
    """
    Extensión del objeto línea de venta (pedidos) para establecer
    ciertas opciones por defecto.
    """
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        """
        Sobreescribe product_id_change para:
            - Eliminar el código del producto de la descripción automática.
            - Establecer el descuento del producto por defecto según el cliente.
        """

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)

        #
        # Eliminar el código del producto de la descripción automática.
        #
        if len(result.get('value', {}).get('name', '')):
            result['value']['name'] = re.sub('^\[.*?\]\s', '', result['value']['name'])

        #
        # Establecer el descuento del producto por defecto según el cliente.
        #
        partner_obj = self.pool.get('res.partner')
        if partner_id:
            result['value']['discount'] = partner_obj.browse(cr, uid, partner_id).sale_discount

        return result

    _columns = {
        'name': fields.text('Order Reference', required=True, select=True,
            readonly=True, states={'draft': [('readonly', False)]})
     }

sale_order_line()


class sale_shop(osv.osv):

    _inherit = "sale.shop"

    _columns = {
        'account_ids': fields.many2many('account.account', 'sale_shop_account',
                                        'shop_id', 'account_id',
                                        string="Cuentas asociadas")
    }

sale_shop()
