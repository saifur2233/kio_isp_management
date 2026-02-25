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

    # State timeline timestamps (for stopwatch statusbar)
    state_draft_date = fields.Datetime(string="Draft At", readonly=True, copy=False)
    state_confirm_date = fields.Datetime(string="OWN Confirm At", readonly=True, copy=False)
    state_noc_confirm_date = fields.Datetime(string="NOC Confirm At", readonly=True, copy=False)
    state_done_date = fields.Datetime(string="Done At", readonly=True, copy=False)

    # Stored durations between stage transitions
    dur_draft_to_confirm_sec = fields.Integer(
        string="Draft → Confirm (sec)",
        compute="_compute_state_durations",
        store=True,
    )
    dur_confirm_to_noc_sec = fields.Integer(
        string="Confirm → NOC Confirm (sec)",
        compute="_compute_state_durations",
        store=True,
    )
    dur_noc_to_done_sec = fields.Integer(
        string="NOC Confirm → Done (sec)",
        compute="_compute_state_durations",
        store=True,
    )
    dur_draft_to_confirm_display = fields.Char(
        string="Draft → Confirm",
        compute="_compute_state_durations",
        store=True,
    )
    dur_confirm_to_noc_display = fields.Char(
        string="Confirm → NOC Confirm",
        compute="_compute_state_durations",
        store=True,
    )
    dur_noc_to_done_display = fields.Char(
        string="NOC Confirm → Done",
        compute="_compute_state_durations",
        store=True,
    )

    device_id = fields.Char()
    port_number = fields.Many2many(
        'isp.port.master',
        string='Port Number',
        help='Select one or more ports from configuration.'
    )
    device_details = fields.Char()
    is_lacp = fields.Boolean(string='Is LACP')


    def _format_seconds(self, sec):
        total_ms = int(round(float(sec or 0) * 1000))
        if total_ms < 0:
            total_ms = 0
        hours, remainder = divmod(total_ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, milliseconds = divmod(remainder, 1000)
        centiseconds = milliseconds // 10
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    @api.model
    def create(self, vals):
        now = fields.Datetime.now()
        initial_state = vals.get('state') or 'draft'

        if not vals.get('state_draft_date'):
            vals['state_draft_date'] = now

        initial_state_date_field = self._get_state_date_field(initial_state)
        if initial_state_date_field and not vals.get(initial_state_date_field):
            vals[initial_state_date_field] = vals.get('state_draft_date') or now

        return super().create(vals)

    def write(self, vals):
        if 'state' not in vals:
            return super().write(vals)

        new_state = vals.get('state')
        state_date_field = self._get_state_date_field(new_state)
        if not state_date_field:
            return super().write(vals)

        now = fields.Datetime.now()
        if len(self) == 1:
            rec = self
            write_vals = dict(vals)
            if not rec.state_draft_date:
                write_vals['state_draft_date'] = rec.create_date or now
            if not rec[state_date_field]:
                write_vals[state_date_field] = now
            return super().write(write_vals)

        for rec in self:
            write_vals = dict(vals)
            if not rec.state_draft_date:
                write_vals['state_draft_date'] = rec.create_date or now
            if not rec[state_date_field]:
                write_vals[state_date_field] = now
            super(IspTransmissionOwn, rec).write(write_vals)
        return True

    def _get_state_date_field(self, state):
        return {
            'draft': 'state_draft_date',
            'confirm': 'state_confirm_date',
            'noc_confirm': 'state_noc_confirm_date',
            'done': 'state_done_date',
        }.get(state)

    @api.depends(
        'state_draft_date',
        'state_confirm_date',
        'state_noc_confirm_date',
        'state_done_date',
        'create_date',
    )
    def _compute_state_durations(self):
        for rec in self:
            draft_dt = rec.state_draft_date or rec.create_date
            confirm_dt = rec.state_confirm_date
            noc_dt = rec.state_noc_confirm_date
            done_dt = rec.state_done_date

            sec1 = 0
            if draft_dt and confirm_dt and confirm_dt > draft_dt:
                sec1 = int((confirm_dt - draft_dt).total_seconds())

            sec2 = 0
            if confirm_dt and noc_dt and noc_dt > confirm_dt:
                sec2 = int((noc_dt - confirm_dt).total_seconds())

            sec3 = 0
            if noc_dt and done_dt and done_dt > noc_dt:
                sec3 = int((done_dt - noc_dt).total_seconds())

            rec.dur_draft_to_confirm_sec = sec1
            rec.dur_confirm_to_noc_sec = sec2
            rec.dur_noc_to_done_sec = sec3
            rec.dur_draft_to_confirm_display = self._format_seconds(sec1) if sec1 else ""
            rec.dur_confirm_to_noc_display = self._format_seconds(sec2) if sec2 else ""
            rec.dur_noc_to_done_display = self._format_seconds(sec3) if sec3 else ""



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
