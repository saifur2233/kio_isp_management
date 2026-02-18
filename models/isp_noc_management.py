from odoo import fields, models, api


class IspNocManagement(models.Model):
    _name = 'isp.noc.management'
    _description = 'Isp Noc Management'

    active = fields.Boolean(default=True, invisible=True)

