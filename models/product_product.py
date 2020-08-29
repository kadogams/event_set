# -*- coding: utf-8 -*-

import sys

from odoo import api, fields, models
from odoo.addons.website.models import ir_http


class ProductProduct(models.Model):
    _inherit = "product.product"

    event_ids = fields.Many2many('event.event', string='Events',
                                 help='Buying the product will automatically register the user to the events.')
    event_seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')],
                                                string='Maximum Attendees', store=True, readonly=True,
                                                compute='_compute_event_seats')
    event_seats_available = fields.Integer('Available Seats', store=True, readonly=True,
                                           compute='_compute_event_seats')
    event_is_expired = fields.Boolean('Event Expired', readonly=True, compute='_compute_event_is_expired',
                                      help='Check if one or more events are expired')
    cart_qty = fields.Integer(compute='_compute_cart_qty')

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        """Redirection, inheritance mechanism hides the method on the model.

        """
        if self.event_set_ok:
            self.type = 'service'

    @api.depends('event_ids', 'event_ids.date_tz', 'event_ids.date_begin')
    def _compute_event_is_expired(self):
        for record in self:
            record.event_is_expired = False
            for event in record.event_ids:
                event = event.with_context(tz=event.date_tz)
                begin_tz = fields.Datetime.context_timestamp(event, event.date_begin)
                current_tz = fields.Datetime.context_timestamp(event, fields.Datetime.now())
                if begin_tz < current_tz:
                    record.event_is_expired = True
                    break

    # maybe use seats_expected?
    @api.depends('event_ids', 'event_ids.seats_availability', 'event_ids.seats_available')
    def _compute_event_seats(self):
        for record in self:
            limited = False
            qty = sys.maxsize
            for event in record.event_ids:
                if event.seats_availability == 'limited' and event.seats_available < qty:
                    limited = True
                    qty = event.seats_available
            record.event_seats_availability = limited and 'limited' or 'unlimited'
            record.event_seats_available = limited and qty or 0

    def _compute_cart_qty(self):
        """Get cart quantity in order to set custom availability messages.

        """
        website = ir_http.get_request_website()
        if not website:
            self.cart_qty = 0
            return
        cart = website.sale_get_order()
        for product in self:
            product.cart_qty = sum(cart.order_line.filtered(lambda p: p.product_id.id == product.id).mapped('product_uom_qty')) if cart else 0
