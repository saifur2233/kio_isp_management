from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .district_selection import DIVISION_SELECTION


class IspClient(models.Model):
    _name = 'isp.client'
    _description = 'ISP Client'
    _order = 'name desc'
    _rec_name = 'client_name'

    # ────────────────────────────────────────────────
    # Fields
    # ────────────────────────────────────────────────

    name = fields.Char(
        string='Client ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    client_name = fields.Char(string='Client Name')
    email = fields.Char(string='Email')
    password = fields.Char(string='Password')
    password_confirmation = fields.Char(string='Password Confirmation')
    mobile = fields.Char(string='Mobile')
    organization_name = fields.Char(string='Organization Name')
    license_id = fields.Many2one('isp.license', string='License Type')

    division = fields.Selection(DIVISION_SELECTION, string='Division')
    district_id = fields.Many2one(
        'isp.district',
        string='District',
        help="Only districts that belong to the selected division are available."
    )
    upazila_id = fields.Many2one(
        'isp.upazila',
        string='Upazila',
        domain="[('district_id', '=', district_id)]",
        help="Only upazilas from the selected district are available."
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

    contact_authorization = fields.Binary(string="Contact Authorization")
    contact_authorization_filename = fields.Char(string="Contact Authorization Filename")

    financial_agreement = fields.Binary(string="Financial Agreement")
    financial_agreement_filename = fields.Char(string="Financial Agreement Filename")

    general_agreement = fields.Binary(string="General Agreement")
    general_agreement_filename = fields.Char(string="General Agreement Filename")

    contact_person_ids = fields.One2many('isp.client.contact', 'client_id', string="Contact Persons")

    technical_address = fields.Text(string="Address")
    technical_mobile = fields.Char(string="Mobile")
    technical_email = fields.Char(string="Email")
    survey_id = fields.Many2one('isp.survey', string="Survey", index=True, ondelete='set null')

    client_type_id = fields.Many2one(
        'isp.client.type',
        string='Client Type',
        options="{'no_create': True}"
    )

    support_team_id = fields.Many2one(
        'isp.support.team',
        string='Support Team',
        options="{'no_create': True}"
    )

    active = fields.Boolean(default=True, invisible=True)

    user_id = fields.Many2one('res.users', string='Marketing KAM')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, copy=False)
    portal_user_id = fields.Many2one('res.users', string='Portal User', readonly=True, copy=False)

    state = fields.Selection([
        ('legal_confirm', 'Legal Confirm'),
        ('legal_reject', 'Legal Reject'),
    ], string="Status", default='legal_confirm', tracking=True, copy=False)
    legal_decided = fields.Boolean(string='Legal Decision Made', default=False, copy=False)

    # ────────────────────────────────────────────────
    # Methods – each method has its own separate comment block
    # ────────────────────────────────────────────────

    @api.model
    def create(self, vals):
        """
        Automatically generate unique Client ID using sequence
        when creating a new ISP Client record if no name is provided.
        Also handles:
        - Email validation
        - Password matching check
        - Creates/links res.partner and portal user automatically
        """
        # Generate sequence for Client ID
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code('isp.client') or _("New")

        # Basic validations before creation
        email = (vals.get('email') or '').strip().lower()
        if not email:
            raise ValidationError(_("Email is required."))

        pw = vals.get('password') or ''
        pwc = vals.get('password_confirmation') or ''
        if pw or pwc:
            if pw != pwc:
                raise ValidationError(_("Password and Password Confirmation do not match."))

        # Create the client record first
        client = super(IspClient, self).create(vals)

        # ─── Partner creation / linking ───
        partner = self.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not partner:
            partner_vals = {
                'name': client.organization_name or client.client_name or client.name,
                'email': email,
                'phone': client.mobile,
                'street': client.technical_address,
                'company_type': 'company' if client.organization_name else 'person',
                'customer_rank': 1,
                # Division, District, Upazila যোগ করুন
                'division': client.division,
                'district_id': client.district_id.id if client.district_id else False,
                'upazila_id': client.upazila_id.id if client.upazila_id else False,
            }
            partner = self.env['res.partner'].sudo().create(partner_vals)
        else:
            # যদি প্যার্টনার ইতিমধ্যে থাকে, তাহলে তথ্য আপডেট করুন
            partner.sudo().write({
                'name': client.organization_name or client.client_name or client.name,
                'phone': client.mobile,
                'street': client.technical_address,
                # Division, District, Upazila আপডেট করুন
                'division': client.division,
                'district_id': client.district_id.id if client.district_id else False,
                'upazila_id': client.upazila_id.id if client.upazila_id else False,
            })

        client.partner_id = partner.id

        # ─── Portal user creation / linking ───
        user = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if not user:
            portal_group = self.env.ref('base.group_portal')
            user_vals = {
                'name': client.client_name or partner.name,
                'login': email,
                'email': email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [portal_group.id])],
            }
            # Set password only if provided
            if pw:
                user_vals['password'] = pw

            user = self.env['res.users'].sudo().create(user_vals)
        else:
            # Ensure partner link
            if not user.partner_id:
                user.sudo().write({'partner_id': partner.id})

            # Optional: update password if provided
            if pw:
                user.sudo().write({'password': pw})

            # Ensure portal group is assigned
            portal_group = self.env.ref('base.group_portal')
            if portal_group.id not in user.groups_id.ids:
                user.sudo().write({'groups_id': [(4, portal_group.id)]})

        client.portal_user_id = user.id

        return client

    # ────────────────────────────────────────────────

    @api.onchange('division')
    def _onchange_division(self):
        for record in self:
            # যদি district নির্বাচিত থাকে কিন্তু division mismatch হয় → district reset
            if record.district_id and record.district_id.division != record.division:
                record.district_id = False

            # upazila শুধু তখনই reset হবে যখন সেটা current district-এর না
            if record.upazila_id and record.district_id and record.upazila_id.district_id != record.district_id:
                record.upazila_id = False

            # district নাই থাকলে upazila invalid → reset
            if not record.district_id:
                record.upazila_id = False

    # ────────────────────────────────────────────────

    @api.onchange('district_id')
    def _onchange_district_id(self):
        """
        Reset upazila when district changes
        to ensure only valid upazilas are selected.
        """
        for record in self:
            if record.upazila_id and record.upazila_id.district_id != record.district_id:
                record.upazila_id = False

    # ────────────────────────────────────────────────

    def action_legal_confirm(self):
        """
        Mark the client record as 'Legal Confirm' only when all documentation is provided.
        """
        self.ensure_one()
        self._check_documentation_complete()
        self.state = 'legal_confirm'
        self.legal_decided = True

    # ────────────────────────────────────────────────

    def action_legal_reject(self):
        """
        Mark the client record as 'Legal Reject' (rejected by legal team).
        Usually called when legal review finds issues.
        """
        self.state = 'legal_reject'
        self.legal_decided = True
    def write(self, vals):
        """
        Update res.partner when isp.client fields are updated
        """
        result = super(IspClient, self).write(vals)

        # যদি Division, District, Upazila আপডেট করা হয়
        if any(field in vals for field in ['division', 'district_id', 'upazila_id',
                                           'organization_name', 'client_name',
                                           'mobile', 'technical_address', 'email']):
            for client in self:
                if client.partner_id:
                    partner_vals = {}

                    # যদি Division, District, Upazila পরিবর্তন করা হয়
                    if 'division' in vals:
                        partner_vals['division'] = vals['division']
                    if 'district_id' in vals:
                        partner_vals['district_id'] = vals['district_id']
                    if 'upazila_id' in vals:
                        partner_vals['upazila_id'] = vals['upazila_id']

                    # অন্যান্য ফিল্ড আপডেট
                    if 'organization_name' in vals or 'client_name' in vals:
                        partner_vals['name'] = client.organization_name or client.client_name or client.name
                    if 'mobile' in vals:
                        partner_vals['phone'] = vals['mobile']
                    if 'technical_address' in vals:
                        partner_vals['street'] = vals['technical_address']
                    if 'email' in vals:
                        partner_vals['email'] = vals['email']

                    if partner_vals:
                        client.partner_id.sudo().write(partner_vals)

        return result



    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.client_name} [{rec.name}]"



    def _check_required_docs_for_sent_to_legal(self):
        """
        Validate required documents before sending to Legal.
        Required documents:
          - Financial Agreement
          - Profile Image
          - Cheque Image
        """
        for rec in self:
            missing = []

            if not rec.financial_agreement:
                missing.append(_("Financial Agreement"))
            if not rec.profile_image:
                missing.append(_("Profile Image"))
            if not rec.cheque_image:
                missing.append(_("Cheque Image"))

            if missing:
                raise ValidationError(_(
                    "You cannot send this record to Legal because the following documents are missing:\n- %s"
                ) % ("\n- ".join(missing)))
    
    def _check_documentation_complete(self):
        """Ensure all documentation fields are filled before legal confirm."""
        required_docs = [
            ('profile_image', _("Profile Image")),
            ('brtc_license', _("BRTC License")),
            ('contact_authorization', _("Contact Authorization")),
            ('general_agreement', _("General Agreement")),
            ('cheque_image', _("Cheque Image")),
            ('nid_card', _("NID Card")),
            ('trade_license', _("Trade License")),
            ('financial_agreement', _("Financial Agreement")),
        ]
        for rec in self:
            missing = [label for field, label in required_docs if not getattr(rec, field)]
            if missing:
                raise ValidationError(_("You cannot confirm this record because the following documents are missing:\n- %s") % ("\n- ".join(missing)))
