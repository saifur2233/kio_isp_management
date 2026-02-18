from odoo import fields, models

class IspSupportTeam(models.Model):
    _name = 'isp.support.team'
    _description = 'ISP Support Team'
    _rec_name = 'name'
    _order = 'name asc'

    name = fields.Char(string='Support Team', required=True)
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        (
            'unique_support_team_name',
            'unique(name)',
            'Support Team name must be unique!'
        ),
    ]