# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP - Account balance reporting engine
#    Copyright (C) 2009 Pexego Sistemas Informáticos. All Rights Reserved
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
Account balance report print wizard
"""
__author__ = "Borja López Soilán (Pexego)"


import wizard
import pooler


class wizard_print_letter(wizard.interface):
    """
    Account balance report print wizard.
    Allows the user to select which 'balance report' will be printed,
    and which printing template will be used. By default the current
    balance report and its template printing design will be used.
    """

    init_fields = {
        'letter_text' : {'type': 'text', 'required': False},
    }


    init_form = """<?xml version="1.0" encoding="utf-8"?>
    <form string="Impresión de cartas" colspan="4">
        <label string="Por favor, introduzca el texto de la carta:"/>
        <newline/>
        <field name="letter_text" nolabel="1" colspan="4"/>
    </form>"""


    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch': init_form, 'fields': init_fields, 'state':[('end','Cancelar'),('print','Imprimir')]}
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report': 'res.partner.address.letter', 'state':'end'}
        }
    }
wizard_print_letter('munion_base.print_letter_wizard')

