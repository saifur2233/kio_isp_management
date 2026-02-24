from odoo import fields, models, api, _
from odoo.exceptions import ValidationError



class IspTransmissionOwn(models.Model):
    _name = 'isp.transmission.own'
    _description = 'Own Transmission'
    _rec_name = 'marketing_id'


    active = fields.Boolean(default=True, invisible=True)
    marketing_id = fields.Many2one(
        'isp.marketing.management',
        string='Marketing Ref',
        ondelete='set null',
        index=True,
        tracking=True,
        help='Marketing record linked to this NTTN survey.'
    )

    seq_id = fields.Char(string='ID', readonly=True, tracking=True,
                         help='Unique survey identifier propagated from marketing.')
    district = fields.Char(string='District', readonly=True, tracking=True,
                           help='District inherited from the marketing request.')
    upazila = fields.Char(string='Upazila', readonly=True, tracking=True,
                          help='Upazila inherited from the marketing request.')
    area = fields.Char(string='Area', readonly=True, tracking=True,
                       help='Specific area/village for the request.')
    total_capacity = fields.Float(string='Total Capacity', readonly=True, tracking=True,
                                  help='Summed requested capacity from the marketing record.')
    remarks = fields.Text(string='Marketing Remarks', readonly=True, tracking=True,
                          help='Marketing team remarks pulled from the request.')
    latitude = fields.Float(string="Latitude", readonly=True, tracking=True,
                            help='Marketing-provided latitude of the site.')
    longitude = fields.Float(string="Longitude", readonly=True, tracking=True,
                             help='Marketing-provided longitude of the site.')

    aggregation_point_id = fields.Many2one(
        'isp.aggregation.point',
        string='Aggregation Point',
        tracking=True,
        help='Aggregation point associated with this transmission.'
    )
    aggregation_switch_model_no = fields.Char(
        string='Switch Model No',
        related='aggregation_point_id.switch_model_no',
        readonly=True,
    )
    aggregation_pop_latitude = fields.Char(
        string='POP Latitude',
        related='aggregation_point_id.pop_latitude',
        readonly=True,
    )
    aggregation_pop_longitude = fields.Char(
        string='POP Longitude',
        related='aggregation_point_id.pop_longitude',
        readonly=True,
    )

    own_remarks = fields.Text(string='OWN Remarks', tracking=True,
                               help='Surveyor remarks entered by the NTTN team.')

    survey_report = fields.Text(
        string="Survey Report",
        help='Survey notes for primary-only connections.'
    )
    survey_report_file = fields.Binary(
        string="Survey Report File",
        attachment=True,
        help='Attach supporting documents for the primary-only survey.'
    )
    survey_report_filename = fields.Char(
        string="Survey File Name",
        help='Filename for the primary-only survey attachment.'
    )

    survey_report_for_primary = fields.Text(
        string="Survey Report for Primary",
        help='Text notes for the primary portion of secondary connectivity.'
    )
    survey_report_for_primary_file = fields.Binary(
        string="Primary Survey Report File",
        attachment=True,
        help='Attachment for the primary portion of secondary connectivity.'
    )
    survey_report_for_primary_filename = fields.Char(
        string="Primary Survey File Name",
        help='Filename for the primary survey attachment.'
    )

    survey_report_for_secondary = fields.Text(
        string="Survey Report for Secondary",
        help='Text notes for the secondary portion of secondary connectivity.'
    )
    survey_report_for_secondary_file = fields.Binary(
        string="Secondary Survey Report File",
        attachment=True,
        help='Attachment for the secondary portion of secondary connectivity.'
    )
    survey_report_for_secondary_filename = fields.Char(
        string="Secondary Survey File Name",
        help='Filename for the secondary survey attachment.'
    )

    # =========================
    # RESURVEY REPORT (NEW)
    # =========================
    resurvey_report = fields.Text(
        string="Resurvey Report",
        help='Resurvey notes for primary-only connections.'
    )
    resurvey_report_file = fields.Binary(
        string="Resurvey Report File",
        attachment=True,
        help='Attach supporting documents for the primary-only resurvey.'
    )
    resurvey_report_filename = fields.Char(
        string="Resurvey File Name",
        help='Filename for the primary-only resurvey attachment.'
    )

    resurvey_report_for_primary = fields.Text(
        string="Resurvey Report for Primary",
        help='Text notes for the primary portion of dual-connection resurvey.'
    )
    resurvey_report_for_primary_file = fields.Binary(
        string="Resurvey Primary Report File",
        attachment=True,
        help='Attachment for the primary portion of dual-connection resurvey.'
    )
    resurvey_report_for_primary_filename = fields.Char(
        string="Resurvey Primary File Name",
        help='Filename for the resurvey primary attachment.'
    )

    resurvey_report_for_secondary = fields.Text(
        string="Resurvey Report for Secondary",
        help='Text notes for the secondary portion of dual-connection resurvey.'
    )
    resurvey_report_for_secondary_file = fields.Binary(
        string="Resurvey Secondary Report File",
        attachment=True,
        help='Attachment for the secondary portion of dual-connection resurvey.'
    )
    resurvey_report_for_secondary_filename = fields.Char(
        string="Resurvey Secondary File Name",
        help='Filename for the resurvey secondary attachment.'
    )

    capacity_line_ids = fields.One2many(
        'isp.capacity.type',
        'own_id',
        string="Capacity Details",
    )

    def action_add_capacity_line(self):
        self.ensure_one()
        self.env['isp.capacity.type'].create({'own_id': self.id})
        return True

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'OWN Confirm'),
            ('noc_confirm', 'NOC Confirm'),
            ('done', 'Done')
        ],
        default='draft',
    )

    device_id = fields.Char()
    port_number = fields.Many2many(
        'isp.port.master',
        string='Port Number',
        help='Select one or more ports from configuration.'
    )
    device_details = fields.Char()



    def action_own_confirm(self):
        for rec in self:
            missing = []

            if not rec.device_id:
                missing.append(_("Device ID"))
            if not rec.port_number:
                missing.append(_("Port Number"))
            if not rec.device_details:
                missing.append(_("Device Details"))

            if missing:
                raise ValidationError(_(
                    "You cannot confirm this record because the following fields are missing:\n- %s"
                ) % ("\n- ".join(missing)))

            rec.state = 'confirm'

    def action_own_noc_confirm(self):
        for rec in self:
            rec.state = 'noc_confirm'

    def action_own_done(self):
        for rec in self:
            rec.state = 'done'
