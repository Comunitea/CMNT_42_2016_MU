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

from osv import osv, fields
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

    _columns = {
        'name': fields.text('Description', required=True)
    }

account_invoice_line()


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if res.get('value', False) and res['value'].get('partner_bank_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', res['value']['partner_bank_id']), ('state', '=', 'valid')])
            res['value']['sdd_mandate_id'] = mandate_ids and mandate_ids[0] or False

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        invoice_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        if vals.get('partner_bank_id', False) and not vals.get('sdd_mandate_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', vals['partner_bank_id']), ('state', '=', 'valid')])
            if mandate_ids:
                self.write(cr, uid, [invoice_id], {
                    'sdd_mandate_id': mandate_ids[0]
                })

        return invoice_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.get('partner_bank_id', False) and not vals.get('sdd_mandate_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', vals['partner_bank_id']), ('state', '=', 'valid')])
            if mandate_ids:
                vals['sdd_mandate_id'] = mandate_ids[0]
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

    def onchange_partner_bank(self, cr, uid, ids, partner_bank_id=False):
        res = super(account_invoice, self).onchange_partner_bank(cr, uid, ids, partner_bank_id=partner_bank_id)
        if partner_bank_id:
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', partner_bank_id), ('state', '=', 'valid')])
            if mandate_ids:
                res['value']['sdd_mandate_id'] = mandate_ids[0]
            else:
                res['value']['sdd_mandate_id'] = False
            res['value']['partner_bank_id'] = partner_bank_id
        else:
            res['value']['sdd_mandate_id'] = False

        return res
