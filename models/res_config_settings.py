from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Backward-compatible toggles used by older settings views.
    enable_ocn = fields.Boolean(
        string="Enable OCN",
        config_parameter="mail_mobile.enable_ocn",
        help="Enable OCN-related options."
    )
    disable_redirect_firebase_dynamic_link = fields.Boolean(
        string="Disable link redirection to mobile app",
        config_parameter="mail_mobile.disable_redirect_firebase_dynamic_link",
        help="Disable automatic redirect links to mobile app."
    )
    map_box_token = fields.Char(
        string="Token Map Box",
        config_parameter="web_map.token_map_box",
        help="MapBox API token for map features."
    )
    setting_account_avatax = fields.Boolean(
        string="Use AvaTax",
        config_parameter="account_avatax.setting_account_avatax",
        help="Enable AvaTax integration settings."
    )
    avalara_environment = fields.Selection(
        [
            ("sandbox", "Sandbox"),
            ("production", "Production"),
        ],
        string="Avalara Environment",
        config_parameter="account_avatax.avalara_environment",
        default="sandbox",
    )
    avalara_api_id = fields.Char(
        string="Avalara API ID",
        config_parameter="account_avatax.avalara_api_id",
    )
    avalara_api_key = fields.Char(
        string="Avalara API Key",
        config_parameter="account_avatax.avalara_api_key",
    )
    avalara_partner_code = fields.Char(
        string="Avalara Company Code",
        config_parameter="account_avatax.avalara_partner_code",
    )
    avalara_use_upc = fields.Boolean(
        string="Use UPC",
        config_parameter="account_avatax.avalara_use_upc",
        default=True,
    )
    avalara_commit = fields.Boolean(
        string="Commit in Avatax",
        config_parameter="account_avatax.avalara_commit",
    )
    avalara_address_validation = fields.Boolean(
        string="Avalara Address Validation",
        config_parameter="account_avatax.avalara_address_validation",
    )
    enable_nttn = fields.Boolean(
        string="Enable NTTN",
        config_parameter="isp.enable_nttn",
        help="Enable NTTN-related options."
    )
    isp_mb_value = fields.Float(
        string="MB Value",
        config_parameter="isp.mb_value",
        help="Enter MB manually."
    )

    # Compatibility fields for databases that still contain inherited views from
    # enterprise currency_rate_live while its python model extension is absent.
    currency_provider = fields.Selection(
        [
            ("ecb", "European Central Bank"),
            ("xe_com", "xe.com"),
            ("cbuae", "Central Bank of the UAE"),
            ("bnb", "Bulgaria National Bank"),
            ("bbr", "Central Bank of Brazil"),
            ("boc", "Bank of Canada"),
            ("fta", "Federal Tax Administration of Switzerland"),
            ("mindicador", "Central Bank of Chile (mindicador.cl)"),
            ("cnb", "Czech National Bank"),
            ("cbegy", "Central Bank of Egypt"),
            ("banguat", "Bank of Guatemala"),
            ("boi", "Bank of Italy"),
            ("banxico", "Bank of Mexico"),
            ("bcrp", "SUNAT / Bank of Peru"),
            ("nbp", "National Bank of Poland"),
            ("bnr", "National Bank of Romania"),
            ("srb", "Sveriges Riksbank"),
            ("tcmb", "Central Bank of the Republic of Turkiye"),
            ("hmrc", "HM Revenue & Customs"),
            ("bnm", "Bank Negara Malaysia"),
            ("bi", "Bank Indonesia"),
            ("bcu", "Uruguayan Central Bank"),
        ],
        string="Service Provider",
        default="ecb",
    )
    currency_interval_unit = fields.Selection(
        [
            ("manually", "Manually"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
        ],
        string="Interval Unit",
        default="manually",
    )
    currency_next_execution_date = fields.Date(string="Next Execution Date")

    # Compatibility fields for databases that still contain settings views
    # from enterprise account_invoice_extract while its model extension
    # is not loaded in this environment.
    extract_in_invoice_digitalization_mode = fields.Selection(
        [
            ("no_send", "Do not digitize"),
            ("manual_send", "Digitize on demand"),
            ("auto_send", "Digitize automatically"),
        ],
        string="Incoming invoice digitization mode",
        config_parameter="account.extract_in_invoice_digitalization_mode",
        default="no_send",
    )
    extract_out_invoice_digitalization_mode = fields.Selection(
        [
            ("no_send", "Do not digitize"),
            ("manual_send", "Digitize on demand"),
            ("auto_send", "Digitize automatically"),
        ],
        string="Outgoing invoice digitization mode",
        config_parameter="account.extract_out_invoice_digitalization_mode",
        default="no_send",
    )
    extract_single_line_per_tax = fields.Boolean(
        string="Single Line Per Tax (Compatibility)",
        config_parameter="account.extract_single_line_per_tax",
    )