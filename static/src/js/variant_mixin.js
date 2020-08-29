odoo.define('academy.VariantMixin', function (require) {
'use strict';

var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/academy/static/src/xml/event_set_product_availability.xml',
    QWeb
);

/**
 * Addition to the variant_mixin._onChangeCombination
 *
 * This will prevent the user from selecting a quantity that is not available for that product if it is an event set.
 *
 * It will also display various info/warning messages regarding the select product's availability.
 *
 * This behavior is only applied for the web shop (and not on the SO form)
 * and only for the main product.
 *
 * @param {MouseEvent} ev
 * @param {$.Element} $parent
 * @param {Array} combination
 */
VariantMixin._onChangeCombinationEventSet = function (ev, $parent, combination) {
    var product_id = 0;
    // needed for list view of variants
    if ($parent.find('input.product_id:checked').length) {
        product_id = $parent.find('input.product_id:checked').val();
    } else {
        product_id = $parent.find('.product_id').val();
    }
    var isMainProduct = combination.product_id &&
        ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
        combination.product_id === parseInt(product_id);

    if (!this.isWebsite || !isMainProduct){
        return;
    }

    var qty = $parent.find('input[name="add_qty"]').val();

    $parent.find('#add_to_cart').removeClass('out_of_stock');
    $parent.find('#buy_now').removeClass('out_of_stock');
    if (combination.event_set_ok) {
        if (combination.event_is_expired) {
            $parent.find('#add_to_cart').addClass('disabled out_of_stock');
            $parent.find('#buy_now').addClass('disabled out_of_stock');
        }
        else if (combination.event_seats_availability === "limited") {
            combination.event_seats_available -= parseInt(combination.cart_qty);
            if (combination.event_seats_available < 0) {
                combination.event_seats_available = 0;
            }
            // Handle case when manually write in input
            if (qty > combination.event_seats_available) {
                var $input_add_qty = $parent.find('input[name="add_qty"]');
                qty = combination.event_seats_available || 1;
                $input_add_qty.val(qty);
            }
            if (qty > combination.event_seats_available
                || combination.event_seats_available < 1 || qty < 1) {
                $parent.find('#add_to_cart').addClass('disabled out_of_stock');
                $parent.find('#buy_now').addClass('disabled out_of_stock');
            }
        }
    }

    xml_load.then(function () {
        $('.oe_website_sale')
            .find('.event_availability_message_' + combination.product_template)
            .remove();

        var $message = $(QWeb.render(
            'academy.product_availability',
            combination
        ));
        $('div.event_availability_messages').html($message);
        // $('strong.attribute_name').html("ayayaya");
    });
};

publicWidget.registry.WebsiteSale.include({
    /**
     * Adds the event availability checking to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        VariantMixin._onChangeCombinationEventSet.apply(this, arguments);
    }
});

return VariantMixin;

});
