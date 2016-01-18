# -*- coding: utf-8 -*-
"""
Módulo para la importación simple de datos de FacturaPlus a OpenERP.

Por ahora sólo importa los archivos/tablas CLIENTES.DBF, DIRCLI.DBF 
    y ARTICULO.DBF de FacturaPlus (formato dBASE IV / FoxPro;
    se usa Ydbf como motor de acceso a los archivos dBASE)
    
Uso: fplus2oe.py <empresa> <usuario> <pass> <archivo>
    Donde <empresa> es la empresa OpenERP donde se importarán los datos;
    <usuario> y <pass> es la información de autenticación en OpenERP;
    y <archivo> es el archivo/tabla a importar, 
    por ejemplo "FacturaPlus/DBF01/CLIENTES.dbf".
    
Nota: La importación es estremadamente simple y no contempla todas las columnas
de FacturaPlus, sino que muchos campos tomarán valores predefinidos en el código
(hardcoded). Así que este código deberá ser refactorizado para adaptarlo
a las necesidades de cada empresa.

En el código se definen algunas constantes para parametrizar la importación.
"""

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# - MAPEOS CONFIGURABLES -------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

#
# Mapeo de tipos de IVA de FacturaPlus a sus nombres (name) en OpenERP
#
SALE_TAXES = { 'G': 'IVA 16%', 'R': 'IVA 7%', '0': '' }
SUPPLIER_TAXES = { 'G': '16% IVA Soportado (operaciones corrientes)', 'R': '7% IVA Soportado (operaciones corrientes)', '0': '' }

#
# Cuentas contables por defecto para los clientes
#
DEFAULT_CLIENT_RECEIVABLE_ACCOUNT =     '430000'
DEFAULT_CLIENT_PAYABLE_ACCOUNT =        '410000'
DEFAULT_SUPPLIER_RECEIVABLE_ACCOUNT =   '430000'
DEFAULT_SUPPLIER_PAYABLE_ACCOUNT =      '400000'

#
# Mapeo de descuentos especiales (NDTO, NDTOESP) de FacturaPlus a Tarifas de OpenERP
# PRICELIST_MAPPING[tipo][NDTO][NDTOESP] => product_pricelist.name
#
DEF_SALE_PL = 'Public Pricelist'
DEF_PURCH_PL = 'Public Pricelist'
#PRICELIST_MAPPING = {
#    'sale': {
#        0: { 0.0: DEF_SALE_PL, },
#        1: { 0.0: DEF_SALE_PL, 20.0: u'20% descuento', 25.0: u'25% descuento', },
#        6: { 0.0: DEF_SALE_PL, 20.0: u'20% descuento', 25.0: u'25% descuento', },
#    },
#    'purchase': {
#        0: { 0.0: DEF_PURCH_PL, },
#        1: { 0.0: DEF_PURCH_PL, 20.0: DEF_PURCH_PL, 25.0: DEF_PURCH_PL, },
#        6: { 0.0: DEF_PURCH_PL, 20.0: DEF_PURCH_PL, 25.0: DEF_PURCH_PL, },
#    },
#}
PRICELIST_MAPPING = {
    'sale': {
        0: { 0.0: DEF_SALE_PL, },
        1: { 0.0: DEF_SALE_PL, 20.0: DEF_SALE_PL, 25.0: DEF_SALE_PL, },
        6: { 0.0: DEF_SALE_PL, 20.0: DEF_SALE_PL, 25.0: DEF_SALE_PL, },
    },
    'purchase': {
        0: { 0.0: DEF_PURCH_PL, },
        1: { 0.0: DEF_PURCH_PL, 20.0: DEF_PURCH_PL, 25.0: DEF_PURCH_PL, },
        6: { 0.0: DEF_PURCH_PL, 20.0: DEF_PURCH_PL, 25.0: DEF_PURCH_PL, },
    },
}


#
# Mapeo de Formas de pago de FacturaPlus a Tipos de pago (code) y Plazos de pago (name) de OpenERP
#
#PAYMENT_MAPPING = {
#    # 'CCODPAGO FacturaPlus': ('payment_term.code', 'payment_type.name'),
#    '@T': ('TARJETA',       u'0 días'),         # Tarjeta de crédito
#    '@C': ('EFECTIVO',      u'0 días'),         # Cobtrareembolso - Entrega
#    'CO': ('EFECTIVO',      u'0 días'),         # Contado
#    '01': ('RECIBO_CSB',    u'0 días'),         # Giro a la vista
#    '02': ('RECIBO_CSB',    u'30 días'),        # Giro a 30 días
#    '03': ('RECIBO_CSB',    u'60 días'),        # Giro a 60 días
#    '04': ('RECIBO_CSB',    u'90 días'),        # Giro a 90 días
#    '05': ('PAGARE',        u'15 días'),        # Pagare o cheque
#    '06': ('TRANSF',        u'15 días'),        # Ingreso bancario
#    '07': ('RECIBO_CSB',    u'45 días'),        # Giro 45 días
#    '08': ('CHEQUE',        u'10 días'),         # Reposición
#    '09': ('EFECTIVO',      u'0 días'),         # Contrareembolso
#    '10': ('TRANSF',        u'0 días'),         # Ingreso bancario día factura
#    '11': ('RECIBO_CSB',    u'30/60/90 días'),  # 30-60-90 días
#    '12': ('CHEQUE',        u'30 días'),        # Cheque o pagare
#    '13': ('PAGARE',        u'0 días'),         # Pagare o cheque
#    '14': ('RECIBO_CSB',    u'15 días'),        # Giro a 15 días
#    '15': ('RECIBO_CSB',    u'0 días'),         # Giro de prov.
#    '16': ('RECIBO_CSB',    u'30/60 días'),     # Giro a 30-60 días
#    '17': ('CHEQUE',        u'10 días'),         # Reposición o cheque
#    '18': ('PAGARE',        u'90 días'),        # Pagare a 90 días
#    '19': ('RECIBO_CSB',    u'180 días'),       # Giro a 180 días
#    '20': ('TRANSF',        u'180 días'),       # Ingreso bancario 180 días
#}
PAYMENT_MAPPING = {
    # 'CCODPAGO FacturaPlus': ('payment_term.code', 'payment_type.name'),
    '@T': ('TARJETA',       u'CONTADO'),         # Tarjeta de crédito
    '@C': ('EFECTIVO',      u'CONTADO'),         # Cobtrareembolso - Entrega
    'CO': ('EFECTIVO',      u'CONTADO'),         # Contado
    '01': ('RECIBO_CSB',    u'GIRO A LA VISTA'),         # Giro a la vista
    '02': ('RECIBO_CSB',    u'GIRO 30 DIAS'),   # Giro a 30 días
    '03': ('RECIBO_CSB',    u'GIRO A 60 DIAS'),        # Giro a 60 días
    '04': ('RECIBO_CSB',    u'GIRO A 90 DIAS'),        # Giro a 90 días
    '05': ('PAGARE',        u'15 días'),        # Pagare o cheque
    '06': ('TRANSF',        u'INGRESO BANCARIO'),        # Ingreso bancario
    '07': ('RECIBO_CSB',    u'45 días'),        # Giro 45 días
    '08': ('REPOSICION',    u'REPOSICION '),        # Reposición
    '09': ('EFECTIVO',      u'CONTADO'),         # Contrareembolso
    '10': ('TRANSF',        u'INGRESO BANCARIO'), # Ingreso bancario día factura
    '11': ('RECIBO_CSB',    u'30/60/90 días'),  # 30-60-90 días
    '12': ('CHEQUE',        u'30 días'),        # Cheque o pagare
    '13': ('PAGARE',        u'PAGARE O CHEQUE'), # Pagare o cheque
    '14': ('RECIBO_CSB',    u'15 días'),        # Giro a 15 días
    '15': ('RECIBO_CSB',    u'CONTADO'),         # Giro de prov.
    '16': ('RECIBO_CSB',    u'30/60 días'),     # Giro a 30-60 días
    '17': ('CHEQUE',        u'10 días'),        # Reposición o cheque
    '18': ('PAGARE',        u'PAGARE A 90 DIAS'),        # Pagare a 90 días
    '19': ('RECIBO_CSB',    u'180 días'),       # Giro a 180 días
    '20': ('TRANSF',        u'180 días'),       # Ingreso bancario 180 días
}

