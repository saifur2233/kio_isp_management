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

    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_total_amount',
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
    
    



    @api.model
    def create(self, vals):
        if vals.get('work_order_name', _('New')) == _('New'):
            vals['work_order_name'] = self.env['ir.sequence'].next_by_code('isp.work.order') or _('New')
        return super().create(vals)

    @api.depends('capacity_type_ids.capacity', 'capacity_type_ids.existing_price')
    def _compute_total_amount(self):
        for order in self:
            total = 0.0
            for line in order.capacity_type_ids:
                qty = line.capacity or 0.0
                price = line.existing_price or 0.0
                total += qty * price
            order.total_amount = total

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
            order.work_state = 'work_order_confirmed'
        return self.action_open_work_order()

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
        print("Button Clicked By Admin")


    def action_marketing_revert(self):
        print("Button Clicked By Admin")


    
    def action_legal_confirm(self):
        print("Button Clicked By Admin")


    def action_legal_revert(self):
        print("Button Clicked By Admin")
