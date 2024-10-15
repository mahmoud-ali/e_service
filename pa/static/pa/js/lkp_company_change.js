django.jQuery(function($){
    var initial_license = $("select#id_license").val() || 0
    $("select#id_company").on("change", function() {
        var company = $("select#id_company").val() || 0
        var license = $("select#id_license").val() || initial_license

        $.get("/app/pa/lkp_license/"+company+"/"+license+"/", function( data ) {          
            $("select#id_license").html(data);

        });
    });
});
