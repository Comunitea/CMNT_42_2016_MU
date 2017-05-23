# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Omar Castiñeira Savedra (http://www.pexego.es)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields


class payment_type_face_code(osv.osv):

    _name = "payment.type.face.code"

    _columns = {
        "code": fields.char("Code", size=2, required=True),
        "name": fields.char("Name", size=128, required=True)
    }

payment_type_face_code()


class payment_type(osv.osv):

    _inherit = "payment.type"

    _columns = {
        'related_bank_account_id': fields.many2one("res.partner.bank", "Related bank account", help="Company bank account if it is set in paynment name"),
        'face_code_id': fields.many2one("payment.type.face.code", "FACe code")
    }

payment_type()
