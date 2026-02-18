# -*- coding: utf-8 -*-
from odoo import models, fields, _

class IspWorkOrderType(models.Model):
    _name = 'isp.work.order.type'
    _description = 'Work Order Type'
    _order = 'name'

    name = fields.Char(string="Work Order Type", required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'unique_work_order_type_name',
            'unique(name)',
            'Work Order Type name must be unique!'
        ),
    ]
