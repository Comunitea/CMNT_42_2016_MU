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
Extensión del objeto compañía para establecer
la cabecera de los informes por defecto.
"""
__author__ = "Borja López Soilán (Pexego)"

from osv import osv
import os
import tools

class res_company(osv.osv):
    """
    Extensión del objeto compañía para establecer
    la cabecera de los informes por defecto.
    """
    _inherit = "res.company"

    def _get_header(self,cr,uid,ids):
        try :
            return tools.file_open(os.path.join('munion_sale', 'report', 'corporate_rml_header.rml')).read()
        except:
            return super(res_company, self)._get_header(cr,uid,ids)

    _defaults = {
        'rml_header': _get_header,
    }

res_company()


