# -*- coding: utf-8 -*-
# from odoo import http


# class EstateRental(http.Controller):
#     @http.route('/estate_rental/estate_rental', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/estate_rental/estate_rental/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('estate_rental.listing', {
#             'root': '/estate_rental/estate_rental',
#             'objects': http.request.env['estate_rental.estate_rental'].search([]),
#         })

#     @http.route('/estate_rental/estate_rental/objects/<model("estate_rental.estate_rental"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('estate_rental.object', {
#             'object': obj
#         })

