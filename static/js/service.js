
function create_subservice(serviceid,containerid){
    form = $("#subservice-form")
    form.find("input[name=serviceid]").val(serviceid)
    form.find("input[name=name]").val("SubService")

    now = new Date()
    form.find("input[name=starttime]").dateplustimepicker({
        dateFormat: 'yy-mm-dd',
        timeFormat: 'hh:mm:ss',
        stepHour: 1,
        stepMinute: 15,
        numberOfMonths: 1,
        step: {minutes: 15},
        show: 'fold',
        showButtonPanel: true,
        defaultTime: now
    });
    form.find("input[name=starttime]").dateplustimepicker("setTime",now);

    oneHour = new Date()
    oneHour.addHours(1)
    form.find("input[name=endtime]").dateplustimepicker({
        dateFormat: 'yy-mm-dd',
        timeFormat: 'hh:mm:ss',
        stepHour: 1,
        stepMinute: 15,
        numberOfMonths: 1,
        step: {minutes: 15},
        show: 'fold',
        showButtonPanel: true,
        defaultTime: oneHour
    });
    form.find("input[name=endtime]").dateplustimepicker("setTime",oneHour);

    create_new_subservice_ui_dialog(serviceid,containerid)
}

function render_service(service, containerid){
    $("#serviceTemplate").tmpl( service, {containerid : containerid} ) .appendTo( "#servicepaginator" );
    $("#newsubservicebutton-"+service.id).button()
}

function load_service_mfiles(serviceid,url){
     $.ajax({
       type: "GET",
       url: url,
       success: function(service){
            $("#mservetree").mserve( "load", {
                serviceid : service.id ,
                mfolder_set : service.mfolder_set,
                mfile_set : service.mfile_set,
                folder_structure : service.folder_structure
            } )
       }
    });
}

function create_mfolder_paginator(mfolders){
        var mfoldercontainer = $("#mfoldercontainer")
        $(mfolders).each( function(index,mfolder){
            $("#mfolderTemplate").tmpl(mfolder).appendTo(mfoldercontainer)
            $("#mfolderholder-"+mfolder.id).click( function(){console.log(mfolder)} )
        } )

}

function update_service_priority(url,priority){
     $.ajax({
       type: "PUT",
       data: "priority="+priority,
       url: url,
       success: function(msg){
       }
     });
}

function check_service_method(method){
    if (! eval("typeof service_" + method + " == 'function'")) {
        $('#button-'+method+'-button').button({disabled: true});
    }
}

function render_managementproperty(serviceid, url, property){

    if(property.values.type == "step"){
        $( "#managementpropertyTemplate-steps" ).tmpl( property ).appendTo( "#managementpropertyholder" ) ;
        $("#service-setmanagementproperty-button-"+property.id ).button().click(
            function() {
                service_setmanagementproperty_ajax(serviceid, url, property.property, $( "#slider-"+property.id ).slider( "value" ) )
            }
        )

        sliderval=0
        if(isNaN(property.value) ){
            sliderval = property.val
        }

        $( "#slider-"+property.id ).slider({
                value:  sliderval,
                range: "min",
                min: property.values.min,
                max: property.values.max,
                step: property.values.step,
                slide: function( event, ui ) {
                        $( "#val-"+property.id ).val( ui.value );
                }
        });
         var malt = $( "#managementalts-"+property.id )

         $.each(property.values.altchoices, function(i,choice){

                var b = $("<button>Set "+choice+"</button>")
                b.button()
                malt.append( b )
                b.click(function(){
                    service_setmanagementproperty_ajax(serviceid, url, property.property, choice )
                })

         })
        $( "#val-"+property.id ).val(  $( "#slider-"+property.id ).slider( "value" ) );

    }else if(property.values.type == "enum"){
        $( "#managementpropertyTemplate-choices" ).tmpl( property ).appendTo( "#managementpropertyholder" ) ;

         var mr = $( "#managementradio-"+property.id )

         $.each(property.values.choices, function(i,choice){
            if(choice == property.value){
                mr.append( $("<input type='radio' id='radio-"+property.id+"-"+i+"' value='"+choice+"' name='radio"+property.id+"' checked='checked'   /><label for='radio-"+property.id+"-"+i+"'>"+choice+"</label>"))
            }else{
                mr.append( $("<input type='radio' id='radio-"+property.id+"-"+i+"' value='"+choice+"' name='radio"+property.id+"'  /><label for='radio-"+property.id+"-"+i+"'>"+choice+"</label>"))
            }
         })

         mr.buttonset().find("input[type=radio]").change(function() {
            service_setmanagementproperty_ajax(serviceid, url, property.property, $(this).val())
        });

    }else if(property.values.type == "string"){
        var mpt = $( "#managementpropertyTemplate-string" ).tmpl( property )
        mpt.appendTo( "#managementpropertyholder" ) ;

        mpt.find("input[type=text]").change(function() {
            service_setmanagementproperty_ajax(serviceid, url, property.property, $(this).val())
        });
    }

}

function service_setmanagementproperty_ajax(service, url, prop, val){
     $.ajax({
       type: "PUT",
       data: "property="+prop+"&value="+val,
       url: url,
       success: function(msg){
         //showMessage("Property Set", "Property '"+prop+"' set to "+val);
         $("."+prop).html(val)
       }
     });
 }

function service_postmanagementproperty_ajax(serviceid, url, data){
     $.ajax({
       type: "POST",
       data: data,
       url: url,
       success: function(property){
           render_managementproperty(serviceid, url, property)
       },
       error: function(msg){
        showError("Error creating new property.",""+msg.responseText)
       }
     });
 }