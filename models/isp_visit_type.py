# -*- coding: utf-8 -*-

from odoo import models, fields, _


class IspVisitType(models.Model):
    _name = 'isp.visit.type'
    _description = 'Visit Type'
    _order = 'name'

    name = fields.Char(string="Visit Type", required=True, help="Label shown in the marketing visit pickers.")
    active = fields.Boolean(default=True, help="Inactive visit types stay on historical records but disappear from selection.")

    _sql_constraints = [
        (
            'unique_visit_type_name',
            'unique(name)',
            _('Visit Type must be unique.')
        )
    ]
