from odoo import fields, models, api



class IspLegal(models.Model):
    _name = 'isp.legal'
    _description = 'Isp Legal'

    name = fields.Char()
    active = fields.Boolean(default=True, invisible=True)