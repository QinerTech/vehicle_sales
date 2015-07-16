# -*- coding: utf-8 -*-

from openerp import api, fields, models


class saleOrder(models.Model):
    _inherit = 'sale.order'

    deposit = fields.Float(u'订金', readonly=True, states={'draft': [('readonly', False)]})
    note_payment = fields.Text(u'其他付款方式', readonly=True, states={'draft': [('readonly', False)]})
    note_shipping = fields.Text(u'车辆运输', readonly=True, states={'draft': [('readonly', False)]})
    note_agreement = fields.Text(u'双方特别约定', readonly=True, states={'draft': [('readonly', False)]})
