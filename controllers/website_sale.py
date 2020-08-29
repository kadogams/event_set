# -*- coding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError


class WebsiteSaleEventSet(WebsiteSale):
    @http.route()
    def cart_update(self, **kwargs):
        """Cart update override to express checkout if the product is an Event Set and reproduce the behaviour when
        buying an event ticket.

        """
        product_tmpl_id = kwargs.get('product_template_id')
        if product_tmpl_id and request.env['product.template'].browse(int(product_tmpl_id)).event_set_ok:
            kwargs.update(express=True)
        return super(WebsiteSaleEventSet, self).cart_update(**kwargs)

    @http.route()
    def payment_transaction(self, **kwargs):
        """Payment transaction override to check event availability and cart quantities before placing the order.

        """
        # print('WebsiteSaleEventSet')
        order = request.website.sale_get_order()
        values = []
        for line in order.order_line:
            if line.event_set_ok:
                if line.product_id.event_is_expired:
                    values.append(_('The registration qqis not longer available'))
                elif line.product_id.event_seats_availability == 'limited':
                    cart_qty = int(sum(
                        order.order_line.filtered(
                            lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty')
                        )
                    )
                    avl_qty = line.product_id.event_seats_available
                    if cart_qty > avl_qty:
                        values.append(_('You ask for %s seats but only %s is available') % (cart_qty, avl_qty if avl_qty > 0 else 0))
        if values:
            raise ValidationError('. '.join(values) + '.')
        return super(WebsiteSaleEventSet, self).payment_transaction(**kwargs)
