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
Sustituye el comportamiento por defecto de los contratos de mantenimiento,
para permitir siempre envíar reportes de error,
y que estos reportes se envíen directamente a Pexego.
"""

from osv import osv

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

def sendMail(fro, to, subject, text, files=[], server="localhost"):
    """
    Envía un correo usando el servidor especificado (local por defecto).
    """
    assert type(fro)==list
    assert type(to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = COMMASPACE.join(fro)
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()


class maintenance_contract(osv.osv):
    """
    Sustituye el comportamiento por defecto de maintenance_contract, para
    permitir envíar siempre reportes de error, y que estos reportes se
    envíen a Pexego.
    """
    _name = "maintenance.contract"
    _description = "Maintenance Contract"

    def status(self, cr, uid):
        return {
            'status': 'full',
            'uncovered_modules': [],
        }

    def send(self, cr, uid, tb, explanations, remarks=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id

        try:
            message = u"""
Error de OpenERP reportado por %s en %s usando la base de datos %s.

*** EXPLICACION ***

%s


*** COMENTARIOS ***

%s


*** DETALLES ***

%s
                """ % (
                    user.name,
                    company.name,
                    cr.dbname,
                    unicode(explanations, "utf-8"),
                    unicode(remarks, "utf-8"),
                    unicode(tb, "utf-8"))

            message = message.encode('utf-8', 'replace')

            sendMail(
                    ["OpenERP Maintenance <openerp-maintenance@pexego.es>"],
                    ["errores-openerp@pexego.es"],
                    "Reporte de error de OpenERP (%s)" % company.name,
                    message
                )
        except:
            raise
            return False
        return True

maintenance_contract()

