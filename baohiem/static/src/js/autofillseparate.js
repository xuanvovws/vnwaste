odoo.define('autofill.separate', function (require) {
    "use strict";
    // import packages
    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    
    // widget implementation
    var AutofillWidget = basic_fields.FieldMonetary.extend({
    _prepareInput: function ($input) {
         this._super.apply(this, arguments);
         this.$input.mask("#,##0", {reverse: true});
         return this.$input;
     },
    });
    
    registry.add('autofill_separate', AutofillWidget); // add our "auto fill separate" widget to the widget registry
});