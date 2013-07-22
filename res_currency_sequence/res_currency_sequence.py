# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
from datetime import datetime, date, timedelta

class res_currency_rate(osv.osv):
    _name = "res.currency.rate"
    _inherit = "res.currency.rate"
    
    def get_res_currency_rate(self, cr, uid, currency_id, name, context=None):
        """
           This function returns rate of the day, if not found, returns the previous day.
        """
        currency_rate_ids = self.search(cr, uid, [('currency_id','=',currency_id), ('name', '<=', name)], limit=1, order='name desc')
        if currency_rate_ids == []:
            currency_rate_ids = self.search(cr, uid, [('currency_id','=',currency_id), ('name', '>', name)], limit=1, order='name asc')
        if currency_rate_ids == []:
            return 0
        currency_rate = self.browse(cr, uid, currency_rate_ids[0], context=context)
        return currency_rate.rate

class ResCurrency(osv.osv):
    _name = "res.currency"
    _inherit = "res.currency"
        
    _columns = {
        'sequence': fields.integer('Sequence', required=True, help='Use to arrange calculation sequence', select=True),
    }
    
    _defaults = {
        'sequence': 0,
    }
     
    _sql_constraints = [
        ('res_currency_sequence', 'unique(sequence)', 'Sequence must be unique per currency!'),
    ]
    
    _order = 'sequence'
    
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'sequence': None,
        })
        return super(ResCurrency, self).copy(cr, uid, id, default, context)
    
    def get_exchange_rate(self, cr, uid, res_currency_initial, res_currency_finally, name, context=None):
        """
        :param name: date of exchange rate
        """
        res_currency_rate_obj = self.pool.get('res.currency.rate')
        result = 0.00
        
        res_currency_base_id = self.search(cr, uid, [('base', '=', True)])
        res_currency_base = self.browse(cr, uid, res_currency_base_id)[0]
        
        if res_currency_initial.id == res_currency_base.id:
            result = res_currency_rate_obj.get_res_currency_rate(cr, uid, res_currency_finally.id, name, context=context)
        else:
            currency_rate_initial = res_currency_rate_obj.get_res_currency_rate(self, cr, uid, res_currency_initial.id, name, context=context)
            currency_rate_finally = res_currency_rate_obj.get_res_currency_rate(self, cr, uid, res_currency_finally.id, name, context=context)
            result = currency_rate_initial * currency_rate_finally
        return result