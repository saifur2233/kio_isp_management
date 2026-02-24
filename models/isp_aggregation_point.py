from odoo import models, fields


class IspAggregationPoint(models.Model):
    _name = 'isp.aggregation.point'
    _description = 'ISP Aggregation Point'
    _rec_name = 'name'

    name = fields.Char(string='Aggregation Name', required=True)
    switch_model_no = fields.Char(string='Switch Model No')
    pop_latitude = fields.Char(string='POP Latitude')
    pop_longitude = fields.Char(string='POP Longitude')
