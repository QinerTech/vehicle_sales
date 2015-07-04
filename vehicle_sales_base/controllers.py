# -*- coding: utf-8 -*-
from openerp import http

# class Module(http.Controller):
#     @http.route('/module/module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module/module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module.listing', {
#             'root': '/module/module',
#             'objects': http.request.env['module.module'].search([]),
#         })

#     @http.route('/module/module/objects/<model("module.module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module.object', {
#             'object': obj
#         })