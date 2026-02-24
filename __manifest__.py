# -*- coding: utf-8 -*-
{
    'name': "Kio ISP Management",

    'summary': "Manage ISP sales, customers, and service subscriptions efficiently",

    'description': """
Kio ISP Management System
=========================

A comprehensive solution for Internet Service Provider operations management.

Key Features:
------------
* **Sales Management**: Track and manage ISP service sales with customer assignments
* **Customer Relations**: Integrate seamlessly with Odoo contacts for customer management
* **Salesperson Tracking**: Automatically assign and track sales personnel for each transaction
* **Service Organization**: Streamline your ISP business operations in one centralized system

This module is designed specifically for ISPs to manage their daily sales operations,
customer subscriptions, and sales team performance tracking.
""",

    'author': "Kendroo Ltd",
    'website': "https://kendroo.io/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale', 'account', 'mail'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'data/isp_marketing_sequence.xml',
        'data/isp_client_sequence.xml',
        'data/isp_survey_sequence.xml',
        'data/isp_work_order_sequence.xml',
        'reports/isp_work_order_report.xml',

        'views/menu.xml',
        'views/isp_dashboard_views.xml',
        'views/isp_survey_views.xml',
        'views/isp_district_views.xml',
        'views/isp_upazila_views.xml',
        'views/isp_capacity_views.xml',
        'views/isp_port_views.xml',
        'views/isp_nttn_provider_views.xml',
        'views/res_config_settings_views.xml',
        'views/isp_noc_views.xml',
        'views/isp_transmission_nttn_views.xml',
        'views/isp_transmission_own_views.xml',
        'views/isp_support_views.xml',
        'views/isp_license_views.xml',
        'views/isp_client_views.xml',
        'views/support_team_views.xml',
        'views/client_type_views.xml',
        'views/isp_work_order_type_views.xml',
        'views/isp_aggregation_point_views.xml',
        'views/isp_visit_type_views.xml',
        'views/res_partner_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'kio_isp_management/static/src/js/isp_dashboard_action.js',
            'kio_isp_management/static/src/xml/isp_dashboard_templates.xml',
            'kio_isp_management/static/src/css/isp_views.css',
            'kio_isp_management/static/src/css/isp_survey_table_align.css',
            'kio_isp_management/static/src/js/isp_state_duration_statusbar.js',
        'kio_isp_management/static/src/xml/isp_state_duration_statusbar.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
