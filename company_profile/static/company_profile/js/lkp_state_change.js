django.jQuery(function($){
    var initial_locality = $("select#id_locality").val() || 0
    $("select#id_state").on("change", function() {
        var state = $("select#id_state").val() || 0
        var locality = $("select#id_locality").val() || initial_locality

        $.get("http://127.0.0.1:8000/lkp_locality/"+state+"/"+locality+"/", function( data ) {          
            $("select#id_locality").html(data);

        });
    });
});