#
# Mapeo de (prefijos de) códigos de subcuenta a tipos de cuenta
#
ACCOUNT_INTERNAL_TYPE_MAPPING = {
    '43': 'receivable', '44': 'receivable', '470': 'receivable',
    '40': 'payable', '41': 'payable', '475': 'payable',
    '0': 'other',
    '1': 'other',
    '2': 'other',
    '3': 'other',
    '4': 'other',
    '5': 'other',
    '6': 'other',
    '7': 'other',
    '8': 'other',
    '9': 'other',
}
ACCOUNT_USER_TYPE_MAPPING = {
    '43': 'terceros - rec',
    '44': 'terceros - rec',
    '470': 'impuestos',
    '475': 'impuestos',
    '40': 'terceros - pay',
    '41': 'terceros - pay',
    '460': 'terceros - rec',
    '465': 'terceros - pay', 
    '485': 'terceros - rec',
    '499': 'terceros - pay',
    '0': 'view',
    '1': 'capital',
    '2': 'inmo',
    '3': 'stock',
    '4': 'terceros',
    '5': 'financieras',
    '6': 'gastos',
    '7': 'ingresos',
    '8': 'gastos',
    '9': 'ingresos',
}

#
# Cuentas contables cuyas subcuentas son conciliables.
#
ACCOUNTS_TO_CONCILE = ('40', '41', '43', '44', '47', '520', '529',)

# Plantilla base del plan de cuentas a usar
ACCOUNT_BASE_TEMPLATE = "PGCE PYMES"

# Tipo para cuentas vista
ACCOUNT_VIEW_TYPE = 'view'
# Tipo de usuario para cuentas vista
ACCOUNT_VIEW_USER_TYPE = 'view'

# Código del diario en el que realizar las importaciones
ACCOUNT_MOVE_JOURNAL = 'GRAL'

#
# Descripciones para los asientos de importación
#
ACCOUNT_MOVE_REF = u'Importación ContaPlus'
ACCOUNT_MOVE_LINE_NAME = u'Importación %s'


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# - CODIGO ---------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


import ydbf
import sys
import re
import xmlrpclib
import socket


class CCCHelper:
    """
    Clase auxiliar con métodos para calcular el Código Cuenta Cliente (CCC).
    Basado en http://www.bulma.net/body.phtml?nIdNoticia=1396
    """
    def __init__(self):
        pass

    def _crc(self, data):
        """
        Cálculo del CRC de un número de 10 dígitos
        ajustados con ceros por la izquierda
        """
        factor = (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)
        # Cálculo CRC
        ncrc = 0
        for n in range(10):
            ncrc += int(data[n]) * factor[n]
        # Reducción del CRC a un dígito
        value = 11 - ncrc % 11
        if value == 10:
            value = 1
        elif value == 11:
            value = 0
        return value

    def ccc_control_code(self, bank, agent, account):
        """
        Cálculo del Código de Control Bancario
        """
        data ="00%04d%04d" % (int(bank), int(agent))
        cd1 = self._crc(data)
        data ="%010d" % long(account)
        cd2 = self._crc(data)
        return "%1d%1d" % (cd1, cd2)

    def ccc(self, bank, agent, account):
        """
        Devuelve el Código Cuenta Cliente (CCC) para un banco, sucursal y cuenta
        dados.
        """
        return "%s %s %s %s" % (bank, agent, self.ccc_control_code(bank, agent, account), account)


class RecordImportError(Exception):
    """Error al importar un registro"""
    pass


class AccountNotFoundException(Exception):
    """Cuenta contable no encontrada"""
    pass

class ParentAccountNotFoundException(Exception):
    """Cuenta contable padre no encontrada"""
    pass


