from odoo import fields, models


class IspPortMaster(models.Model):
    _name = 'isp.port.master'
    _description = 'ISP Port'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This port already exists!'),
    ]
