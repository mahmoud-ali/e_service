django.jQuery(function($){
    var initial_license = {}

    $("#id_company").on("change", function(e) {
        company = $(this);
        licence = $("#id_license");
        initial_license[company.val()] = licence.val();

        licence_val = initial_license[company.val()] || 0;
        // console.log('Selecting: ' ,initial_license);
        
        $.get("/app/lkp_license/"+company.val()+"/"+licence_val+"/", function( data ) {          
            // console.log(licence)
            // console.log(data)
            licence = licence.html(data);
            // console.log("ddd",data)
        });
    });
});