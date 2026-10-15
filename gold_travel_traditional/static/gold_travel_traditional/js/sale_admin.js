(function () {
    function toggleBuyerFields() {
        var typeSelect = document.getElementById('id_buyer_type');
        var exporter = document.getElementById('id_buyer_exporter');
        var saig = document.getElementById('id_buyer_saig');
        if (!typeSelect || !exporter || !saig) return;

        function show(field, visible) {
            var row = field.closest('.form-row');
            if (row) row.style.display = visible ? '' : 'none';
        }

        var isSaig = typeSelect.value === 'saig';
        show(exporter, !isSaig);
        show(saig, isSaig);
    }

    function init() {
        toggleBuyerFields();
        var typeSelect = document.getElementById('id_buyer_type');
        if (typeSelect) {
            typeSelect.addEventListener('change', toggleBuyerFields);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
