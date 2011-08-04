

function create_service(containerid){
 $.ajax({
   type: "POST",
   data: "name=Service&container="+containerid,
   url: '/services/',
   success: function(msg){
            loadServices(containerid)
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
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

                $( "#serviceTemplate" ).tmpl( services.slice(start,end) ) .appendTo( "#servicepaginator" );

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#servicepaginator").pagination(services.length, {
                    items_per_page:8,
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
                end   = (new_page_index+1)*this.items_per_page
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

                        $(workflow.tasks).each(function(tindex,task){

                            $("#allowremotecheck-"+task.id).buttonset()

                            //if( tasks["descriptions"][task.task_name] && tasks["descriptions"][task.task_name].examples ){
                                //$( "#id_args-"+task.id ).autocomplete({
                                //        source: tasks["descriptions"][task.task_name].examples
                                //})
                            //}
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

                update_profile_buttons()

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

function update_profile_buttons(){
    $(".savebutton").button().click( function(){showMessage("Alert","To be done")} );
    $(".delbutton").button().click( function(){showMessage("Alert","To be done ")} );
    //$(".allowremotecheck").button()
}

function service_newprofile_ajax(serviceid,profileid,workflowid,data){
     $.ajax({
       type: "POST",
       data: data,
       url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/',
       success: function(task){
            $("#taskTemplate" ).tmpl( task ) .appendTo( "#workflowtable-"+workflowid );
            update_profile_buttons()
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
                            mr.append( $("<input type='radio' id='radio-"+property.id+"-"+i+"' name='radio"+property.id+"' checked='checked'   /><label for='radio-"+property.id+"-"+i+"'>"+choice+"</label>"))
                        }else{
                            mr.append( $("<input type='radio' id='radio-"+property.id+"-"+i+"' name='radio"+property.id+"'  /><label for='radio-"+property.id+"-"+i+"'>"+choice+"</label>"))
                        }
                     })

                     mr.buttonset()
                     
                     $("#service-setmanagementproperty-button-"+property.id ).button().click(
                        function() {
                            var value = $("input:radio[name=radio"+property.id+"]:checked")
                            var id = value.attr("id")
                            var label = $("label[for='"+id+"']")
                            service_setmanagementproperty_ajax(serviceid,property.property, label.text() )
                        }
                     )
                }

           });

       }
     });
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

