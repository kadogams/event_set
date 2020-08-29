# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    """Add fields related to event sets. It will allow to trigger event registrations upon the validation of a sale
    order.

    """
    _inherit = "product.template"

    event_set_ok = fields.Boolean(string='Is an Event Set',
                                  help="If checked this product automatically creates an event registration at the "
                                       "sales order confirmation.")
    event_availability = fields.Selection([
        ('always', 'Show availability on website'),
        ('threshold', 'Show availability below a threshold'),
    ], string='Event Availability', help='Adds an event availability status on the web product page.')
    event_available_threshold = fields.Integer(string='Availability Threshold', default=5)
    event_ids = fields.Many2many('event.event', string='Events', help='Buying the product will automatically register '
                                                                      'the user to the events.',
                                 compute='_compute_event_ids', inverse='_set_event_ids', store=True)
    event_seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')],
                                                string='Maximum Attendees', store=True, readonly=True,
                                                compute='_compute_event_seats')
    event_seats_available = fields.Integer('Available Seats', store=True, readonly=True,
                                           compute='_compute_event_seats')

    @api.constrains('event_set_ok', 'type')
    def _check_event_set_type(self):
        """Check if the type of an Event Set is a Service.

        """
        if self.event_set_ok and self.type != 'service':
            raise ValidationError("The type of an Event Set must be a Service")

    @api.constrains('event_set_ok', 'product_variant_ids')
    def _check_event_set_variants(self):
        """Check if the there is not any existing relationships between the product variants of an Event Set and Event
        records before modifying the field.

        """
        if not self.event_set_ok and self.product_variant_ids and self.product_variant_ids.event_ids:
            raise ValidationError("All existing relationships between the product variants of an Event Set and Event "
                                  "records have to be removed before modifying Event Set field")

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        if self.event_set_ok:
            self.type = 'service'

    @api.depends('product_variant_ids', 'product_variant_ids.event_ids')
    def _compute_event_ids(self):
        """Get the events associated to its unique variant. Allows to edit event sets from the product template form
        view.

        """
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            # replaces all existing records in the set
            template.event_ids = [(6, 0, [event.id for event in template.product_variant_ids.event_ids])]
        for template in (self - unique_variants):
            # removes all records from the set
            template.event_ids = [(5,)]

    @api.depends('product_variant_ids', 'product_variant_ids.event_ids')
    def _set_event_ids(self):
        """Set events to its unique variant. Allows to edit event sets from the product template form view.

        """
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            # replaces all existing records in the set
            template.product_variant_ids.event_ids = [(6, 0, [event.id for event in template.event_ids])]
        for template in (self - unique_variants):
            # removes all records from the set
            template.event_ids = [(5,)]

    @api.depends('product_variant_ids', 'product_variant_ids.event_seats_availability',
                 'product_variant_ids.event_seats_available')
    def _compute_event_seats(self):
        """Get event information from its unique variant.

        """
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.event_seats_availability = template.product_variant_ids.event_seats_availability
            template.event_seats_available = template.product_variant_ids.event_seats_available
        for template in (self - unique_variants):
            template.event_seats_availability = None
            template.event_seats_available = None

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        """Override function in order to add information about event sets.

        """
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template
        )

        if not self.env.context.get('website_sale_event_set_get_quantity'):
            return combination_info

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            combination_info.update({
                'event_seats_availability': product.event_seats_availability,
                'event_seats_available': product.event_seats_available,
                'event_set_ok': product.event_set_ok,
                'event_availability': product.event_availability,
                'event_available_threshold': product.event_available_threshold,
                'event_is_expired': product.event_is_expired,
                'product_template': product.product_tmpl_id.id,
                'cart_qty': product.cart_qty,
                'uom_name': product.uom_id.name,
            })
        else:
            product_template = self.sudo()
            combination_info.update({
                # 'event_seats_availability': 'unlimited',
                # 'event_seats_available': 0,
                'event_set_ok': product_template.event_set_ok,
                'event_availability': product_template.event_availability,
                'event_available_threshold': product_template.event_available_threshold,
                'product_template': product_template.id,
                'cart_qty': 0
            })

        return combination_info
