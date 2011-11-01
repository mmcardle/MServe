

function create_service(containerid){
    form = $("#service-form")
    form.find("input[name=name]").val("Service")

    now = new Date()
    form.find("input[name=starttime]").dateplustimepicker({
        dateFormat: 'yy-mm-dd',
        timeFormat: 'hh:mm:ss',
        stepHour: 1,
        stepMinute: 15,
        numberOfMonths: 1,
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
        show: 'fold',
        showButtonPanel: true,
        defaultTime: oneHour
    });
    form.find("input[name=endtime]").dateplustimepicker("setTime",oneHour);

    create_new_service_ui_dialog(containerid)
}

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
        step: { minutes: 15 },
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
        step: { minutes: 15 },
        show: 'fold',
        showButtonPanel: true,
        defaultTime: oneHour
    });
    form.find("input[name=endtime]").dateplustimepicker("setTime",oneHour);

    create_new_subservice_ui_dialog(serviceid,containerid)
}

function render_service(service,containerid){
    $("#serviceTemplate").tmpl( service, { containerid : containerid } ) .appendTo( "#servicepaginator" );
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
            $("#mfolderholder-"+mfolder.id).click( function(){ console.log(mfolder) } )
        } )

}

function loadServices(containerid){
    $.ajax({
       type: "GET",
       url: "/containers/"+containerid+"/",
       success: function(msg){
            services = msg.dataservice_set;

            if(services.length==0){
                 $("#servicemessages").append("<div id='noservices' class='message' >No Services</div>");
                return;
            }else{

                $("#noservices").remove()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>services.length){
                    end=services.length;
                }

                var serviceslice = services.slice(start,end)
                $(serviceslice).each( function(index,service){ render_service(service,containerid) } )

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#servicepaginator").pagination(services.length, {
                    items_per_page:16,
                    callback:handlePaginationClick
            });
       }
     });
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
        $('#button-'+method+'-button').button({ disabled: true });
    }
}

function service_loadprofiles(serviceid){

    $.ajax({
       type: "GET",
       url: "/tasks/",
       success: function(tasks){
            service_loadprofiles_remote(serviceid, tasks)
        }
    });

}

function service_loadprofiles_remote(serviceid, tasks){
    $.ajax({
       type: "GET",
       url: "/services/"+serviceid+"/profiles/",
       success: function(profiles){

            if(profiles.length==0){
                 $("#profilemessages").append("<div id='noprofiles' class='message' >No profiles</div>");
                return;
            }else{

                $("#noprofiles").remove()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end = (new_page_index+1)*this.items_per_page
                if(end>profiles.length){
                    end=profiles.length;
                }

                profileslice = profiles.slice(start,end)
                $( "#profileTemplate" ).tmpl( profileslice ) .appendTo( "#profilepaginator" );

                $(".allowremotecheck").button()
                $(".workflows").accordion({
                    collapsible: true,
                    autoHeight: false,
                    navigation: true,
                })

                $(profileslice).each(function(pindex,profile){
                    $(profile.workflows).each(function(windex,workflow){
                        console.log("WF-"+workflow)
                        $(workflow.tasksset).each(function(tsindex,taskset){
                            console.log(taskset)
                            $(taskset.tasks).each(function(tindex,task){
                                console.log(task)
                                //if( tasks["descriptions"][task.task_name] && tasks["descriptions"][task.task_name].examples ){
                                    //$( "#id_args-"+task.id ).autocomplete({
                                    //        source: tasks["descriptions"][task.task_name].examples
                                    //})
                                //}
                            });
                        });

                        $("#addbutton-workflow-"+workflow.id).button().click(
                            function(){
                                    data = $("#newtaskform-workflow-"+workflow.id).serialize()
                                    service_newprofile_ajax(serviceid,profile.id,workflow.id,data)
                            }
                        )

                    });
                });

                $(".task_name").autocomplete({
			source: tasks.regular
		});


                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#servicepaginator").pagination(profiles.length, {
                    items_per_page:5,
                    callback:handlePaginationClick
            });
       }
     });
}

function service_newprofile_ajax(serviceid,profileid,workflowid,data){
     $.ajax({
       type: "POST",
       data: data,
       url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/',
       success: function(task){
            $("#taskTemplate" ).tmpl( task ) .appendTo( "#workflowtable-"+workflowid );
       },
       error: function(msg){
            showError("Error Adding Task",msg.responseText)
        }
     });
 }


function service_loadmanagementproperties(serviceid){
     $.ajax({
       type: "GET",
       url: '/services/'+serviceid+'/properties/',
       success: function(properties){
           $.each(properties, function(i,property){
                render_managementproperty(serviceid, property)
           });
       }
     });
}

function render_managementproperty(serviceid, property){

    if(property.values.type == "step"){
        $( "#managementpropertyTemplate-steps" ).tmpl( property ).appendTo( "#managementpropertyholder" ) ;
        $("#service-setmanagementproperty-button-"+property.id ).button().click(
            function() {
                service_setmanagementproperty_ajax(serviceid,property.property, $( "#slider-"+property.id ).slider( "value" ) )
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
                    service_setmanagementproperty_ajax(serviceid,property.property, choice )
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
            service_setmanagementproperty_ajax(serviceid, property.property, $(this).val())
        });

    }else if(property.values.type == "string"){
        var mpt = $( "#managementpropertyTemplate-string" ).tmpl( property )
        mpt.appendTo( "#managementpropertyholder" ) ;

        mpt.find("input[type=text]").change(function() {
            service_setmanagementproperty_ajax(serviceid, property.property, $(this).val())
        });
    }

}

function service_setmanagementproperty_ajax(service,prop,val){
     $.ajax({
       type: "PUT",
       data: "property="+prop+"&value="+val,
       url: '/api/'+service+'/setmanagementproperty/',
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
           render_managementproperty(serviceid, property)
       }
     });
 }