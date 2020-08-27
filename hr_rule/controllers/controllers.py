# -*- coding: utf-8 -*-
from odoo import http

# class Module1(http.Controller):
#     @http.route('/module1/module1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module1/module1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module1.listing', {
#             'root': '/module1/module1',
#             'objects': http.request.env['module1.module1'].search([]),
#         })

#     @http.route('/module1/module1/objects/<model("module1.module1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module1.object', {
#             'object': obj
#         })