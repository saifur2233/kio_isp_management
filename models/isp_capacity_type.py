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

    @api.constrains('vlan_port', 'transmission_id')
    def _check_unique_vlan_per_aggregation_nttn(self):
        """Prevent reusing the same VLAN ID within the same Aggregation Point and NTTN."""
        for record in self:
            if not record.vlan_port or not record.transmission_id:
                continue

            aggregation_point = record.transmission_id.aggregation_point_id
            nttn_provider = record.transmission_id.nttn_provider_name
            if not aggregation_point or not nttn_provider:
                continue

            duplicate = self.search([
                ('id', '!=', record.id),
                ('vlan_port', '=', record.vlan_port),
                ('transmission_id.aggregation_point_id', '=', aggregation_point.id),
                ('transmission_id.nttn_provider_name', '=', nttn_provider.id),
            ], limit=1)

            if duplicate:
                raise ValidationError(_(
                    "VLAN ID '%s' is already used for this Aggregation Point under the same NTTN."
                ) % record.vlan_port)
