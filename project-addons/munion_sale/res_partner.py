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
Extensión del objeto empresa para:
    - Añadir campos adicionales (descuento de línea por defecto).
    - Ordenar por código en lugar de por nombre
"""
__author__ = "Borja López Soilán (Pexego)"

from osv import fields,osv

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _order = "ref,name"
    _columns = {
        'sale_discount': fields.float("Descuento de venta"),
    }

res_partner()

