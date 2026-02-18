from odoo import fields, models, api


class IspLicense(models.Model):
    _name = 'isp.license'
    _description = 'ISP License'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'License name must be unique!'),
    ]