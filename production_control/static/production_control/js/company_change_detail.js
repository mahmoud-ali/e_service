
django.jQuery(function($){
    function on_company_change(e){
        // console.log("e",e)
        company = $(e);
        if (company && company.val()){
            licence = $(e).parent().parent().find(".field-license select");
            initial_license[company.val()] = licence.val();
        
            // console.log('company',company)
        
            licence_val = initial_license[company.val()] || 0;
            // console.log('Selecting: ' ,initial_license);
            
            $.get("/app/lkp_license/"+company.val()+"/"+licence_val+"/", function( data ) {          
                // console.log(licence)
                // console.log(data)
                licence = licence.html(data);
                // console.log("ddd",data)
            });
        }

    }    
    
    var initial_license = {}
    $(".field-company select").each(function(i,e) {
        on_company_change(e);
    });

    $(".field-company select").on("change", function(e) {
        on_company_change(e.target);
    });
});