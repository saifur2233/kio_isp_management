from odoo import fields, models, api


class IspMacDetail(models.Model):
    _name = 'isp.mac.detail'
    _description = 'ISP MAC Detail'

    survey_existing_id = fields.Many2one('isp.survey', string='Survey (Existing)')
    survey_offer_id = fields.Many2one('isp.survey', string='Survey (Offer)')
    product_id = fields.Many2one('product.product', string='Package Name')
    qty = fields.Float(string='Qty')
    current_rate = fields.Float(string='Current Rate')
    commission_rate = fields.Float(string='Commission (%)')
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
    )

    # @api.depends('qty', 'current_rate', 'commission_rate')
    # def _compute_amount(self):
    #     for record in self:
    #         base_amount = (record.qty or 0.0) * (record.current_rate or 0.0)
    #         record.amount = base_amount * ((record.commission_rate or 0.0) / 100.0)
    
    
    @api.depends('qty', 'current_rate', 'commission_rate')
    def _compute_amount(self):
        for rec in self:
            qty = rec.qty or 0.0
            rate = rec.current_rate or 0.0
            commission = rec.commission_rate or 0.0

            rec.amount = qty * rate * commission


