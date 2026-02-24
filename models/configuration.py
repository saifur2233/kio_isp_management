from odoo import fields, models, _
from .district_selection import (
    DISTRICT_SELECTION,
    DIVISION_SELECTION,
    DISTRICT_DIVISION_MAP,
    resolve_district_code,
)
from .upazila_selection import UPAZILA_SELECTION


class IspDistrict(models.Model):
    _name = 'isp.district'
    _description = 'ISP District'

    name = fields.Char(required=True)
    code = fields.Char(required=True, copy=False)
    division = fields.Selection(DIVISION_SELECTION, required=True)
    upazila_ids = fields.One2many('isp.upazila', 'district_id')
    upazila_count = fields.Integer(compute='_compute_upazila_count')
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        ('district_code_unique', 'UNIQUE(code)', 'The district code must be unique.')
    ]

    def init(self):
        """Ensure the base list of districts is always available."""
        self = self.sudo()
        code_to_record = {
            district.code: district
            for district in self.search([])
        }
        for code, name in DISTRICT_SELECTION:
            division_code = DISTRICT_DIVISION_MAP.get(code)
            if not division_code:
                continue
            vals = {
                'name': name,
                'division': division_code,
            }
            record = code_to_record.get(code)
            if record:
                record.write(vals)
            else:
                code_to_record[code] = self.create({**vals, 'code': code})

    def _compute_upazila_count(self):
        for rec in self:
            rec.upazila_count = len(rec.upazila_ids)



    def action_view_upazilas(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Upazilas"),
            "res_model": "isp.upazila",
            "view_mode": "tree,form",
            "domain": [("district_id", "=", self.id)],
            "context": {"default_district_id": self.id},
        }




class IspUpazila(models.Model):
    _name = 'isp.upazila'
    _description = 'ISP Upazila'

    name = fields.Char(required=True)
    code = fields.Char(required=True, copy=False)
    district_id = fields.Many2one('isp.district', required=True, ondelete='cascade')

    _sql_constraints = [
        ('upazila_code_unique', 'UNIQUE(code)', 'The upazila code must be unique.')
    ]

    def init(self):
        """Populate upazila records based on the reference list."""
        self = self.sudo()
        district_model = self.env['isp.district']
        code_to_record = {upazila.code: upazila for upazila in self.search([])}
        for code, label in UPAZILA_SELECTION:
            try:
                district_label, upazila_label = [part.strip() for part in label.split('-', 1)]
            except ValueError:
                continue
            district_code = resolve_district_code(district_label)
            if not district_code:
                continue
            district = district_model.search([('code', '=', district_code)], limit=1)
            if not district:
                continue
            vals = {
                'name': upazila_label,
                'district_id': district.id,
            }
            record = code_to_record.get(code)
            if record:
                record.write(vals)
            else:
                code_to_record[code] = self.create({**vals, 'code': code})



class IspCapacityMaster(models.Model):
    _name = 'isp.capacity.master'
    _description = 'ISP Capacity'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This capacity name already exists!'),
    ]


class IspNttnProvider(models.Model):
    _name = 'isp.nttn.provider'
    _description = 'NTTN Provider'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True, invisible=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This provider name already exists!'),
    ]
