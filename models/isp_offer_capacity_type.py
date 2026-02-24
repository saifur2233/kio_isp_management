from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class IspOfferCapacityType(models.Model):
    _name = 'isp.offer.capacity.type'
    _description = 'ISP Offer Capacity Type'

    type_id = fields.Many2one('isp.capacity.master', string='Item')
    survey_id = fields.Many2one('isp.survey', string='Survey')

    parameter = fields.Selection(
        [
            ('mb', 'MB'),
        ],
        default='mb',
        readonly=True
    )
    capacity = fields.Integer(string='Capacity')
    buffer_bandwidth = fields.Float(string='Buffer Bandwidth')
    offer_price = fields.Float(string='Offer Price')
    offer_total_price = fields.Float(
        string='Total Offer Price',
        compute='_compute_offer_total_price',
    )

    @api.depends('capacity', 'offer_price')
    def _compute_offer_total_price(self):
        for record in self:
            record.offer_total_price = (record.capacity or 0.0) * (record.offer_price or 0.0)

    @api.constrains('type_id', 'parameter', 'capacity')
    def _check_type_id_requirements(self):
        for record in self:
            if record.type_id:
                if not record.parameter:
                    raise ValidationError(
                        _("Parameter (Gb/Mb) is required when Item is selected.")
                    )
                if not record.capacity or record.capacity <= 0:
                    raise ValidationError(
                        _("Capacity must be greater than zero when Item is selected.")
                    )
