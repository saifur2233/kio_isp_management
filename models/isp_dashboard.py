from odoo import api, fields, models


class IspDashboard(models.Model):
    _name = "isp.dashboard"
    _description = "ISP Dashboard"

    name = fields.Char()

    new_client = fields.Integer(
        string="Active Clients",
        compute="_compute_metrics",
        readonly=True
    )
    left_client = fields.Integer(
        string="Left Clients",
        compute="_compute_metrics",
        readonly=True
    )

    total_collected_bill = fields.Monetary(
        string="Total Collected Bill",
        compute="_compute_metrics",
        readonly=True,
        currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True
    )

    def _compute_metrics(self):
        IspClient = self.env['isp.client']
        Move = self.env['account.move']

        # 🔹 Collected / Paid invoices only
        grouped = Move.read_group(
            [
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
            ],
            ['amount_total:sum'],
            []
        )

        total_collected = grouped[0]['amount_total_sum'] if grouped else 0.0

        for rec in self:
            rec.new_client = IspClient.search_count([('active', '=', True)])
            rec.left_client = IspClient.search_count([('active', '=', False)])
            rec.total_collected_bill = total_collected
