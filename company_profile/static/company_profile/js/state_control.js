django.jQuery(function($){
    var val = django.jQuery("select#id_state option:selected").val();
    $("select#id_state option").each(function(index){
    if (val == 'submitted'){
        if($(this).attr("value")!=val && $(this).attr("value")!='accepted'){
            $(this).remove();
        }
    }else if (val == 'accepted'){
        if($(this).attr("value")!=val && $(this).attr("value")!='approved' && $(this).attr("value")!='rejected'){
            $(this).remove();
        }
    }else if (val == 'approved'){
        if($(this).attr("value")!=val){
            $(this).remove();
        }
    }else if (val == 'rejected'){
        if($(this).attr("value")!=val){
            $(this).remove();
        }
    }
    });
});
