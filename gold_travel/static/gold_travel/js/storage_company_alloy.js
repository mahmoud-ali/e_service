django.jQuery(function($){
    var currentCompanyId = null;

    function updateRawWeight($select) {
        var $td = $select.closest('.field-alloy_serial_no');
        var weight = $select.find('option:selected').data('weight');
        var $display = $td.find('.alloy-raw-weight');
        if ($display.length === 0) {
            $display = $('<div class="alloy-raw-weight" style="margin-top:4px;font-weight:bold;"></div>');
            $select.after($display);
        }
        if (weight !== undefined && weight !== null && weight !== '') {
            $display.text('الوزن الخام: ' + weight + ' جرام');
        } else {
            $display.text('');
        }
    }

    function populateAlloySelect($select, companyId, selectedId) {
        var url = "/app/gold_travel/lkp_alloy/" + (companyId || 0) + "/" + (selectedId || 0) + "/";
        $.get(url, function(data){
            $select.html(data);
            updateRawWeight($select);
        });
    }

    function refreshAlloySelects() {
        var companyId = $("#id_company").val();
        currentCompanyId = companyId;
        $(".field-alloy_serial_no select").each(function(){
            populateAlloySelect($(this), companyId, $(this).val());
        });
    }

    $("#id_company").on("change", refreshAlloySelects);

    $(document).on("change", ".field-alloy_serial_no select", function(){
        updateRawWeight($(this));
    });

    $(document).on("formset:added", function(event){
        populateAlloySelect($(event.target).find(".field-alloy_serial_no select"), currentCompanyId, 0);
    });

    $(".field-alloy_serial_no select").each(function(){
        updateRawWeight($(this));
    });
});
