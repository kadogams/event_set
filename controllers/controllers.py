# -*- coding: utf-8 -*-
# from odoo import http


# class EventSet(http.Controller):
#     @http.route('/event_set/event_set/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/event_set/event_set/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('event_set.listing', {
#             'root': '/event_set/event_set',
#             'objects': http.request.env['event_set.event_set'].search([]),
#         })

#     @http.route('/event_set/event_set/objects/<model("event_set.event_set"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('event_set.object', {
#             'object': obj
#         })
