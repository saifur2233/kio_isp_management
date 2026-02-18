from odoo import models, fields

class IspClientType(models.Model):
    _name = 'isp.client.type'
    _description = 'ISP Client Type'
    _rec_name = 'name'
    _order = 'name asc'

    name = fields.Char(string='Client Type', required=True)
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        (
            'unique_client_type_name',
            'unique(name)',
            'Client Type name must be unique!'
        ),
    ]




