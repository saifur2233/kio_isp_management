# models/isp_survey_stage.py
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ISPSurveyStage(models.Model):
    _name = 'isp.survey.stage'
    _description = 'ISP Survey Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_last_stage = fields.Boolean(default=False)

    # Optional but very useful fields
    fold = fields.Boolean(
        string='Folded in Kanban',
        help="This stage is folded in the kanban view when there are no records in it."
    )

    @api.constrains('is_last_stage')
    def _check_only_one_last_stage(self):
        for rec in self:
            if rec.is_last_stage:
                count = self.search_count([
                    ('is_last_stage', '=', True),
                    ('id', '!=', rec.id)
                ])
                if count:
                    raise ValidationError(
                        "Only ONE stage can be marked as the Last Stage."
                    )
