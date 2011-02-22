

function create_service(containerid){
 $.ajax({
   type: "POST",
   data: "name=Service&cid="+containerid,
   url: '/service/',
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
       url: "/container/"+containerid+"/",
       success: function(msg){
            services = msg.dataservice_set;

            $(".numservices").html(services.length);
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

                for(var i=start;i<end;i++) {
                    
                    //var c = $("<div>"+services[i].name+"  <a href='/browse/"+services[i].id+"/'>"+services[i].id+"</a>&nbsp;<em>"+services[i].mfile_set.length+" files</em></div>")
                    //$('#servicepaginator').append(c)
                }
                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#servicepaginator").pagination(msg.length, {
                    items_per_page:20,
                    callback:handlePaginationClick
            });
       },
       error: function(msg){
            showError( "Failure to get services ",msg );
       }
     });
}

function check_service_method(method){
    if (! eval("typeof service_" + method + " == 'function'")) {
        $('#button-'+method+'-button').button({ disabled: true });
    }
}

function service_setmanagementproperty_ajax(service,prop,val){
     $.ajax({
       type: "PUT",
       data: "property="+prop+"&value="+val,
       url: '/api/'+service+'/setmanagementproperty/',
       success: function(msg){
         showMessage("Property Set", "Property '"+prop+"' set to "+val);
         $("."+prop).html(val)
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
 }

function service_setmanagementproperty(serviceid) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var prop = $( "#prop" ),
    val = $( "#val" ),

    allFields = $( [] ).add( prop ).add( val ),
    tips = $( ".validateTips" );

    function updateTips( t ) {
            tips.text( t ).addClass( "ui-state-highlight" );
            setTimeout(function() {
                    tips.removeClass( "ui-state-highlight", 1500 );
            }, 500 );
    }

    function check(o,name){
      if( o.val() !=null && o.val() != ""){
          return true;
      } else {
          updateTips( "That is not a valid " +name+ " "+ o.val() + ".");
          return false;
      }
    }

    $( "#set-management-property-button-dialog-form" ).dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                    "Set Management Property": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );

                            bValid = bValid && check( prop, "property");
                            bValid = bValid && check( val, "value");

                            if ( bValid ) {
                                    service_setmanagementproperty_ajax(serviceid,prop.val(),val.val());
                                    $( this ).dialog( "close" );
                            }
                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            },
            close: function() {
                    allFields.val( "" ).removeClass( "ui-state-error" );
            }
    });

    $( "#service-setmanagementproperty-button" )
            .click(function() {
                    $( "#set-management-property-button-dialog-form" ).dialog( "open" );
            });
}
