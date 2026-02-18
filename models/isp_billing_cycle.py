from odoo import fields, models


class IspBillingCycle(models.Model):
    _name = 'isp.billing.cycle'
    _description = 'ISP Billing Cycle'

    work_order_id = fields.Many2one(
        'isp.work.order',
        string='Work Order',
        required=True,
        ondelete='cascade'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='work_order_id.currency_id',
        readonly=True
    )
    day = fields.Integer(string='Day')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    percentage = fields.Float(string='Percentage')
