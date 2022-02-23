# -*- coding: utf-8 -*-
# from odoo import http


# class Timekeeping(http.Controller):
#     @http.route('/timekeeping/timekeeping/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/timekeeping/timekeeping/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('timekeeping.listing', {
#             'root': '/timekeeping/timekeeping',
#             'objects': http.request.env['timekeeping.timekeeping'].search([]),
#         })

#     @http.route('/timekeeping/timekeeping/objects/<model("timekeeping.timekeeping"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('timekeeping.object', {
#             'object': obj
#         })
