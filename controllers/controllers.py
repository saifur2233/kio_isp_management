# -*- coding: utf-8 -*-
# from odoo import http


# class KioIspManagement(http.Controller):
#     @http.route('/kio_isp_management/kio_isp_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kio_isp_management/kio_isp_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kio_isp_management.listing', {
#             'root': '/kio_isp_management/kio_isp_management',
#             'objects': http.request.env['kio_isp_management.kio_isp_management'].search([]),
#         })

#     @http.route('/kio_isp_management/kio_isp_management/objects/<model("kio_isp_management.kio_isp_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kio_isp_management.object', {
#             'object': obj
#         })

