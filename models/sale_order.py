# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    event_set_ok = fields.Boolean(related='product_id.event_set_ok', readonly=True)

    def _update_registrations(self, confirm=True, cancel_to_draft=False, registration_data=None):
        """Create and confirm registrations linked to an Event Set. Seats will have to be manually confirmed there are
        no more available.
        """
        if confirm:
            Registration = self.env['event.registration'].sudo()
            for so_line in self.filtered('event_set_ok'):
                att_data = {'sale_order_line_id': so_line}
                att_data = Registration._prepare_attendee_values(att_data)
                for event in so_line.product_id.event_ids:
                    seats_available = event.seats_available
                    att_data.update({'event_id': event.id})
                    for count in range(int(so_line.product_uom_qty)):
                        registration = Registration.create(att_data.copy())
                        # Avoid raising a ValidationError, seats will have to be manually confirmed if no more available
                        if seats_available:
                            registration.sudo().confirm_registration()
                        seats_available -= 1
        return super(SaleOrderLine, self)._update_registrations(confirm, cancel_to_draft, registration_data)