class FacturaPlus2OpenERP:
    """
    Importa a OpenERP datos de una base de datos dBASE de FacturaPlus.
    Nota: La importación es muy básica y no tiene en cuenta muchos campos.
    """

    def __init__(self, dbname, user, passwd):
        """
        Inicializar las opciones por defecto y conectar con OpenERP
        """

        self.encoding='iso-8859-1'
        self.on_errors = 'strict'
        self.update_accounts_only = False


    #-------------------------------------------------------------------------
    #--- WRAPPER XMLRPC OPENERP ----------------------------------------------
    #-------------------------------------------------------------------------


        self.url_template = "http://%s:%s/xmlrpc/%s"
        self.server = "localhost"
        self.port = 8069
        self.dbname = dbname
        self.user_name = user
        self.user_passwd = passwd
        self.user_id = 0
 
        #
        # Conectamos con OpenERP
        #
        login_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'common'))
        self.user_id = login_facade.login(self.dbname, self.user_name, self.user_passwd)
        self.object_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'object'))   
        
        
    def create(self, model, data, context=None):
        """
        Wrapper del metodo create.
        """
        if context is None: context = {}
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'create', data, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en create: %s' % (err.faultCode, err.faultString))
        

    def search(self, model, query, context=None):
        """
        Wrapper del metodo search.
        """
        if context is None: context = {}
        try:
            ids = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'search', query, context)
            return ids
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en search: %s' % (err.faultCode, err.faultString))


    def read(self, model, ids, fields, context=None):
        """
        Wrapper del metodo read.
        """
        if context is None: context = {}
        try:
            data = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'read', ids, fields, context)
            return data
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en read: %s' % (err.faultCode, err.faultString))


    def write(self, model, ids, field_values, context=None):
        """
        Wrapper del metodo write.
        """
        if context is None: context = {}
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'write', ids, field_values, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en write: %s' % (err.faultCode, err.faultString))


    def unlink(self, model, ids, context=None):
        """
        Wrapper del metodo unlink.
        """
        if context is None: context = {}
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'unlink', ids, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en unlink: %s' % (err.faultCode, err.faultString))

    def default_get(self, model, fields_list=[], context=None):
        """
        Wrapper del metodo default_get.
        """
        if context is None: context = {}
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'default_get', fields_list, context)
            return res
        except socket.error, err:
            raise Exception('Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception('Error %s en default_get: %s' % (err.faultCode, err.faultString))


    #-------------------------------------------------------------------------
    #--- MÉTODOS AUXILIARES --------------------------------------------------
    #-------------------------------------------------------------------------

    def get_partner_or_address_country_id(self, record, partners_type):
        """
        Busca el id del país en OpenERP,
        dado un registro (cliente/proveedor/dirección) de FacturaPlus
        """
        if record[(partners_type == 'clients') and 'CNACCLI' or 'CNACPRO'] == 'ESPA':
            country_ids = self.search('res.country', [('code', '=', 'ES')])
            if len(country_ids) > 0:
                assert len(country_ids) == 1
                return country_ids[0]
        return False


    def get_partner_or_address_state_id(self, record, partners_type):
        """
        Busca el id de la provincia en OpenERP,
        dado un registro (cliente/proveedor/dirección) de FacturaPlus.
        """
        country_id = self.get_partner_or_address_country_id(record, partners_type)
        if country_id:
            if len(record['CCODPROV']) == 4:
                state_ids = self.search('res.country.state', [('code', '=', record['CCODPROV'][2:]), ('country_id', '=', country_id)])
                if len(state_ids) > 0:
                    assert len(state_ids) == 1
                    return state_ids[0]
        return False


    def get_partner_ccc(self, record):
        """
        Obtiene el Código de Cuenta Cliente,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        if record['CCUENTA']:
            if record['CAGENCIA']:
                return CCCHelper().ccc(record['CENTIDAD'], record['CAGENCIA'], record['CCUENTA'])
            else:
                return record['CCUENTA']
        return False


    def get_partner_bank_id(self, record):
        """
        Obtiene el id del banco,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        bank_ids = self.search('res.bank', [('code', '=', record['CENTIDAD'])])
        if len(bank_ids) > 0:
            return bank_ids[0]
        return False


    def get_partner_bank_country_id(self, record):
        """
        Obtiene el id del país del banco,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        bank_id = self.get_partner_bank_id(record)
        if bank_id:
            data = self.read('res.bank', [bank_id], ['country'])
            # Res: [{'country': (67, u'Espa\xf1a')}]
            return data[0]['country'][0]
        return False


    def get_partner_bank_name(self, record):
        """
        Devuelve el nombre para el banco de un cliente,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        name = record['CNBRBCO']
        if len(record['CDIRBCO']):
            name = "%s, %s" % (name, record['CDIRBCO'])
        if len(record['CDIRBCO']):
            name = "%s, %s" % (name, record['CPOBBCO'])
        return name


    def get_partner_vat(self, record, partners_type):
        """
        Obtiene el vat (NIF/CIF), 
        lo limpia (eliminamos espacios y otros símbolos, añadimos 'ES' al principio si es necesario),
        y hace una comprobación ligera de que sea válido,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        is_client = (partners_type == 'clients')
        nifcif = record[is_client and 'CDNICIF' or 'CNIFDNI']
        nifcif = nifcif.upper().replace("-","").replace(" ","").replace(".","")
        if re.match(r'[A-Z]{3}[0-9]{7}[A-Z]', nifcif) or re.match(r'[A-Z]{2}[0-9]{8}[A-Z]', nifcif):
            return nifcif
        elif re.match(r'[A-Z][0-9]{7}[A-Z0-9]', nifcif) or re.match(r'[0-9]{8}[A-Z]', nifcif):
            return 'ES%s' % nifcif
        elif len(nifcif) == 0:
            return False
        else:
            if self.on_errors == 'ignore':
                print u"WARN: Ignorando el NIF/CIF del cliente!!! (ignorando el error)"
                return False
            else:
                raise RecordImportError(u"NIF/CIF invalido (1): %s (%s)" % (nifcif, record[is_client and 'CDNICIF' or 'CNIFDNI']))


    def get_partner_payment_term_id(self, record):
        """
        Obtiene el plazo de pago del cliente,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        payment_match = PAYMENT_MAPPING.get(record['CCODPAGO'])
        if payment_match:
            payment_term_ids = self.search(u'account.payment.term', [('name', '=', payment_match[1])])
            if len(payment_term_ids):
                return payment_term_ids[0]
            else:
                if self.on_errors == 'ignore':
                    print u"WARN: No se encontro el plazo de pago '%s' asociado a '%s'!!! (ignorando el error)" % (payment_match[1], record['CCODPAGO'])
                else:
                    raise RecordImportError(u"No se encontro el plazo de pago '%s' asociado a '%s'" % (payment_match[1], record['CCODPAGO']))
        else:
            if self.on_errors == 'ignore':
                print u"WARN: Condicion de pago '%s' desconocida (no mapeada)!!! (ignorando el error)" % record['CCODPAGO']
            else:
                raise RecordImportError(u"Condicion de pago desconocida (no mapeada): %s" % record['CCODPAGO'])
        return False


    def get_partner_payment_type_id(self, record):
        """
        Obtiene el tipo de pago del cliente,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        payment_match = PAYMENT_MAPPING.get(record['CCODPAGO'])
        if payment_match:
            payment_type_ids = self.search(u'payment.type', [('code', '=', payment_match[0])])
            if len(payment_type_ids):
                return payment_type_ids[0]
            else:
                if self.on_errors == 'ignore':
                    print u"WARN: No se encontro el tipo de pago '%s' asociado a '%s'!!! (ignorando el error)" % (payment_match[0], record['CCODPAGO'])
                    return False
                else:
                    raise RecordImportError(u"No se encontro el tipo de pago '%s' asociado a '%s'" % (payment_match[0], record['CCODPAGO']))
        else:
            raise RecordImportError(u"Condicion de pago desconocida (no mapeada): %s" % record['CCODPAGO'])
        return False


    def get_partner_pricelist_id(self, record, type, partners_type):
        """
        Obtiene la tarifa del partner,
        dado un registro (cliente/proveedor) de FacturaPlus.
        """
        is_client = (partners_type == 'clients')
        is_supplier = not is_client
        ndto = (is_client and int(record['NDTO'])) or 0
        ndtoesp = (is_client and float(record['NDTOESP'])) or (is_supplier and float(record['NDTO'])) or 0.0
        try:
            pricelist_match = PRICELIST_MAPPING[type][ndto][ndtoesp]
        except:
            raise RecordImportError(u"Tarifa desconocida (no mapeada): %s" % repr((type, ndto, ndtoesp)))
        pricelist_ids = self.search(u'product.pricelist', [('name', '=', pricelist_match)])
        if len(pricelist_ids):
            return pricelist_ids[0]
        else:
            if self.on_errors == 'ignore':
                print u"WARN: No se encontro la tarifa '%s' asociada a '%s'!!! (ignorando el error)" % (pricelist_match, repr((type, ndto, ndtoesp)))
            else:
                raise RecordImportError(u"No se encontro la tarifa '%s' asociada a '%s'" % (pricelist_match, repr((type, ndto, ndtoesp))))
        return False


    def get_product_taxes_id(self, record):
        """
        Obtiene los id de los impuestos (IVA) a usar,
        dado un registro (artículo) de FacturaPlus.
        """
        if record['CTIPOIVA'] in ('G', 'R'): # General o Reducido
            sale_taxes = self.search(u'account.tax', [('name', '=', SALE_TAXES[record['CTIPOIVA']]), ('parent_id', '=', False)])
            return [(6, 0, sale_taxes)]
        elif record['CTIPOIVA'] == '0': # Sin IVA
            return [(6, 0, [])]
        else:
            raise RecordImportError(u"IVA desconocido: %s", record['CTIPOIVA'])


    def get_product_supplier_taxes_id(self, record):
        """
        Obtiene los id de los impuestos (IVA) a usar,
        dado un registro (artículo) de FacturaPlus.
        """
        if record['CTIPOIVA'] in ('G', 'R'): # General o Reducido
            supplier_taxes = self.search(u'account.tax', [('name', '=', SUPPLIER_TAXES[record['CTIPOIVA']]), ('parent_id', '=', False)])
            return [(6, 0, supplier_taxes)]
        elif record['CTIPOIVA'] == '0': # Sin IVA
            return [(6, 0, [])]
        else:
            raise RecordImportError(u"IVA desconocido: %s" % record['CTIPOIVA'])


    def get_account_id_for_account_number(self, account_number):
        """
        Obtiene el id de una cuenta contable dado su número de cuenta ('430000').
        Si no la encuentra lanza una excepción.
        """
        if len(account_number) > 0:
            account_ids = self.search('account.account', [('code', '=', account_number)])
            if account_ids and len(account_ids) > 0:
                return account_ids[0]
            else:
                raise AccountNotFoundException(u"Cuenta contable no encontrada: %s" % account_number)
        return False

    def get_account_id_for_account_number_or_subaccount(self, account_number):
        """
        Obtiene el id de una cuenta contable dado su número de cuenta ('430000').
        Si no la encuentra intenta con una subcuenta acabada en cero,
        y si tampoco la encuentra lanza una excepción.
        """
        if len(account_number) > 0:
            account_ids = self.search('account.account', [('code', '=', account_number)])
            if account_ids and len(account_ids) > 0:
                return account_ids[0]
            else:
                account_ids = self.search('account.account', [('code', '=like', '%s%%0' % account_number)])
                if account_ids and len(account_ids) > 0:
                    return account_ids[0]
                raise AccountNotFoundException(u"Cuenta contable no encontrada: %s" % account_number)
        return False

    def get_account_parent_id(self, account_number):
        """
        Obtiene el id de la cuenta padre que correspondería a una cuenta dada
        según su numeración (ej. '4300001' tendría de padre la cuenta
        con código'4300').
        Si no la encuentra lanza una excepción.
        """
        #
        # Para encontrar el padre, vamos quitándole dígitos a la derecha
        # al número de subcuenta, hasta que coincida con alguna cuenta.
        #
        if len(account_number) > 0:
            parent_account_number = account_number[:-1]
            while len(parent_account_number) > 0:
                account_ids = self.search('account.account', [('code', '=', parent_account_number)])
                if account_ids and len(account_ids) > 0:
                    return account_ids[0]
                parent_account_number = parent_account_number[:-1]
        raise ParentAccountNotFoundException(u"Cuenta contable padre no encontrada para %s" % account_number)


    def get_account_type(self, account_number):
        """
        Devuelve el tipo de cuenta contable según su código.
        """
        tmp_account_number = account_number
        while len(tmp_account_number) > 0:
            type_match = ACCOUNT_INTERNAL_TYPE_MAPPING.get(tmp_account_number)
            if type_match:
                return type_match
            tmp_account_number = tmp_account_number[:-1]
        raise RecordImportError(u"Mapeo de tipo de cuenta desconocido para: %s" % account_number)


    def get_account_user_type_id(self, account_number):
        """
        Devuelve el tipo de usuario de cuenta contable según su código.
        """
        tmp_account_number = account_number
        while len(tmp_account_number) > 0:
            type_match = ACCOUNT_USER_TYPE_MAPPING.get(tmp_account_number)
            if type_match:
                account_user_type_ids = self.search(u'account.account.type', [('code', '=', type_match)])
                if len(account_user_type_ids):
                    return account_user_type_ids[0]
            tmp_account_number = tmp_account_number[:-1]
        raise RecordImportError(u"Mapeo de tipo de cuenta de usuario desconocido para: %s" % account_number)

    def get_account_reconcile(self, account_number):
        """
        Devuelve 1 si la cuenta debe ser reconciliable o 0 si no.
        """
        tmp_account_number = account_number
        while len(tmp_account_number) > 0:
            if tmp_account_number in ACCOUNTS_TO_CONCILE:
                return 1
            tmp_account_number = tmp_account_number[:-1]
        return 0

    def get_account_original_code_from_template(self, account_number):
        """
        Devuelve el código que correspondía originalmente a una cuenta en
        la plantilla de plan contable.
        (OpenERP añade ceros a la derecha de las cuentas hoja)
        """
        tmp_account_number = account_number
        while len(tmp_account_number) > 0:
            account_template_ids = self.search(u'account.account.template', [
                    ('code', '=', tmp_account_number),
                    ('template_name', '=', ACCOUNT_BASE_TEMPLATE)
                ])
            if len(account_template_ids):
                account_template_data = self.read(u'account.account.template', account_template_ids, ['code'])
                return account_template_data[0]['code']
            tmp_account_number = tmp_account_number[:-1]
        return 0

    def get_account_user_type_id_by_code(self, type_code):
        """
        Devuelve el tipo de usuario de cuenta contable según su código.
        """
        account_user_type_ids = self.search(u'account.account.type', [('code', '=', type_code)])
        if len(account_user_type_ids):
            return account_user_type_ids[0]
        raise RecordImportError(u"Mapeo de tipo de cuenta de usuario desconocido para: %s" % type_code)

    #-------------------------------------------------------------------------
    #---  IMPORTACIÓN DE PRODUCTOS -------------------------------------------
    #-------------------------------------------------------------------------
    
    def import_products(self, p_filename):
        """
        Importa los artículos de la tabla ARTICULO.DBF de FacturaPlus a OpenERP
        """
        if self.update_accounts_only:
            return self.import_products_accounts_only(p_filename)
            
        #
        # Abrimos la tabla de artículos de FacturaPlus
        #
        dbf = ydbf.open(p_filename, encoding=self.encoding)

        records_with_errors = {}
        accounts_to_create = []

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Importando articulo '%s'..." % record['CREF']

                #
                # Resolvemos los ids de las cuentas contables para el producto
                #
                accounts = {}
                for field in ('CSCTAVTAS', 'CSCTACPRAS'):
                    try:
                        accounts[field] = self.get_account_id_for_account_number(record[field])
                    except AccountNotFoundException:
                        print u"WARN: No se ha encontrado la cuenta contable %s, sera necesario crearla a mano (el producto se importara sin ella)" % record[field]
                        accounts_to_create.append(record[field])

                #
                # Establecemos los valores del producto
                #
                values = {
                    'default_code' : record['CREF'],                # Código artículo
                    'name': record['CDETALLE'],                     # Nombre
                    'description': record['CDETALLE'],              # Descripción
                    'list_price': '%f' % record['NPVP'],            # Precio de venta
                    'standard_price': '%f' % record['NCOSTEPROM'],  # Precio de compra
                    'taxes_id': self.get_product_taxes_id(record),          # IVA venta
                    'supplier_taxes_id': self.get_product_supplier_taxes_id(record),    # IVA compra
                    'property_account_income': accounts.get('CSCTAVTAS', False),       # Cuenta contable ingresos
                    'property_account_expense': accounts.get('CSCTACPRAS', False),     # Cuenta contable gastos
                    'categ_id': 1,
                    'warranty': False,
                    'property_stock_procurement': 5,
                    'supply_method': 'produce',
                    'uos_id': False,
                    'ean13': False,
                    'mes_type': 'fixed',
                    'uom_id': 1,
                    'description_purchase': False,
                    'variants': False,
                    'uos_coeff': 1.0,
                    'sale_ok': 1,
                    'purchase_ok': 1,
                    'product_manager': False,
                    'track_outgoing': 0,
                    'company_id': 1,
                    'produce_delay': 1.0,
                    'state': False,
                    'loc_rack': False,
                    'uom_po_id': 1,
                    'type': 'service',
                    'property_stock_account_input': False,
                    'property_stock_account_output': False,
                    'track_incoming': 0,
                    'property_stock_production': 6,
                    'procure_method': 'make_to_order',
                    'active': 1,
                    'property_stock_inventory': 4,
                    'cost_method': 'average',
                    'loc_row': False,
                    'rental': 0,
                    'packaging': [],
                    'sale_delay': 7.0,
                    'loc_case': False,
                    'description_sale': False,
                    'track_production': 0,
                    'seller_ids': [],
                }
                        
                #
                # Intentamos crear el producto en OpenERP
                #              
                product_ids = self.search(u'product.product', [('name', '=', values['name'])])
                if len(product_ids) > 0:
                    # Actualizar
                    print u"INFO: Actualizando el producto %s en OpenERP" % product_ids[0]
                    self.write('product.product', product_ids[0], values)
                else:    
                    # Crear
                    print u"INFO: Creando un nuevo producto en OpenERP"
                    self.create('product.product', values)
                print u"INFO: ...listo, '%s' importado." % record['CREF']
                
            except RecordImportError, ex:
                records_with_errors[record['CREF']] = ex
                print u"ERROR: %s " % ex

        if len(accounts_to_create) > 0:
            print u"WARN: Por favor, cree manualmente las siguientes cuentas contables y repita la operación:\n\t%s" \
                    % list(set(accounts_to_create))
        if len(records_with_errors) > 0:
            print u"ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)
                
                
                
    #-------------------------------------------------------------------------
    #--- IMPORTACIÓN DE CLIENTES ---------------------------------------------
    #-------------------------------------------------------------------------

    def import_clients(self, c_filename):
        """
        Importa los clientes de la tabla CLIENTES.DBF de FacturaPlus a OpenERP
        delegando en import_partners.
        """
        if self.update_accounts_only:
            return self.import_partners_accounts_only(c_filename,  'clients')
        else:
            return self.import_partners(c_filename, 'clients')


    def import_suppliers(self, c_filename):
        """
        Importa los proveedores de la tabla PROVEEDO.DBF de FacturaPlus a OpenERP
        delegando en import_partners.
        """
        if self.update_accounts_only:
            return self.import_partners_accounts_only(c_filename,  'suppliers')
        else:
            return self.import_partners(c_filename, 'suppliers')

    
    def import_partners(self, c_filename, partners_type='clients'):
        """
        Importa las empresas (clientes o proveedores según el parámetro type),
        de FacturaPlus (CLIENTES.DBF o PROVEEDO.DBF) a OpenERP.
        """

        assert partners_type in ('clients', 'suppliers')
        is_client = (partners_type == 'clients')
        is_supplier = not is_client
        suffix = is_client and 'CLI' or 'PRO'

        #
        # Abrimos la tabla de artículos de FacturaPlus
        #
        dbf = ydbf.open(c_filename, encoding=self.encoding)

        records_with_errors = {}
        accounts_to_create = []

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Importando empresa '%s'..." % record['CCOD%s' % suffix]

                #
                # Direccion por defecto
                #
                address_values = {
                    'name':  record[is_client and 'CNOMCOM' or 'CNOMPRO'],
                    'title': False,
                    'type': 'default',
                    'street': record['CDIR%s' % suffix],
                    # TODO: Se importa el campo CONTACTO en street2 al no haber un campo que se corresponda, habría que crear un campo de usuario
                    'street2': (is_client and record['CCONTACTO'] and len(record['CCONTACTO']) and '(%s)' % record['CCONTACTO'] or False)
                                or (is_supplier and record['CPERCONT'] and len(record['CPERCONT']) and '(%s)' % record['CPERCONT'] or False),
                    'function': False,
                    'city': record['CPOB%s' % suffix],
                    'zip': record['CPTL%s' % suffix],
                    'country_id': self.get_partner_or_address_country_id(record, partners_type),
                    'state_id': self.get_partner_or_address_state_id(record, partners_type),
                    'phone': record['CTFO1%s' % suffix],
                    'mobile': record['CTFO2%s' % suffix],
                    'fax': record[is_client and 'CFAXCLI' or 'CFAX'],
                    'email': record['EMAIL'],
                }

                #
                # Información bancaria
                #
                bank_values = False
                if record['CENTIDAD']:
                    bank_values = {
                        'state': u'bank',
                        'name': self.get_partner_bank_name(record),
                        'acc_number': self.get_partner_ccc(record),
                        'acc_country_id': self.get_partner_bank_country_id(record),
                        'bank': self.get_partner_bank_id(record),
                        'sequence': 0,
                        'owner_name': False,
                        'street': False,
                        'zip': False,
                        'city': False,
                        'state_id': False,
                        'default_bank': True, # Banco por defecto (account_payment_extension)
                    }

                #
                # Resolvemos los ids de las cuentas contables para el partner
                #
                accounts = {}
                for field in ('CSUBCTA',):  # Nota: la coma hace falta para que python sepa que es una tupla :)
                    try:
                        accounts[field] = self.get_account_id_for_account_number(record[field])
                    except AccountNotFoundException:
                        print u"WARN: No se ha encontrado la cuenta contable %s, sera necesario crearla a mano (el partner se importara sin ella)" % record[field]
                        accounts_to_create.append(record[field])

                #
                # Datos del partner
                #
                partner_values = {
                    'name': record['CNOM%s' % suffix],          # Nombre
                    'ref': record['CCOD%s' % suffix],           # Código
                    'comercial': record[is_client and 'CNOMCOM' or 'CNOMPRO'],     # Nombre comercial
                    'comment': is_client and record['COBSCLI'] or False,       # Observaciones
                    'address': [(0, 0, address_values)],    # Dirección
                    'bank_ids': len(record['CCUENTA']) > 0 and [(0, 0, bank_values)] or [], # Banco
                    'property_account_receivable': is_client 
                        and (accounts.get('CSUBCTA') or self.get_account_id_for_account_number_or_subaccount(DEFAULT_CLIENT_RECEIVABLE_ACCOUNT))
                        or self.get_account_id_for_account_number_or_subaccount(DEFAULT_SUPPLIER_RECEIVABLE_ACCOUNT), # Cuenta cobros
                    'property_account_payable': is_supplier
                        and (accounts.get('CSUBCTA') or self.get_account_id_for_account_number_or_subaccount(DEFAULT_SUPPLIER_PAYABLE_ACCOUNT))
                        or self.get_account_id_for_account_number_or_subaccount(DEFAULT_CLIENT_PAYABLE_ACCOUNT), # Cuenta pagos
                    'property_payment_term': self.get_partner_payment_term_id(record),  # Plazos de pago
                    'payment_type_customer': is_client and self.get_partner_payment_type_id(record) or False,  # Tipo de pago (account_payment_extension)
                    'payment_type_supplier': is_supplier and self.get_partner_payment_type_id(record) or False,  # Tipo de cobro (account_payment_extension)
                    'vat': self.get_partner_vat(record, partners_type), #  NIF/CIF
                    'vat_subjected': 1,                 # Todos con IVA por defecto
                    'property_account_position': 1,     # Regimen Nacional por defecto
                    'property_stock_customer': 8,       # Ubicación "Clientes"
                    'property_stock_supplier': 7,       # Ubicación "Proveedores"
                    'property_product_pricelist': self.get_partner_pricelist_id(record, 'sale', partners_type),    # Tarifa de compra
                    'property_product_pricelist_purchase': self.get_partner_pricelist_id(record, 'purchase', partners_type),   # Tarifa de venta
                    'customer': is_client and 1 or 0,
                    'supplier': is_supplier and 1 or 0,
                    'active': 1,
                    'title': False,
                    'city': False,
                    'user_id': False,
                    'parent_id': False,
                    'date': False,
                    'website': False,
                    'lang': u'es_ES', # Por defecto todos los partners usarán Español.
                    'credit_limit': False,
                    'country': False,
                    'events': [],
                    'category_id': [(6, 0, [])]
                }
                
                #
                # Añadir campos personalizados
                #
                partner_values.update({
                    'sale_discount': (is_client and float(record['NDTOESP'])) or (is_supplier and float(record['NDTO'])) or 0.0 # Descuento de venta
                })

                #
                # Buscamos el partner en OpenERP
                #
                if partners_type=='clients':
                    partner_ids = self.search(u'res.partner', [('ref', '=', partner_values['ref']), ('customer', '=', 1)])
                else:
                    partner_ids = self.search(u'res.partner', [('ref', '=', partner_values['ref']), ('supplier', '=', 1)])


                if len(partner_ids) > 0:
                    #
                    # Actualizamos el partner (teniendo cuidado con las relaciones 1 a n [direcciones y bancos])
                    #
                    print "INFO: Actualizando el partner %s en OpenERP" % partner_ids[0]
                    try:
                        #
                        # Marcamos para eliminar las direcciones y bancos antiguos
                        #
                        partner_data = self.read('res.partner', partner_ids[0], ['address', 'bank_ids'])
                        print u"DEBUG: Marcando para borrar sus antiguas direcciones y bancos (%s y %s)" % (partner_data['address'], partner_data['bank_ids'])
                        partner_values['address'].extend([(2, x, False) for x in partner_data['address']])
                        partner_values['bank_ids'].extend([(2, x, False) for x in partner_data['bank_ids']])

                        # Escribimos el registro
                        self.write('res.partner', partner_ids[0], partner_values)
                    except Exception, err:
                        if re.match(r".*Error.*validating.*vat.*VAT.*correct.*", "%s" % err, re.DOTALL):
                            #
                            # Comprobamos la posibilidad de que el usuario se haya
                            # equivocado al escribir el NIF y haya puesto la letra delante.
                            #
                            vat_match = re.match(r'ES(?P<char>[A-Z])(?P<number>[0-9]{8})', partner_values['vat'])
                            if vat_match:
                                old_vat = partner_values['vat']
                                partner_values['vat'] = 'ES%s%s' % (vat_match.group('number'), vat_match.group('char'))
                                try:
                                    # Volvemos a intentar crear el registro
                                    print u"INFO: Reintentando actualización tras 'arreglar' el NIF"
                                    self.write('res.partner', partner_ids[0], partner_values)
                                except Exception, err:
                                    if re.match(r".*Error.*validating.*vat.*VAT.*correct.*", "%s" % err, re.DOTALL):
                                        if self.on_errors == 'ignore':
                                            print u"WARN: Ignorando el NIF/CIF del partner!!!"
                                            # Volvemos a intentar crear el registro sin NIF/CIF
                                            partner_values['vat'] = False
                                            try:
                                                self.write('res.partner', partner_ids[0], partner_values)
                                            except Exception, err2:
                                                raise RecordImportError(u"Error al actualizar el partner (sin NIF/CIF): %s" % err2)
                                        else:
                                            raise RecordImportError(u"NIF/CIF invalido (3): %s/%s (%s)" % (old_vat, partner_values.get('vat'), record[is_client and 'CDNICIF' or 'CNIFDNI']))
                                    else:
                                        raise RecordImportError(u"Error al actualizar el partner (reintento por NIF/CIF invalido): %s" % err)
                            else:
                                if self.on_errors == 'ignore':
                                    print u"WARN: Ignorando el NIF/CIF del partner!!!"
                                    # Volvemos a intentar crear el registro sin NIF/CIF
                                    partner_values['vat'] = False
                                    try:
                                        self.write('res.partner', partner_ids[0], partner_values)
                                    except Exception, err2:
                                        raise RecordImportError(u"Error al actualizar el partner (sin NIF/CIF): %s" % err2)
                                else:
                                    raise RecordImportError(u"NIF/CIF invalido (2): %s (%s)" % (partner_values.get('vat'), record[is_client and 'CDNICIF' or 'CNIFDNI']))
                        elif re.match(r".*The name of the partner must be unique.*", "%s" % err, re.DOTALL):
                            raise RecordImportError(u"Nombre de empresa duplicado: %s" % partner_values.get('name'))
                        else:
                            raise RecordImportError(u"Error al actualizar el partner: %s" % err)
                else:
                    #
                    # Creamos el partner, masticando un poco las excepciones que se puedan producir.
                    #
                    print u"INFO: Creando un nuevo partner en OpenERP"
                    try:
                        self.create('res.partner', partner_values)
                    except Exception, err:
                        if re.match(r".*Error.*validating.*vat.*VAT.*correct.*", "%s" % err, re.DOTALL):
                            #
                            # Comprobamos la posibilidad de que el usuario se haya
                            # equivocado al escribir el NIF y haya puesto la letra delante.
                            #
                            vat_match = re.match(r'ES(?P<char>[A-Z])(?P<number>[0-9]{8})', partner_values['vat'])
                            if vat_match:
                                old_vat = partner_values['vat']
                                partner_values['vat'] = 'ES%s%s' % (vat_match.group('number'), vat_match.group('char'))
                                try:
                                    print u"INFO: Reintentando creación tras 'arreglar' el NIF"
                                    # Volvemos a intentar crear el registro
                                    self.create('res.partner', partner_values)
                                except Exception, err:
                                    if re.match(r".*Error.*validating.*vat.*VAT.*correct.*", "%s" % err, re.DOTALL):
                                        if self.on_errors == 'ignore':
                                            print u"WARN: Ignorando el NIF/CIF del partner!!!"
                                            # Volvemos a intentar crear el registro sin NIF/CIF
                                            partner_values['vat'] = False
                                            try:
                                                self.create('res.partner', partner_values)
                                            except Exception, err2:
                                                raise RecordImportError(u"Error al crear el partner (sin NIF/CIF): %s" % err2)
                                        else:
                                            raise RecordImportError(u"NIF/CIF invalido (3): %s/%s (%s)" % (old_vat, partner_values.get('vat'), record[is_client and 'CDNICIF' or 'CNIFDNI']))
                                    else:
                                        raise RecordImportError(u"Error al crear el partner (reintento por NIF/CIF invalido): %s" % err)
                            else:
                                if self.on_errors == 'ignore':
                                    print u"WARN: Ignorando el NIF/CIF del partner!!!"
                                    # Volvemos a intentar crear el registro sin NIF/CIF
                                    partner_values['vat'] = False
                                    try:
                                        self.create('res.partner', partner_values)
                                    except Exception, err2:
                                        raise RecordImportError(u"Error al crear el partner (sin NIF/CIF): %s" % err2)
                                else:
                                    raise RecordImportError(u"NIF/CIF invalido (2): %s (%s)" % (partner_values.get('vat'), record[is_client and 'CDNICIF' or 'CNIFDNI']))
                        elif re.match(r".*The name of the partner must be unique.*", "%s" % err, re.DOTALL):
                            raise RecordImportError(u"Nombre de empresa duplicado: %s" % partner_values.get('name'))
                        else:
                            raise RecordImportError(u"Error al crear el partner: %s" % err)
                print u"INFO: ...listo, '%s' importado." % record['CCOD%s' % suffix]

            except RecordImportError, ex:
                records_with_errors[record['CCOD%s' % suffix]] = ex
                print u"ERROR: %s " % ex

        if len(accounts_to_create) > 0:
            print u"WARN: Por favor, cree manualmente las siguientes cuentas contables y repita la operación:\n\t%s" \
                    % list(set(accounts_to_create))
        if len(records_with_errors) > 0:
            print u"ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)
                
                
    #-------------------------------------------------------------------------
    #--- IMPORTACIÓN DE DIRECCIONES (ALTERNATIVAS) DE CLIENTES ---------------
    #-------------------------------------------------------------------------

    def import_clients_addresses(self, ca_filename, client=None):
        """
        Importa las direcciones alternativas de clientes de la tabla DIRCLI.DBF de FacturaPlus a OpenERP,
        ignorando las direcciones '0' (ver http://www.todoexpertos.com/categorias/negocios/gestion/respuestas/1104573/fallo-facturaplus)
        """
        #
        # Abrimos la tabla de artículos de FacturaPlus
        #
        dbf = ydbf.open(ca_filename, encoding=self.encoding)

        records_with_errors = {}
        clients_with_old_address_deleted = []

        #
        # Recorremos los registros
        #
        for record in dbf:
            if not client or record['CCODCLI'] == client:
                try:
                    if record['CIDENDIR'] == '0':
                        print u"INFO: Ignorando direccion '%s/%s'..." % (record['CCODCLI'], record['CIDENDIR'])
                    else:
                        print u"INFO: Importando direccion '%s/%s'..." % (record['CCODCLI'], record['CIDENDIR'])
                        #
                        # Buscamos el cliente para esa dirección
                        #
                        partner_ids = self.search(u'res.partner', [('ref', '=', record['CCODCLI']), ('customer', '=', 1)])
                        if len(partner_ids) > 0:
                            #
                            # Marcamos para eliminar las direcciones alternativas (no por defecto) antiguas
                            # (sólo la primera vez para cada cliente)
                            #
                            if partner_ids[0] not in clients_with_old_address_deleted:
                                try:
                                    clients_with_old_address_deleted.append(partner_ids[0])
                                    address_ids = self.search(u'res.partner.address', [('partner_id', '=', partner_ids[0]), ('type', '!=', 'default')])
                                    if len(address_ids) > 0:
                                        print "INFO: Eliminando direcciones alternativas antiguas de %s en OpenERP" % partner_ids[0]
                                        self.unlink('res.partner.address', address_ids)
                                except Exception, err:
                                    raise RecordImportError("Error al borrar las direcciones antiguas: %s" % err)

                            #
                            # Establecemos los valores del registro (dirección) a importar
                            #
                            address_values = {
                                'partner_id': partner_ids[0],
                                'name': record['CNOMCOM'],
                                'title': False,
                                'type': False,
                                'street': record['CDIRCLI'],
                                'street2': False,
                                'function': False,
                                'city': record['CPOBCLI'],
                                'zip': record['CPTLCLI'],
                                'country_id': self.get_partner_or_address_country_id(record, 'clients'),
                                'state_id': self.get_partner_or_address_state_id(record, 'clients'),
                                'phone': record['CTFO1CLI'],
                                'mobile': False,
                                'fax': False,
                                'email': record['EMAIL'],
                            }

                            #
                            # Creamos la nueva dirección
                            #
                            try:
                                print "INFO: Creando direccion alternativa para %s en OpenERP" % partner_ids[0]
                                self.create('res.partner.address', address_values)
                            except Exception, err:
                                raise RecordImportError("Error al crear la direccion: %s" % err)
                        else:
                            raise RecordImportError("El cliente %s no existe!" % record['CCODCLI'])
                        print u"INFO: ...listo, '%s/%s' importado." % (record['CCODCLI'], record['CIDENDIR'])
                        
                except RecordImportError, ex:
                    records_with_errors[record['CCODCLI']] = ex
                    print "ERROR: %s " % ex

        if len(records_with_errors) > 0:
            print "ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)


    #-------------------------------------------------------------------------
    #--- IMPORTACIÓN DE SUBCUENTAS CONTABLES ---------------------------------
    #-------------------------------------------------------------------------

    def import_accounts(self, sa_filename):
        """
        Importa las subcuentas SUBCTA.DBF y sus saldos de ContaPlus a OpenERP.
        Pero no crea entidades/partners de OpenERP (eso se hace a partir de
        los datos de FacturaPlus).
        """
        #
        # Abrimos la tabla de subcuentas de ContaPlus
        #
        dbf = ydbf.open(sa_filename, encoding=self.encoding)

        records_with_errors = {}

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Importando subcuenta '%s/%s'..." % (record['COD'], record['TITULO'])
                
                # Obtenemos la subcuenta (si existe)
                accounts_ids = self.search(u'account.account', [('code', '=', record['COD'])])

                # Buscamos el padre esperado para la cuenta
                account_parent_id = self.get_account_parent_id(record['COD'])

                if len(accounts_ids) > 0:
                    # La cuenta ya existe
                    print u"INFO: La cuenta '%s' ya existe, nada que hacer." % record['COD']
                    # TODO: Quiza sea necesario detectar si la cuenta existe
                    # pero ha sido creada a partir de la plantilla por culpa
                    # del número de dígitos.
                else:
                    # La cuenta no existe
                    print u"INFO: La cuenta '%s' no existe, creandola..." % record['COD']

                    #
                    # Establecemos los valores del registro (cuenta) a importar
                    #
                    account_values = {
                        'code': record['COD'],
                        'name': record['TITULO'],
                        'parent_id': account_parent_id,
                        'type': self.get_account_type(record['COD']),
                        'user_type': self.get_account_user_type_id(record['COD']),
                        'reconcile': self.get_account_reconcile(record['COD']),
                        'company_id': 1,
                        'currency_id': False,
                        'currency_mode': 'current',
                        'check_history': 1,
                        'active': 1,
                        'tax_ids': [(6, 0, [])],
                        'note': False,
                    }

                    #
                    # Creamos la nueva cuenta
                    #
                    try:
                        print "INFO: Creando nueva subcuenta %s en OpenERP" % account_values['code']
                        self.create('account.account', account_values)
                    except Exception, err:
                        raise RecordImportError("Error al crear la subcuenta: %s" % err)

                #
                # Modificamos el padre de la cuenta para cambiarle el tipo
                # a vista (no sólo hay que cambiar el tipo, también
                # hay que quitarle los ceros que OpenERP añadió al final
                # para convertirlo en una subcuenta)
                #
                try:
                    parent_data = self.read(u'account.account', [account_parent_id], ['code', 'type', 'user_type'])[0]
                    if parent_data['type'] != ACCOUNT_VIEW_TYPE:
                        print "INFO: Convirtiendo cuenta padre %s en vista" % parent_data['code']
                        new_parent_data = {}
                        # Restauramos el código de la cuenta a su original según
                        # la plantilla contable (quitamos los ceros que OpenERP
                        # haya podído añadir a la derecha:
                        new_parent_data['code'] = self.get_account_original_code_from_template(parent_data['code'])
                        # Cambiamos el tipo interno
                        new_parent_data['type'] = ACCOUNT_VIEW_TYPE
                        new_parent_data['user_type'] = self.get_account_user_type_id_by_code(ACCOUNT_VIEW_USER_TYPE)
                        # Guardamos los cambios del padre
                        self.write(u'account.account', account_parent_id, new_parent_data)
                except Exception, err:
                    raise RecordImportError("Error al convertir la cuenta padre en vista: %s" % err)

                print u"INFO: ...listo, cuenta '%s/%s' importada." % (record['COD'], record['TITULO'])

            except RecordImportError, ex:
                records_with_errors[record['COD']] = ex
                print "ERROR: %s " % ex

        if len(records_with_errors) > 0:
            print "ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)


    def import_accounts_balance(self, sa_filename):
        """
        Importa de SUBCTA.DBF los saldos de ContaPlus a OpenERP.
        Nota: import_accounts debe haberse ejecutado anteriormente para crear
        las cuentas.
        """
        #
        # Abrimos la tabla de subcuentas de ContaPlus
        #
        dbf = ydbf.open(sa_filename, encoding=self.encoding)

        records_with_errors = {}

        #
        # Establecemos los datos por defecto para el movimiento contable
        #
        journal_id = self.search('account.journal', [('code', '=', ACCOUNT_MOVE_JOURNAL)])[0]
        account_move_data = {
            'ref': ACCOUNT_MOVE_REF,
            'journal_id': journal_id,
            'line_id': [],
            'partner_id': False,
            'to_check': 0
        }
        account_move_data.update(self.default_get('account.move', ['date', 'period_id', 'state', 'type', 'name']))
        lines_data = account_move_data['line_id']

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Cargando saldo subcuenta '%s/%s'..." % (record['COD'], record['TITULO'])
                # Obtenemos la subcuenta (si existe)
                accounts_ids = self.search(u'account.account', [('code', '=', record['COD'])])
                if not len(accounts_ids):
                    # La cuenta no existe
                    raise AccountNotFoundException(u"Cuenta contable no encontrada: %s" % record['COD'])

                #
                # Obtenemos los saldos, en euros, de ContaPlus
                #
                debit =  float(record['SUMADBEU'])
                credit = float(record['SUMAHBEU'])

                # Establecemos los datos de la línea
                line_data = {
                    'account_id': accounts_ids[0],
                    'debit': 0.0,
                    'credit': 0.0,
                    'name': ACCOUNT_MOVE_LINE_NAME % record['TITULO'],
                    'ref': False,
                    'currency_id': False,
                    'tax_amount': False,
                    'partner_id': False,
                    'tax_code_id': False,
                    'date_maturity': False,
                    'amount_currency': False,
                    'analytic_account_id': False,
                }

                #
                # Creamos una línea para el debe y otra para el haber
                # ya que OpenERP no nos permite importar ambos valores en una
                # sóla línea.
                #
                line_data_debit = line_data.copy()
                line_data_credit = line_data
                line_data_debit['debit'] = debit
                line_data_credit['credit'] = credit
                
                #
                # Añadimos cada línea al movimiento (si tienen valor).
                #
                if debit != 0.0:
                    lines_data.append((0, 0, line_data_debit))
                if credit != 0.0:
                    lines_data.append((0, 0, line_data_credit))

            except RecordImportError, ex:
                records_with_errors[record['COD']] = ex
                print "ERROR: %s " % ex

        # Creamos el movimiento contable
        print u"INFO: Creando movimiento contable..."
        self.create('account.move', account_move_data)
        
        if len(records_with_errors) > 0:
            print "ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)


    def import_partners_accounts_only(self, c_filename, partners_type='clients'):
        """
        Importa el enlace a las cuentas contables de los partners.
        """

        assert partners_type in ('clients', 'suppliers')
        is_client = (partners_type == 'clients')
        is_supplier = not is_client
        suffix = is_client and 'CLI' or 'PRO'

        #
        # Abrimos la tabla de artículos de FacturaPlus
        #
        dbf = ydbf.open(c_filename, encoding=self.encoding)

        records_with_errors = {}
        accounts_to_create = []

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Importando enlace cuentas contables de empresa '%s'..." % record['CCOD%s' % suffix]

                #
                # Resolvemos los ids de las cuentas contables para el partner
                #
                accounts = {}
                for field in ('CSUBCTA',):  # Nota: la coma hace falta para que python sepa que es una tupla :)
                    try:
                        accounts[field] = self.get_account_id_for_account_number(record[field])
                    except AccountNotFoundException:
                        print u"WARN: No se ha encontrado la cuenta contable %s, sera necesario crearla a mano (el partner se importara sin ella)" % record[field]
                        accounts_to_create.append(record[field])

                #
                # Datos del partner
                #
                partner_values = {
                    'property_account_receivable': is_client
                        and (accounts.get('CSUBCTA') or self.get_account_id_for_account_number_or_subaccount(DEFAULT_CLIENT_RECEIVABLE_ACCOUNT))
                        or self.get_account_id_for_account_number_or_subaccount(DEFAULT_SUPPLIER_RECEIVABLE_ACCOUNT), # Cuenta cobros
                    'property_account_payable': is_supplier
                        and (accounts.get('CSUBCTA') or self.get_account_id_for_account_number_or_subaccount(DEFAULT_SUPPLIER_PAYABLE_ACCOUNT))
                        or self.get_account_id_for_account_number_or_subaccount(DEFAULT_CLIENT_PAYABLE_ACCOUNT), # Cuenta pagos
                }

                #
                # Actualizamos el partner en OpenERP
                #
                if partners_type=='clients':
                    partner_ids = self.search(u'res.partner', [('ref', '=', record['CCOD%s' % suffix]), ('customer', '=', 1)])
                else:
                    partner_ids = self.search(u'res.partner', [('ref', '=', record['CCOD%s' % suffix]), ('supplier', '=', 1)])

                if len(partner_ids) > 0:
                    print "INFO: Actualizando el partner %s en OpenERP" % partner_ids[0]
                    try:
                        # Escribimos el registro
                        self.write('res.partner', partner_ids[0], partner_values)
                    except Exception, err:
                       raise RecordImportError(u"Error al actualizar el partner: %s" % err)
                else:
                   raise RecordImportError(u"El partner %s no existe" % record['CCOD%s' % suffix])
                print u"INFO: ...listo, '%s' importado." % record['CCOD%s' % suffix]

            except RecordImportError, ex:
                records_with_errors[record['CCOD%s' % suffix]] = ex
                print u"ERROR: %s " % ex

        if len(accounts_to_create) > 0:
            print u"WARN: Por favor, cree manualmente las siguientes cuentas contables y repita la operación:\n\t%s" \
                    % list(set(accounts_to_create))
        if len(records_with_errors) > 0:
            print u"ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)


    def import_products_accounts_only(self, p_filename):
        """
        Importa el enlace contable de los artículos.
        """
        #
        # Abrimos la tabla de artículos de FacturaPlus
        #
        dbf = ydbf.open(p_filename, encoding=self.encoding)

        records_with_errors = {}
        accounts_to_create = []

        #
        # Recorremos los registros
        #
        for record in dbf:
            try:
                print u"INFO: Importando enlace cuentas contables de articulo '%s'..." % record['CREF']

                #
                # Resolvemos los ids de las cuentas contables para el producto
                #
                accounts = {}
                for field in ('CSCTAVTAS', 'CSCTACPRAS'):
                    try:
                        accounts[field] = self.get_account_id_for_account_number(record[field])
                    except AccountNotFoundException:
                        print u"WARN: No se ha encontrado la cuenta contable %s, sera necesario crearla a mano (el producto se importara sin ella)" % record[field]
                        accounts_to_create.append(record[field])

                #
                # Establecemos los valores del producto
                #
                values = {
                    'property_account_income': accounts.get('CSCTAVTAS', False),       # Cuenta contable ingresos
                    'property_account_expense': accounts.get('CSCTACPRAS', False),     # Cuenta contable gastos
                }

                #
                # Intentamos actualizar el producto en OpenERP
                #
                product_ids = self.search(u'product.product', [('name', '=', record['CDETALLE'])])
                if len(product_ids) > 0:
                    # Actualizar
                    print u"INFO: Actualizando el producto %s en OpenERP" % product_ids[0]
                    self.write('product.product', product_ids[0], values)
                else:
                    raise RecordImportError(u"El producto %s no existe" % record['CDETALLE'])

                print u"INFO: ...listo, '%s' importado." % record['CREF']

            except RecordImportError, ex:
                records_with_errors[record['CREF']] = ex
                print u"ERROR: %s " % ex

        if len(accounts_to_create) > 0:
            print u"WARN: Por favor, cree manualmente las siguientes cuentas contables y repita la operación:\n\t%s" \
                    % list(set(accounts_to_create))
        if len(records_with_errors) > 0:
            print u"ERROR: Los siguientes registros causaron algún error y probablemente no se importaron:"
            for rec, ex in records_with_errors.iteritems():
                print "\t%s: %s" % (rec, ex)



                
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
    
                
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print u"Uso: %s <dbname> <user> <password> <filename> [ignore] [account_only]" % sys.argv[0]
    else:
        ENGINE = FacturaPlus2OpenERP(sys.argv[1], sys.argv[2], sys.argv[3])
        FILENAME = sys.argv[4]
        ENGINE.on_errors = len(sys.argv) >= 6 and sys.argv[5] == 'ignore' and 'ignore' or 'strict'
        ENGINE.update_accounts_only = len(sys.argv) >= 7 and sys.argv[6] == 'account_only' and True

        FNL = FILENAME.lower()
        
        if re.match(r'.*articulo.dbf$', FNL):
            ENGINE.import_products(FILENAME)
        elif re.match(r'.*clientes.dbf$', FNL):
            ENGINE.import_clients(FILENAME)
        elif re.match(r'.*proveedo.dbf$', FNL):
            ENGINE.import_suppliers(FILENAME)
        elif re.match(r'.*dircli.dbf$', FNL):
            ENGINE.import_clients_addresses(FILENAME)
        elif re.match(r'.*subcta.dbf$', FNL):
            ENGINE.import_accounts(FILENAME)
            if not ENGINE.update_accounts_only:
                ENGINE.import_accounts_balance(FILENAME)
        else:
            print u"Archivo no soportado."
    
    
    
    
