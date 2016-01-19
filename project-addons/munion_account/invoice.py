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
Extensión del objeto de facturas para establecer
ciertas opciones por defecto (el orden).
"""
__author__ = "Borja López Soilán (Pexego)"

from osv import osv
import netsvc
import re


class account_invoice_line(osv.osv):
    """
    Extensión del objeto línea de factura para establecer
    ciertas opciones por defecto (IVA por defecto y descuento de cliente).
    """
    _inherit = 'account.invoice.line'

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None):
        """
        Sobreescribe product_id_change para:
            - Establecer el descuento del producto por defecto según el cliente.
        """
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, currency_id, context, company_id)

        #
        # Establecer el descuento del producto por defecto según el cliente.
        # (Sólo en facturas a clientes)
        #
        if type in ('out_invoice', 'out_refund'):
            partner_obj = self.pool.get('res.partner')
            if partner_id:
                result['value']['discount'] = partner_obj.browse(cr, uid, partner_id).sale_discount

        return result

account_invoice_line()
