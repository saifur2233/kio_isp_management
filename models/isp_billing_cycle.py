from odoo import fields, models, api


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
    amount = fields.Monetary(string='Total Bill', currency_field='currency_id')
    percentage = fields.Float(string='Percentage')
    total_amount = fields.Monetary(string='Amount', compute="_compute_total_amount")

    @api.depends('amount', 'percentage')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount * rec.percentage
