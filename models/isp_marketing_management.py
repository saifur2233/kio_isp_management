# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .district_selection import DIVISION_SELECTION


class IspMarketingManagement(models.Model):
    _name = 'isp.marketing.management'
    _description = 'ISP Sale'
    _rec_name = 'client_id'
    _order = 'name desc'

    # -------------------------------------------------------------------------
    # BASIC
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help="Unique reference number for this ISP sale.\nAutomatically generated when saving the record."
    )

    client_id = fields.Many2one(
        'isp.client',
        string='Customer',
        help="Select the customer who is purchasing this ISP connection."
    )

    user_id = fields.Many2one(
        'res.users',
        string='Salepersons',
        default=lambda self: self.env.user,
        help="The salesperson responsible for this connection sale.\nDefaults to the current user."
    )

    active = fields.Boolean(default=True, invisible=True)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, copy=False)


    # -------------------------------------------------------------------------
    # AUTO FROM SURVEY (RELATED)
    # -------------------------------------------------------------------------
    # Survey reference (optional but helpful)
    survey_id = fields.Many2one(
        'isp.survey',
        string="Survey",
        related='client_id.survey_id',
        store=True,
        readonly=True
    )

    latitude = fields.Char(
        string="Latitude",
        tracking=True,
        related="client_id.survey_id.latitude",
        store=True,
        readonly=True,
        help="Auto from Survey"
    )

    longitude = fields.Char(
        string="Longitude",
        tracking=True,
        related="client_id.survey_id.longitude",
        store=True,
        readonly=True,
        help="Auto from Survey"
    )

    area = fields.Char(
        string="Area",
        related="client_id.survey_id.area",
        store=True,
        readonly=True,
        help="Auto from Survey"
    )

    remarks = fields.Text(
        string="Remarks",
        related="client_id.survey_id.remarks",
        store=True,
        readonly=True,
        help="Auto from Survey"
    )

    additional_notes = fields.Text(
        string="Additional Notes",
        help="Extra information for the customer or installation team.\nCan be printed on quotation or work order if needed."
    )

    # Location from Client (you already had)
    division = fields.Selection(
        related='client_id.division',
        selection=DIVISION_SELECTION,
        string='Division',
        store=True,
        readonly=True
    )

    district_id = fields.Many2one(
        'isp.district',
        string='District',
        related='client_id.district_id',
        store=True,
        readonly=True
    )

    upazila_id = fields.Many2one(
        'isp.upazila',
        string='Upazila',
        related='client_id.upazila_id',
        store=True,
        readonly=True
    )

    # -------------------------------------------------------------------------
    # CAPACITY (COPY FROM SURVEY VIA ONCHANGE)
    # -------------------------------------------------------------------------
    capacity_type_ids = fields.One2many(
        'isp.capacity.type',
        'isp_sale_id',
        string='Capacity Types',
        help="Capacity lines copied from Survey when Customer is selected.\nEditable in Marketing."
    )

    total_capacity = fields.Integer(
        string='Total Capacity',
        compute='_compute_total_capacity',
        help="Automatically calculated total bandwidth in Mbps.\nGB values are converted using MB factor from system settings."
    )

    # -------------------------------------------------------------------------
    # REPORTS (YOUR FIELDS)
    # -------------------------------------------------------------------------
    survey_report = fields.Text(string="Survey Report")
    survey_report_file = fields.Binary(string="Survey Report File", attachment=True)
    survey_report_filename = fields.Char(string="Survey Report Filename")

    survey_report_for_primary = fields.Text(string="Survey Report for Primary")
    survey_report_for_primary_file = fields.Binary(string="Primary Survey Report File", attachment=True)
    survey_report_for_primary_filename = fields.Char(string="Primary Survey Report Filename")

    survey_report_for_secondary = fields.Text(string="Survey Report for Secondary")
    survey_report_for_secondary_file = fields.Binary(string="Secondary Survey Report File", attachment=True)
    survey_report_for_secondary_filename = fields.Char(string="Secondary Survey Report Filename")

    resurvey_report = fields.Text(string="Resurvey Report")
    resurvey_report_file = fields.Binary(string="Resurvey Report File", attachment=True)
    resurvey_report_filename = fields.Char(string="Resurvey File Name")

    resurvey_report_for_primary = fields.Text(string="Resurvey Report for Primary")
    resurvey_report_for_primary_file = fields.Binary(string="Resurvey Primary Report File", attachment=True)
    resurvey_report_for_primary_filename = fields.Char(string="Resurvey Primary File Name")

    resurvey_report_for_secondary = fields.Text(string="Resurvey Report for Secondary")
    resurvey_report_for_secondary_file = fields.Binary(string="Resurvey Secondary Report File", attachment=True)
    resurvey_report_for_secondary_filename = fields.Char(string="Resurvey Secondary File Name")

    # -------------------------------------------------------------------------
    # SALE ORDER / STATUS
    # -------------------------------------------------------------------------
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('create_sale_order', 'Create Sale Order'),
            ('sent_to_transmission', 'Sent To Transmission'),
        ],
        string="Status",
        default="draft",
    )

    visit_type_id = fields.Many2one(
        'isp.visit.type',
        string="Visit Type",
        domain="[('active', '=', True)]",
    )

    work_order_type_id = fields.Many2one('isp.work.order.type', string="Work Order Type")
    cheque_amount = fields.Integer()
    cash_amount = fields.Integer()

    # -------------------------------------------------------------------------
    # ONCHANGE: when client selected -> copy survey capacity lines into marketing
    # -------------------------------------------------------------------------
    @api.onchange('client_id')
    def _onchange_client_id_copy_survey_data(self):
        for rec in self:
            # reset fields first (optional but clean)
            rec.capacity_type_ids = [(5, 0, 0)]
            rec.cheque_amount = 0.0
            rec.cash_amount = 0.0
            rec.visit_type_id = False
            rec.work_order_type_id = False

            # additional_notes: only overwrite if empty (so user can write own)
            if not rec.additional_notes:
                rec.additional_notes = False

            if not rec.client_id or not rec.client_id.survey_id:
                return

            survey = rec.client_id.survey_id

            # ✅ Copy simple fields from survey
            rec.cheque_amount = survey.cheque_amount or 0.0
            rec.cash_amount = survey.cash_amount or 0.0
            rec.visit_type_id = survey.visit_id.id if survey.visit_id else False
            rec.work_order_type_id = survey.work_id.id if survey.work_id else False

            # ✅ Copy additional notes (only if marketing empty)
            if not rec.additional_notes:
                rec.additional_notes = survey.additional_notes or False

            # ✅ Copy capacity lines from survey
            new_lines = []
            for line in survey.capacity_type_ids:
                new_lines.append((0, 0, {
                    'type_id': line.type_id.id if line.type_id else False,
                    'parameter': line.parameter,
                    'capacity': line.capacity,
                }))
            rec.capacity_type_ids = new_lines

    # -------------------------------------------------------------------------
    # COMPUTE TOTAL CAPACITY
    # -------------------------------------------------------------------------
    @api.depends('capacity_type_ids', 'capacity_type_ids.parameter', 'capacity_type_ids.capacity')
    def _compute_total_capacity(self):
        config_param = self.env['ir.config_parameter'].sudo()
        mb_value = config_param.get_param('isp.mb_value', default='0')

        try:
            mb_factor = float(mb_value)
        except (TypeError, ValueError):
            mb_factor = 0.0

        for sale in self:
            total_capacity = 0

            for capacity_line in sale.capacity_type_ids:
                capacity = capacity_line.capacity or 0
                if not capacity:
                    continue

                if capacity_line.parameter == 'gb':
                    if mb_factor <= 0.0:
                        raise ValidationError(
                            _("Please configure a positive 'MB Value' in Settings > ISP Configuration to convert GB capacities.")
                        )
                    total_capacity += int(capacity * mb_factor)
                else:
                    total_capacity += capacity

            sale.total_capacity = total_capacity

    # -------------------------------------------------------------------------
    # CREATE: SEQUENCE
    # -------------------------------------------------------------------------
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('isp.marketing.management') or 'New'
        return super().create(vals)

    # -------------------------------------------------------------------------
    # CONSTRAINT: at least one capacity
    # -------------------------------------------------------------------------
    @api.constrains('capacity_type_ids')
    def _check_at_least_one_capacity(self):
        for record in self:
            if not record.capacity_type_ids:
                raise ValidationError(_("At least one Capacity Type is required."))

    # -------------------------------------------------------------------------
    # BUTTONS
    # -------------------------------------------------------------------------
    def action_create_sale_order(self):
        self.ensure_one()
        self.state = 'create_sale_order'

        order_lines = []
        for capacity in self.capacity_type_ids:
            if capacity.type_id:
                product = self.env['product.product'].search([
                    ('name', '=', capacity.type_id.name),
                    ('type', '=', 'service')
                ], limit=1)

                if not product:
                    product = self.env['product.product'].create({
                        'name': capacity.type_id.name,
                        'type': 'service',
                        'sale_ok': True,
                        'default_code': capacity.type_id.name.replace(' ', '_').upper(),
                    })
            else:
                product = self.env['product.product'].search([
                    ('name', '=', 'ISP Connection'),
                    ('type', '=', 'service')
                ], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': 'ISP Connection',
                        'type': 'service',
                        'sale_ok': True,
                    })

            description = capacity.parameter.upper() if capacity.parameter else ""

            order_lines.append((0, 0, {
                'product_id': product.id,
                'name': description,
                'product_uom_qty': capacity.capacity,
                'price_unit': 0.0,
            }))

        partner = self.client_id.partner_id
        if not partner:
            raise ValidationError(_("This client has no linked Partner. Please create/link partner first."))

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,  # ✅ standard field in sale.order
            'origin': self.name,
            'order_line': order_lines,
        })

        self.sale_order_id = sale_order.id

        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_send_to_transmission(self):
        """
        Your existing logic kept as-is
        """
        self.ensure_one()

        need_nttn = True
        need_own = True

        common_vals = {
            'marketing_id': self.id,
            'seq_id': self.name,
            'district': self.district_id.name if self.district_id else '',
            'upazila': self.upazila_id.name if self.upazila_id else '',
            'area': self.area or '',
            'total_capacity': self.total_capacity or 0.0,
            'remarks': self.remarks or '',
            'latitude': float(self.latitude) if self.latitude else 0.0,
            'longitude': float(self.longitude) if self.longitude else 0.0,
        }

        created_nttn = None
        created_own = None

        if need_nttn:
            TransmissionNTTN = self.env['isp.transmission.nttn'].sudo()
            nttn = TransmissionNTTN.search([('marketing_id', '=', self.id)], limit=1)
            if not nttn:
                nttn = TransmissionNTTN.create(common_vals)
                for line in self.capacity_type_ids:
                    line.copy({
                        'transmission_id': nttn.id,
                        'isp_sale_id': False,
                        'own_id': False,
                    })
            created_nttn = nttn

        if need_own:
            TransmissionOWN = self.env['isp.transmission.own'].sudo()
            own = TransmissionOWN.search([('marketing_id', '=', self.id)], limit=1)
            if not own:
                own = TransmissionOWN.create(common_vals)
                for line in self.capacity_type_ids:
                    line.copy({
                        'own_id': own.id,
                        'isp_sale_id': False,
                        'transmission_id': False,
                    })
            created_own = own

        self.state = 'sent_to_transmission'

        if created_nttn:
            return {
                'name': _('NTTN Transmission'),
                'type': 'ir.actions.act_window',
                'res_model': 'isp.transmission.nttn',
                'view_mode': 'form',
                'res_id': created_nttn.id,
                'target': 'current',
            }

        return {
            'name': _('OWN Transmission'),
            'type': 'ir.actions.act_window',
            'res_model': 'isp.transmission.own',
            'view_mode': 'form',
            'res_id': created_own.id,
            'target': 'current',
        }

    def action_create_invoice(self):
        self.ensure_one()

        # partner check
        partner = self.client_id.partner_id
        if not partner:
            raise ValidationError(_("This client has no linked Partner. Please create/link partner first."))

        # If already created -> open it
        if self.invoice_id:
            return {
                'name': _('Customer Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
                'target': 'current',
            }

        # invoice lines from capacity_type_ids
        lines = []
        for capacity in self.capacity_type_ids:
            # product from type_id
            if capacity.type_id:
                product = self.env['product.product'].search([
                    ('name', '=', capacity.type_id.name),
                    ('type', '=', 'service')
                ], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': capacity.type_id.name,
                        'type': 'service',
                        'sale_ok': True,
                        'invoice_policy': 'order',
                    })
            else:
                product = self.env['product.product'].search([
                    ('name', '=', 'ISP Connection'),
                    ('type', '=', 'service')
                ], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': 'ISP Connection',
                        'type': 'service',
                        'sale_ok': True,
                        'invoice_policy': 'order',
                    })

            qty = capacity.capacity or 1
            line_name = capacity.parameter.upper() if capacity.parameter else product.name

            lines.append((0, 0, {
                'product_id': product.id,
                'name': line_name,
                'quantity': qty,
                'price_unit': 0.0,  # এখানে price set করবেন
            }))

        if not lines:
            raise ValidationError(_("No capacity lines found to create invoice lines."))

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_origin': self.name,
            'invoice_line_ids': lines,
        })

        self.invoice_id = move.id

        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': move.id,
            'target': 'current',
        }
