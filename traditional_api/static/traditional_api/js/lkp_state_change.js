django.jQuery(function($){
    var initial_soag = $("select#id_soag").val() || 0
    $("select#id_state").on("change", function() {
        var state = $("select#id_state").val() || 0
        var soag = $("select#id_soag").val() || initial_soag

        $.get("/app/api-traditional/lkp_soag/"+state+"/"+soag+"/", function( data ) {          
            $("select#id_soag").html(data);

        });
    });
});
