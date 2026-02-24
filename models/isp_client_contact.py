from odoo import models, fields, _

class IspClientContact(models.Model):
    _name = 'isp.client.contact'
    _description = 'ISP Client Contact'

    client_id = fields.Many2one('isp.client', required=True, ondelete='cascade')
    contact_type = fields.Selection([
        ('owner', 'Owner'),
        ('billing', 'Billing'),
        ('marketing', 'Marketing'),
        ('technical', 'Technical'),
    ], string="Type", required=True)

    name = fields.Char(string="Name")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    active = fields.Boolean(default=True, invisible=True)
