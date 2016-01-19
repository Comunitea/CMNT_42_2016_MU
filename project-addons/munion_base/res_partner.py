# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
Extiende las empresas (partner) para añadir campos
específicos de Mecanizados Unión.
"""

from osv import osv, fields, orm

class res_partner(osv.osv):
    """
    Extiende las empresas (partner) para añadir campos nuevos
    (teléfono, fax, móvil).
    """

    _inherit = 'res.partner'

    #
    # Campos del objeto --------------------------------------------------------
    #

    _columns = {
            'fax': fields.related('address', 'fax', type='char', string='Fax'),
     }


res_partner()
