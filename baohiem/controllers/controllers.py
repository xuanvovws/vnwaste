# -*- coding: utf-8 -*-
# from odoo import http


# class Baohiem(http.Controller):
#     @http.route('/baohiem/baohiem/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/baohiem/baohiem/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('baohiem.listing', {
#             'root': '/baohiem/baohiem',
#             'objects': http.request.env['baohiem.baohiem'].search([]),
#         })

#     @http.route('/baohiem/baohiem/objects/<model("baohiem.baohiem"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('baohiem.object', {
#             'object': obj
#         })
