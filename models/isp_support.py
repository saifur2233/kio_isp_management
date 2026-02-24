from odoo import fields, models, api



class IspSupport(models.Model):
    _name = 'isp.support'
    _description = 'Isp Support'

    active = fields.Boolean(default=True, invisible=True)