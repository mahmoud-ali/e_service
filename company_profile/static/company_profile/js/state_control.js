django.jQuery(document).ready(function(){
    var val = django.jQuery("select#id_state option:selected").val();
    django.jQuery("select#id_state option").each(function(index){
        
    if (val == 'submitted'){
        if(django.jQuery(this).attr("value")!=val && django.jQuery(this).attr("value")!='accepted'){
            django.jQuery(this).hide();
        }
    }else if (val == 'accepted'){
        if(django.jQuery(this).attr("value")!=val && django.jQuery(this).attr("value")!='approved' && django.jQuery(this).attr("value")!='rejected'){
            django.jQuery(this).hide();
        }
    }else if (val == 'approved'){
        if(django.jQuery(this).attr("value")!=val){
            django.jQuery(this).hide();
        }
    }else if (val == 'rejected'){
        if(django.jQuery(this).attr("value")!=val){
            django.jQuery(this).hide();
        }
    }
    });
});
