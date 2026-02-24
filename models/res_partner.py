from odoo import api, fields, models
from .district_selection import DIVISION_SELECTION


class ResPartner(models.Model):
    _inherit = "res.partner"

    division = fields.Selection(DIVISION_SELECTION, string='Division', readonly=True)
    district_id = fields.Many2one('isp.district', string='District', readonly=True)
    upazila_id = fields.Many2one('isp.upazila', string='Upazila', domain="[('district_id', '=', district_id)]",
                                 readonly=True)