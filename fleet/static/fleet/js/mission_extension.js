(function($) {
    $(function() {
        var isExtended = $('#id_is_extended');
        var extensionFields = $('.field-extension_days, .field-extended_planned_end_date, .field-extended_actual_end_date');

        function toggleExtensionFields() {
            if (isExtended.is(':checked')) {
                extensionFields.show();
            } else {
                extensionFields.hide();
            }
        }

        // Initial toggle
        toggleExtensionFields();

        // Toggle on change
        isExtended.change(function() {
            toggleExtensionFields();
        });
    });
})(django.jQuery);
