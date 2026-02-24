from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class IspWorkOrder(models.Model):
    _name = 'isp.work.order'
    _description = 'ISP Work Order'
    _inherits = {'isp.survey': 'survey_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'work_order_name'
    _order = 'work_order_name desc'

    survey_id = fields.Many2one(
        'isp.survey',
        string='Survey',
        required=True,
        ondelete='cascade'
    )

    work_order_name = fields.Char(
        string='Work Order Reference',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New')
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    work_state = fields.Selection(
        [
            ('work_order', 'Work Order Created'),
            ('sell_confirm', 'Sell Submit'),
            ('marketing_confirm', 'Marketing Confirm'),
            ('marketing_revert', 'Marketing Revert'),
            ('legal_confirm', 'Legal Confirm'),
            ('legal_revert', 'Legal Revert'),
        ],
        string='Status',
        default='work_order',
        tracking=True
    )
    work_state_work_order_date = fields.Datetime(string="Work Order Created At", readonly=True, copy=False)
    work_state_sell_confirm_date = fields.Datetime(string="Sell Submit At", readonly=True, copy=False)
    work_state_marketing_confirm_date = fields.Datetime(string="Marketing Confirm At", readonly=True, copy=False)
    work_state_marketing_revert_date = fields.Datetime(string="Marketing Revert At", readonly=True, copy=False)
    work_state_legal_confirm_date = fields.Datetime(string="Legal Confirm At", readonly=True, copy=False)
    work_state_legal_revert_date = fields.Datetime(string="Legal Revert At", readonly=True, copy=False)

    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_total_amount',
        store=True
    )
    total_offer_amount = fields.Monetary(
        string='Total Offer Amount',
        currency_field='currency_id',
        compute='_compute_total_offer_amount',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer Partner',
        compute='_compute_partner',
        store=False,
        readonly=True
    )
    billing_cycle_ids = fields.One2many(
        'isp.billing.cycle',
        'work_order_id',
        string='Billing Cycle'
    )
    
    # Document fields
    cheque_image = fields.Binary(string="Cheque Image")
    cheque_image_filename = fields.Char(string="Cheque Image Filename")

    profile_image = fields.Binary(string="Profile Image")
    profile_image_filename = fields.Char(string="Profile Image Filename")

    nid_card = fields.Binary(string="NID Card")
    nid_card_filename = fields.Char(string="NID Card Filename")

    brtc_license = fields.Binary(string="BRTC License")
    brtc_license_filename = fields.Char(string="BRTC License Filename")

    trade_license = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char(string="Trade License Filename")

    contact_authorization = fields.Binary(string="Authorization")
    contact_authorization_filename = fields.Char(string="Contact Authorization Filename")

    financial_agreement = fields.Binary(string="Financial Agreement")
    financial_agreement_filename = fields.Char(string="Financial Agreement Filename")

    general_agreement = fields.Binary(string="General Agreement")
    general_agreement_filename = fields.Char(string="General Agreement Filename")
    
    billing_by = fields.Selection(
        [
            ('noc', 'NOC'),
            ('marketing', 'Marketing'),
        ],
        default='noc',
        string='Billing By'
    )
    
    cash_information = fields.Monetary(string='Cash Information')
    money_receipt = fields.Binary(string='Money Receipt')
    
    transaction_id = fields.Char(string='Mobile Money ')
    transaction_image = fields.Binary(string='Transaction Image')
    
    user_id = fields.Many2one(
        'res.users',
        string='Revert User',)
    
    revert_reason = fields.Text(string='Revert Reason')
    is_lacp = fields.Boolean(default=False, string="Is LACP")
    
    



    @api.model
    def create(self, vals):
        if vals.get('work_order_name', _('New')) == _('New'):
            vals['work_order_name'] = self.env['ir.sequence'].next_by_code('isp.work.order') or _('New')

        initial_state = vals.get('work_state') or 'work_order'
        initial_state_date_field = self._get_work_state_date_field(initial_state)
        if initial_state_date_field and not vals.get(initial_state_date_field):
            if initial_state == 'work_order' and vals.get('survey_id'):
                survey = self.env['isp.survey'].browse(vals['survey_id'])
                vals[initial_state_date_field] = survey.state_work_order_date or fields.Datetime.now()
            else:
                vals[initial_state_date_field] = fields.Datetime.now()

        return super().create(vals)

    def write(self, vals):
        if 'work_state' not in vals:
            return super().write(vals)

        new_state = vals.get('work_state')
        state_date_field = self._get_work_state_date_field(new_state)
        if not state_date_field:
            return super().write(vals)

        now = fields.Datetime.now()
        surveys_to_stop = self.filtered(
            lambda rec: rec.work_state == 'work_order'
            and new_state != 'work_order'
            and rec.survey_id
            and not rec.survey_id.state_work_order_stop_date
        ).mapped('survey_id')

        if len(self) == 1:
            if not self[state_date_field]:
                vals = dict(vals, **{state_date_field: now})
            result = super().write(vals)
            if surveys_to_stop:
                surveys_to_stop.sudo().write({'state_work_order_stop_date': now})
            return result

        for rec in self:
            rec_vals = dict(vals)
            if not rec[state_date_field]:
                rec_vals[state_date_field] = now
            super(IspWorkOrder, rec).write(rec_vals)
        if surveys_to_stop:
            surveys_to_stop.sudo().write({'state_work_order_stop_date': now})
        return True

    def _get_work_state_date_field(self, state):
        return {
            'work_order': 'work_state_work_order_date',
            'sell_confirm': 'work_state_sell_confirm_date',
            'marketing_confirm': 'work_state_marketing_confirm_date',
            'marketing_revert': 'work_state_marketing_revert_date',
            'legal_confirm': 'work_state_legal_confirm_date',
            'legal_revert': 'work_state_legal_revert_date',
        }.get(state)

    @api.depends('capacity_type_ids.capacity', 'capacity_type_ids.existing_price')
    def _compute_total_amount(self):
        for order in self:
            total = 0.0
            for line in order.capacity_type_ids:
                qty = line.capacity or 0.0
                price = line.existing_price or 0.0
                total += qty * price
            order.total_amount = total

    @api.depends('offer_capacity_type_ids.capacity', 'offer_capacity_type_ids.offer_price')
    def _compute_total_offer_amount(self):
        for order in self:
            total = 0.0
            for line in order.offer_capacity_type_ids:
                qty = line.capacity or 0.0
                price = line.offer_price or 0.0
                total += qty * price
            order.total_offer_amount = total

    def _compute_partner(self):
        Client = self.env['isp.client']
        for order in self:
            partner = False
            if order.survey_id:
                client = Client.search([('survey_id', '=', order.survey_id.id)], limit=1)
                if client and client.partner_id:
                    partner = client.partner_id.id
            order.partner_id = partner

    def action_confirm_work_order(self):
        for order in self:
            missing_price = order.capacity_type_ids.filtered(lambda l: not l.existing_price)
            if missing_price:
                raise ValidationError(_("Please set the Existing Price on every line before confirming the work order."))
            order.work_state = 'sell_confirm'
        return self.action_open_work_order()

    def action_add_capacity_line(self):
        self.ensure_one()
        if not self.survey_id:
            return True
        self.env['isp.capacity.type'].create({'survey_id': self.survey_id.id})
        return True

    def action_add_billing_cycle_line(self):
        self.ensure_one()
        self.env['isp.billing.cycle'].create({'work_order_id': self.id})
        return True

    def action_add_offer_capacity_line(self):
        self.ensure_one()
        if not self.survey_id:
            return True
        self.env['isp.offer.capacity.type'].create({'survey_id': self.survey_id.id})
        return True

    def action_open_work_order(self):
        self.ensure_one()
        form_view = self.env.ref('kio_isp_management.view_isp_work_order_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Work Order'),
            'res_model': 'isp.work.order',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_id': self.id,
            'target': 'current',
        }

    def action_view_clients(self):
        self.ensure_one()
        return self.survey_id.action_view_clients()

    def action_print_work_order(self):
        self.ensure_one()
        report = self.env.ref('kio_isp_management.action_report_isp_work_order', raise_if_not_found=False)



    def action_marketing_confirm(self):
        for order in self:
            order.work_state = 'marketing_confirm'
        return self.action_open_work_order()


    def action_marketing_revert(self):
        for order in self:
            order.work_state = 'marketing_revert'
        return self.action_open_work_order()



    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _prepare_transmission_common_vals(self):
        self.ensure_one()
        return {
            'seq_id': self.work_order_name or self.name or '',
            'district': self.district_id.name if self.district_id else '',
            'upazila': self.upazila_id.name if self.upazila_id else '',
            'area': self.area or '',
            'total_capacity': self.total_capacity or 0.0,
            'remarks': self.remarks or self.additional_notes or '',
            'latitude': self._safe_float(self.latitude),
            'longitude': self._safe_float(self.longitude),
        }

    def _copy_capacity_lines_to_nttn(self, nttn):
        for line in self.capacity_type_ids:
            line.copy({
                'transmission_id': nttn.id,
                'isp_sale_id': False,
                'own_id': False,
            })

    def _copy_capacity_lines_to_own(self, own):
        for line in self.capacity_type_ids:
            line.copy({
                'own_id': own.id,
                'isp_sale_id': False,
                'transmission_id': False,
            })

    def _ensure_transmission_records_from_links(self):
        self.ensure_one()
        selected_links = {self.primary_link, self.secondary_link}
        selected_links.discard(False)
        if not selected_links:
            return

        common_vals = self._prepare_transmission_common_vals()

        if 'nttn' in selected_links:
            TransmissionNTTN = self.env['isp.transmission.nttn'].sudo()
            nttn = TransmissionNTTN.search([('seq_id', '=', common_vals['seq_id'])], limit=1)
            if not nttn:
                nttn_vals = dict(common_vals, aggregation_point_id=self.aggregation_point_id.id or False)
                nttn = TransmissionNTTN.create(nttn_vals)
                self._copy_capacity_lines_to_nttn(nttn)

        if 'own_network' in selected_links:
            TransmissionOWN = self.env['isp.transmission.own'].sudo()
            own = TransmissionOWN.search([('seq_id', '=', common_vals['seq_id'])], limit=1)
            if not own:
                own = TransmissionOWN.create(common_vals)
                self._copy_capacity_lines_to_own(own)

    def action_legal_confirm(self):
        for order in self:
            if not order.primary_link or not order.secondary_link:
                raise ValidationError(
                    _("Please provide both Primary Link and Secondary Link before Legal Confirm.")
                )
            order._ensure_transmission_records_from_links()
            order.work_state = 'legal_confirm'
        return self.action_open_work_order()


    def action_legal_revert(self):
        for order in self:
            order.work_state = 'legal_revert'
        return self.action_open_work_order()
