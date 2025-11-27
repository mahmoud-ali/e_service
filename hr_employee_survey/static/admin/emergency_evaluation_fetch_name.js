(function($) {
    $(document).ready(function() {
       
        var employeeCodeField = $('#id_employee_code');
        var employeeNameField = $('#id_employee_name'); 

        
        function fetchAndSetEmployeeName(code) {
            
            if (code) {
                
                employeeNameField.val('Fetching...'); 
                
                $.ajax({
                    url: "http://localhost:8000/surveys/ajax/get_employee_name/", 
                    data: {'code': code},
                    dataType: 'json',
                    success: function(data) {
                        console.log('AJAX successful');
                        employeeNameField.val(data.employee_name || 'Name not found'); 
                    },
                    error: function(xhr, status, error) {
                        console.error("AJAX Error:", status, error);
                        employeeNameField.val('Error fetching name');
                    }
                });
            } else {
                employeeNameField.val(''); 
            }
        }

        employeeCodeField.on('change', function() {
            var code = $(this).val();
            fetchAndSetEmployeeName(code);
        });

        var initialCode = employeeCodeField.val();
        if (initialCode) {
            fetchAndSetEmployeeName(initialCode);
        }
    });
})(django.jQuery);