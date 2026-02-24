from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .district_selection import DIVISION_SELECTION


class IspSurvey(models.Model):
    _name = 'isp.survey'
    _description = 'ISP Survey'
    _order = 'name desc'
    _rec_name = 'customer_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ────────────────────────────────────────────────
    # Fields
    # ────────────────────────────────────────────────

    active = fields.Boolean(default=True, invisible=True)

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help="Unique reference number for this ISP sale.\n"
             "Automatically generated when saving the record."
    )

    latitude = fields.Char(string="Latitude", tracking=True)
    longitude = fields.Char(string="Longitude", tracking=True)
    area = fields.Char(string='Area')
    cheque_amount = fields.Integer()
    cash_amount = fields.Integer()
    additional_notes = fields.Text()
    remarks = fields.Text()


    total_capacity = fields.Integer(
        string='Total Capacity',
        compute='_compute_total_capacity',
    )
    total_existing_price = fields.Integer(
        string='Total Existing Price',
        compute='_compute_total_existing_price',
    )

    visiting_type = fields.Selection(
        [('phone_call', 'Phone Call'), ('office_visit', 'Office Visit')],
        string='Visiting Type',
        default='phone_call'
    )
    primary_link = fields.Selection(
        [('nttn', 'NTTN'), ('own_network', 'Own Network')],
        string='Primary Link'
    )
    secondary_link = fields.Selection(
        [('nttn', 'NTTN'), ('own_network', 'Own Network')],
        string='Secondary Link'
    )
    aggregation_point_id = fields.Many2one(
        'isp.aggregation.point',
        string='Aggregation Point'
    )
    switch_model_no = fields.Char(
        string='Switch Model No',
        related='aggregation_point_id.switch_model_no',
        readonly=True
    )
    port_number = fields.Char(
        string='Port Number',
    )
    sfp_type = fields.Char(string='SFP Type')
    pop_latitude = fields.Char(
        string='POP Latitude',
        related='aggregation_point_id.pop_latitude',
        readonly=True
    )
    pop_longitude = fields.Char(
        string='POP Longitude',
        related='aggregation_point_id.pop_longitude',
        readonly=True
    )
    distance_km = fields.Float(
        string='Air Distance (km)',
        compute='_compute_distance_km',
        store=False,
        readonly=True
    )
    road_distance_km = fields.Float(string='Road Distance (km)')
    map_url = fields.Char(
        string='Google Map Link',
        compute='_compute_distance_km',
        store=False,
        readonly=True
    )
    customer_name = fields.Char(string='Customer')
    designation = fields.Char(string='Designation')
    phone = fields.Char()
    email = fields.Char()
    technical_person_name = fields.Char(string='Name')
    technical_person_phone = fields.Char(string='Phone Number')
    technical_person_email = fields.Char(string='Email ID')
    technical_person_designation = fields.Char(string='Designation')
    billing_person_name = fields.Char(string='Name')
    billing_person_phone = fields.Char(string='Phone Number')
    billing_person_email = fields.Char(string='Email ID')
    billing_person_designation = fields.Char(string='Designation')

    client_count = fields.Integer(string="Clients", compute="_compute_client_count")
    work_order_id = fields.Many2one('isp.work.order', string='Work Order', compute='_compute_work_order', store=False)
    
    # ────────────────────────────────────────────────
    # ✅ STATES
    # ────────────────────────────────────────────────
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Survey Done'),
            ('work_order', 'Work Order Created'),
        ],
        string="Status",
        default='draft',
        tracking=True
    )

    # ────────────────────────────────────────────────
    # ✅ STATE TIME TRACKING (timestamps)
    # ────────────────────────────────────────────────
    state_draft_date = fields.Datetime(string="Draft At", readonly=True, copy=False)
    state_done_date = fields.Datetime(string="Survey Done At", readonly=True, copy=False)
    state_work_order_date = fields.Datetime(string="Work Order Created At", readonly=True, copy=False)
    state_work_order_stop_date = fields.Datetime(string="Work Order Stage Stopped At", readonly=True, copy=False)

    # ────────────────────────────────────────────────
    # ✅ STATE DURATIONS (stored + display for OWL widget)
    # ────────────────────────────────────────────────
    dur_draft_to_done_sec = fields.Integer(
        string="Draft → Done (sec)",
        compute="_compute_state_durations",
        store=True
    )
    dur_done_to_work_sec = fields.Integer(
        string="Done → Work (sec)",
        compute="_compute_state_durations",
        store=True
    )

    dur_draft_to_done_display = fields.Char(
        string="Draft → Done",
        compute="_compute_state_durations",
        store=True
    )
    dur_done_to_work_display = fields.Char(
        string="Done → Work",
        compute="_compute_state_durations",
        store=True
    )
    dur_work_order_active_sec = fields.Integer(
        string="Work Order Active (sec)",
        compute="_compute_state_durations",
        store=True
    )
    dur_work_order_active_display = fields.Char(
        string="Work Order Active",
        compute="_compute_state_durations",
        store=True
    )

     # ────────────────────────────────────────────────
    user_id = fields.Many2one('res.users', string='Salepersons', default=lambda self: self.env.user)
    visit_id = fields.Many2one('isp.visit.type', string='Visit Type')
    work_id = fields.Many2one('isp.work.order.type', string='Work Order Type')
    division = fields.Selection(DIVISION_SELECTION, string='Division')
    district_id = fields.Many2one('isp.district', string='District')
    upazila_id = fields.Many2one('isp.upazila', string='Upazila', domain="[('district_id', '=', district_id)]")
    existing_upstream = fields.Char(string = "Existing Upstream")

    capacity_type_ids = fields.One2many('isp.capacity.type', 'survey_id', string='Capacity Types')
    offer_capacity_type_ids = fields.One2many(
        'isp.offer.capacity.type',
        'survey_id',
        string='Offer Product Details'
    )
    existing_mac_detail_ids = fields.One2many(
        'isp.mac.detail',
        'survey_existing_id',
        string='Existing MAC Details'
    )
    offer_mac_detail_ids = fields.One2many(
        'isp.mac.detail',
        'survey_offer_id',
        string='Offer MAC Details'
    )
    
    client_type = fields.Selection([
        ('mac', 'Mac'),
        ('bandwith', 'Bandwidth'),
        ('corporate', 'Corporate')
    ])

    # ────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────

    def _format_seconds(self, sec):
        """Return stopwatch-like duration: HH:MM:SS.cc (2-digit sub-seconds)."""
        total_ms = int(round(float(sec or 0) * 1000))
        if total_ms < 0:
            total_ms = 0

        hours, remainder = divmod(total_ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, milliseconds = divmod(remainder, 1000)
        centiseconds = milliseconds // 10
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    # ────────────────────────────────────────────────
    # create() - set initial draft timestamp
    # ────────────────────────────────────────────────

    @api.model
    def create(self, vals):
        """
        Auto generate sequence & set Draft timestamp on create.
        """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('isp.survey') or _('New')

        if not vals.get('state_draft_date'):
            vals['state_draft_date'] = fields.Datetime.now()

        return super().create(vals)

    # ────────────────────────────────────────────────
    # write() - capture timestamps when state changes
    # ────────────────────────────────────────────────

    def write(self, vals):
        if 'state' in vals:
            new_state = vals.get('state')
            now = fields.Datetime.now()

            for rec in self:
                if not rec.state_draft_date:
                    rec.state_draft_date = rec.create_date or now

            if new_state == 'done':
                for rec in self:
                    if not rec.state_done_date:
                        vals.setdefault('state_done_date', now)

            if new_state == 'work_order':
                for rec in self:
                    if not rec.state_work_order_date:
                        vals.setdefault('state_work_order_date', now)

        return super().write(vals)

    # ────────────────────────────────────────────────
    # ✅ Compute state durations
    # ────────────────────────────────────────────────
    @api.depends('state_draft_date', 'state_done_date', 'state_work_order_date', 'state_work_order_stop_date', 'create_date')
    def _compute_state_durations(self):
        for rec in self:
            draft_dt = rec.state_draft_date or rec.create_date
            done_dt = rec.state_done_date
            work_dt = rec.state_work_order_date
            work_stop_dt = rec.state_work_order_stop_date

            sec1 = 0
            if draft_dt and done_dt:
                sec1 = int((done_dt - draft_dt).total_seconds())

            sec2 = 0
            if done_dt and work_dt:
                sec2 = int((work_dt - done_dt).total_seconds())

            sec3 = 0
            if work_dt and work_stop_dt and work_stop_dt > work_dt:
                sec3 = int((work_stop_dt - work_dt).total_seconds())

            rec.dur_draft_to_done_sec = sec1
            rec.dur_done_to_work_sec = sec2
            rec.dur_work_order_active_sec = sec3
            rec.dur_draft_to_done_display = self._format_seconds(sec1) if sec1 else ""
            rec.dur_done_to_work_display = self._format_seconds(sec2) if sec2 else ""
            rec.dur_work_order_active_display = self._format_seconds(sec3) if sec3 else ""

    # ────────────────────────────────────────────────

    @api.depends('capacity_type_ids', 'capacity_type_ids.parameter', 'capacity_type_ids.capacity')
    def _compute_total_capacity(self):
        """
        Compute total capacity in Mbps.
        Converts GB values to Mbps using system parameter 'isp.mb_value'.
        Raises error if conversion factor is missing or invalid when GB is used.
        """
        config_param = self.env['ir.config_parameter'].sudo()
        mb_value = config_param.get_param('isp.mb_value', default='0')

        try:
            mb_factor = float(mb_value)
        except (TypeError, ValueError):
            mb_factor = 0.0

        for sale in self:
            total_capacity = 0
            has_gb_capacity = False

            for capacity_line in sale.capacity_type_ids:
                capacity = capacity_line.capacity or 0
                if not capacity:
                    continue

                if capacity_line.parameter == 'gb':
                    has_gb_capacity = True
                    if mb_factor <= 0.0:
                        raise ValidationError(
                            _("Please configure a positive 'MB Value' in Settings > ISP Configuration to convert GB capacities.")
                        )
                    total_capacity += int(capacity * mb_factor)
                else:  # mb
                    total_capacity += capacity

            sale.total_capacity = total_capacity

    

    @api.depends('capacity_type_ids', 'capacity_type_ids.capacity', 'capacity_type_ids.existing_price')
    def _compute_total_existing_price(self):
        for sale in self:
            total = 0.0
            for capacity_line in sale.capacity_type_ids:
                capacity = capacity_line.capacity or 0.0
                price = capacity_line.existing_price or 0.0
                total += capacity * price
            sale.total_existing_price = total

    # ────────────────────────────────────────────────
    # Buttons
    # ────────────────────────────────────────────────

    def action_add_capacity_line(self):
        self.ensure_one()
        self.env['isp.capacity.type'].create({'survey_id': self.id})
        return True

    def action_add_offer_capacity_line(self):
        self.ensure_one()
        self.env['isp.offer.capacity.type'].create({'survey_id': self.id})
        return True

    def action_add_existing_mac_line(self):
        self.ensure_one()
        self.env['isp.mac.detail'].create({'survey_existing_id': self.id})
        return True

    def action_add_offer_mac_line(self):
        self.ensure_one()
        self.env['isp.mac.detail'].create({'survey_offer_id': self.id})
        return True

    # ────────────────────────────────────────────────
    # Distance compute
    # ────────────────────────────────────────────────

    @api.depends('latitude', 'longitude', 'pop_latitude', 'pop_longitude')
    def _compute_distance_km(self):
        for record in self:
            record.distance_km = 0.0
            record.map_url = False

            try:
                lat1 = float(record.latitude or 0.0)
                lon1 = float(record.longitude or 0.0)
                lat2 = float(record.pop_latitude or 0.0)
                lon2 = float(record.pop_longitude or 0.0)
            except (TypeError, ValueError):
                continue

            if not all([lat1, lon1, lat2, lon2]):
                continue

            # Haversine formula for distance in kilometers.
            from math import radians, sin, cos, sqrt, atan2
            r = 6371.0
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            record.distance_km = r * c
            record.map_url = (
                "https://www.google.com/maps/dir/?api=1&origin="
                f"{lat1},{lon1}&destination={lat2},{lon2}"
            )

    # ────────────────────────────────────────────────

    # @api.constrains('capacity_type_ids')
    # def _check_at_least_one_capacity(self):
    #     """
    #     Ensure that at least one capacity type line exists.
    #     Prevents saving a survey record without any bandwidth information.
    #     """
    #     for record in self:
    #         if not record.capacity_type_ids:
    #             raise ValidationError(
    #                 _("At least one Capacity Type is required.")
    #             )

    # ────────────────────────────────────────────────

    # ────────────────────────────────────────────────
    # Workflow methods
    # ────────────────────────────────────────────────
    def action_mark_survey_done(self):
        """
        Mark survey as done and ensure a customer record exists.
        Automatically creates a new ISP Client if needed.
        """
        self.ensure_one()
        self._get_or_create_client_from_survey()
        self.state = 'done'
        return self._action_open_survey_form()

    def _ensure_client_creation_requirements(self):
        missing = []
        if not self.customer_name:
            missing.append(_("Customer Name"))
        if not self.email:
            missing.append(_("Email"))
        if not self.phone:
            missing.append(_("Phone/Mobile"))
        if missing:
            raise ValidationError(
                _("You cannot finish this survey because the following fields are missing:\n- %s") %
                ("\n- ".join(missing))
            )

    def _get_or_create_client_from_survey(self):
        """
        Find or create an ISP Client record from this survey.
        """
        self.ensure_one()
        self._ensure_client_creation_requirements()

        Client = self.env['isp.client'].sudo()

        # Prefer client already linked to this survey
        client = Client.search([('survey_id', '=', self.id)], limit=1)
        if client:
            return client

        email = (self.email or '').strip().lower()
        if not email:
            raise ValidationError(_("Email is required to create a client."))

        # Reuse any existing client with same email
        client = Client.search([('email', '=', email)], limit=1)
        if client:
            client.sudo().write({'survey_id': self.id})
            return client

        vals = {
            'survey_id': self.id,
            'client_name': self.customer_name,
            'email': email,
            'mobile': self.phone,
            'division': self.division,
            'district_id': self.district_id.id if self.district_id else False,
            'upazila_id': self.upazila_id.id if self.upazila_id else False,
            'technical_address': self.area,
            'user_id': self.user_id.id if self.user_id else False,
        }
        return Client.create(vals)

    def _action_open_survey_form(self):
        form_view = self.env.ref('kio_isp_management.view_isp_survey_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Survey'),
            'res_model': 'isp.survey',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_id': self.id,
            'target': 'current',
        }

    # ────────────────────────────────────────────────

    def action_open_work_order(self):
        """
        Open the Work Order form and mark this survey as having a work order.
        """
        self.ensure_one()
        if self.state == 'draft':
            raise ValidationError(_("Please mark the survey as done before creating a work order."))

        if self.state != 'work_order':
            self.state = 'work_order'

        WorkOrder = self.env['isp.work.order'].sudo()
        work_order = WorkOrder.search([('survey_id', '=', self.id)], limit=1)
        if not work_order:
            work_order = WorkOrder.create({'survey_id': self.id})

        if not self.capacity_type_ids and self.offer_capacity_type_ids:
            Capacity = self.env['isp.capacity.type'].sudo()
            for offer_line in self.offer_capacity_type_ids:
                Capacity.create({
                    'survey_id': self.id,
                    'type_id': offer_line.type_id.id,
                    'parameter': offer_line.parameter,
                    'capacity': offer_line.capacity,
                    'buffer_bandwidth': offer_line.buffer_bandwidth,
                    'existing_price': offer_line.offer_price,
                })

        self.work_order_id = work_order

        form_view = self.env.ref('kio_isp_management.view_isp_work_order_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Work Order'),
            'res_model': 'isp.work.order',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_id': work_order.id,
            'target': 'current',
        }

    def _compute_work_order(self):
        WorkOrder = self.env['isp.work.order']
        for rec in self:
            work_order = WorkOrder.search([('survey_id', '=', rec.id)], limit=1)
            rec.work_order_id = work_order

    # ────────────────────────────────────────────────

    def _compute_client_count(self):
        Client = self.env['isp.client']
        for rec in self:
            rec.client_count = Client.search_count([('survey_id', '=', rec.id)])

    def action_view_clients(self):
        """
        Open list view of all clients that were created from this survey.
        Shows tree and form views, filtered by current survey record.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clients'),
            'res_model': 'isp.client',
            'view_mode': 'tree,form',
            'domain': [('survey_id', '=', self.id)],
            'context': {'default_survey_id': self.id},
            'target': 'current',
        }

    # ────────────────────────────────────────────────

    @api.depends('stage_id', 'stage_id.is_last_stage')
    def _compute_is_last_stage(self):
        """
        Mirror the stage's `is_last_stage` flag onto the survey itself so the view
        can decide whether to display the Create Client button without duplicating
        stage logic in XML.
        """
        for record in self:
            record.is_last_stage = bool(record.stage_id and record.stage_id.is_last_stage)
