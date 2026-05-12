(function($) {
    function setupSelect2Filter() {
        // Target both vehicle and driver selects in the mission inline
        $('select[id^="id_missionvehicle_set-"]').each(function() {
            var $el = $(this);
            if ($el.data('filter-applied')) return;

            var select2 = $el.data('select2');
            if (select2 && select2.options && select2.options.options.ajax) {
                var ajax = select2.options.options.ajax;
                var originalData = ajax.data;

                ajax.data = function(params) {
                    var data = originalData ? originalData(params) : params;
                    
                    // If it's a vehicle field, add mission_only=1
                    if ($el.attr('id').endsWith('-vehicle')) {
                        data.mission_only = 1;
                    }
                    
                    // If it's a driver field, add vehicle_id from the same row
                    if ($el.attr('id').endsWith('-driver')) {
                        var $row = $el.closest('tr, .form-row');
                        var vehicleId = $row.find('select[id$="-vehicle"]').val();
                        if (vehicleId) {
                            data.vehicle_id = vehicleId;
                        }
                    }
                    
                    return data;
                };
                $el.data('filter-applied', true);
            }
        });
    }

    // Run on load
    $(document).ready(function() {
        // Wait a bit for Select2 to initialize
        setTimeout(setupSelect2Filter, 500);
        
        // Also run when a new row is added
        $(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'missionvehicle_set') {
                setTimeout(setupSelect2Filter, 100);
            }
        });

        // Run when any select is opened just in case
        $(document).on('select2:opening', 'select[id^="id_missionvehicle_set-"]', setupSelect2Filter);
    });
})(django.jQuery);
