from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class IspCapacityType(models.Model):
    _name = 'isp.capacity.type'
    _description = 'isp capacity type'

    transmission_id = fields.Many2one(
        'isp.transmission.nttn',
        string='NTTN Transmission',
        required=False,
    )

    own_id = fields.Many2one('isp.transmission.own', string='OWN')

    type_id = fields.Many2one('isp.capacity.master', string='Item')
    survey_id = fields.Many2one('isp.survey', string='Survey')
    isp_sale_id = fields.Many2one(
        'isp.marketing.management',
    )
    active = fields.Boolean(default=True, invisible=True)

    parameter = fields.Selection(
        [
            ('mb', 'MB'),
        ],
        default='mb',
        readonly=True
    )

    capacity = fields.Integer(string='Capacity')
    buffer_bandwidth = fields.Float(string='Buffer Bandwidth')
    existing_price = fields.Float(string='Existing Price')
    existing_total_price = fields.Float(
        string='Existing Total Price',
        compute='_compute_existing_total_price',
    )

    vlan_port = fields.Char(string="VLAN ID")
    ip_address = fields.Char(string="IP Address")

    @api.depends('capacity', 'existing_price')
    def _compute_existing_total_price(self):
        for record in self:
            record.existing_total_price = (record.capacity or 0.0) * (record.existing_price or 0.0)


    @api.constrains('type_id', 'parameter', 'capacity')
    def _check_type_id_requirements(self):
        """If type_id is selected, then parameter is required and capacity cannot be zero."""
        for record in self:
            if record.type_id:
                if not record.parameter:
                    raise ValidationError(
                        _("Parameter (Gb/Mb) is required when Type is selected.")
                    )
                if not record.capacity or record.capacity <= 0:
                    raise ValidationError(
                        _("Capacity must be greater than zero when Type is selected.")
                    )
