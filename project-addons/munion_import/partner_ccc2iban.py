#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xmlrpclib
import socket
from ccc2iban import *

class convert_ccc2iban(object):
    """clase que importa desde un csv empresas."""
    def __init__(self, dbname, user, passwd):
        """método incial"""
        try:
            self.url_template = "http://%s:%s/xmlrpc/%s"
            self.server = "localhost"
            self.port = 9069
            self.dbname = dbname
            self.user_name = user
            self.user_passwd = passwd

            #
            # Conectamos con OpenERP
            #
            login_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'common'))
            self.user_id = login_facade.login(self.dbname, self.user_name, self.user_passwd)
            self.object_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'object'))

            #convertimos el csv a xml
            res = self.convert_ccc2iban()
            #con exito
            if res:
                print ("Iban conversion successful")
        except Exception, e:
            print ("ERROR: ", (e))
            sys.exit(1)

    #Métodos Xml-rpc

    def create(self, model, data, context={}):
        """
        Wrapper del metodo create.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'create', data, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en create: %s' % (err.faultCode, err.faultString))


    def search(self, model, query, offset=0, limit=False, order=False, context={}, count=False):
        """
        Wrapper del metodo search.
        """
        try:
            ids = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'search', query, offset, limit, order, context, count)
            return ids
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en search: %s' % (err.faultCode, err.faultString))


    def read(self, model, ids, fields, context={}):
        """
        Wrapper del metodo read.
        """
        try:
            data = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'read', ids, fields, context)
            return data
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en read: %s' % (err.faultCode, err.faultString))


    def write(self, model, ids, field_values, context={}):
        """
        Wrapper del metodo write.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'write', ids, field_values, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en write: %s' % (err.faultCode, err.faultString))


    def unlink(self, model, ids, context={}):
        """
        Wrapper del metodo unlink.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'unlink', ids, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en unlink: %s' % (err.faultCode, err.faultString))

    def default_get(self, model, fields_list=[], context={}):
        """
        Wrapper del metodo default_get.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'default_get', fields_list, context=context)
            return res
        except socket.error, err:
            raise Exception('Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception('Error %s en default_get: %s' % (err.faultCode, err.faultString))

    def execute(self, model, method, ids, context={}):
        """
        Wrapper del método execute.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, method, ids)
            return res
        except socket.error, err:
            raise Exception('Conexión rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception('Error %s en execute: %s' % (err.faultCode, err.faultString))

    def convert_ccc2iban(self):
        bank_ids = self.search('res.partner.bank', [('state','=','bank')])

        for bank_id in bank_ids:
            bank_data = self.read('res.partner.bank', bank_id, ['acc_number', 'acc_country_id'])
            if bank_data['acc_country_id']:
                country_data = self.read('res.country', bank_data['acc_country_id'][0], ['code'])
                country_code = country_data['code']
            else:
                country_code = 'ES'

            try:
                ccc = bank_data["acc_number"].replace(" ", "")
                iban = create_iban(country_code, ccc[:8], ccc[8:])
                self.write('res.partner.bank', bank_id, {'state': 'iban', 'acc_number': iban})
            except IBANError, err:
                print err

        return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print u"Uso: %s <dbname> <user> <password>" % sys.argv[0]
    else:
        ENGINE = convert_ccc2iban(sys.argv[1], sys.argv[2], sys.argv[3])
