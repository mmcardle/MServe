
function create_new_import_ui_dialog(authid,remoteserviceurl,consumerurl) {
    	$(function() {
		// a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
		$( "#dialog:ui-dialog" ).dialog( "destroy" );

		var name = $( "#name" )

                allFields = $( [] ).add( name )
                tips = $( ".validateTips" );

		importdialog = $( "#importdialogTemplate" ).tmpl()
                importdialog.dialog({
			autoOpen: false,
			height: 250,
			width: 550,
			modal: true,
			buttons: {
				Close: function() {
					$( this ).dialog( "close" );
				}
			},
			close: function() {
				allFields.val( "" ).removeClass( "ui-state-error" );
			}
		});

		$( "#importbutton" )
                    .button()
                    .click(function() {
                         $.ajax({
                           type: "GET",
                           url: remoteserviceurl,
                           success: function(msg){
                               $( "#import-dialog-items" ).empty()

                               if(msg.length==0){
                                    $( "#import-dialog-items" ).append("<div class='ui-widget-content ui-corner-all ui-state-error'>No known Remote Services</div>")
                               }

                               $.each(msg, function(i,remoteservice){
                                    service = $("<div><button id='remoteservicebutton-"+remoteservice.id+"' >Load "+remoteservice.url+"</button></div>")
                                    service.appendTo($( "#import-dialog-items" ))
                                    $("#remoteservicebutton-"+remoteservice.id).button().click(
                                        function() {
                                                importdialog.dialog( "close" );
                                                load_service_iframe(authid,remoteservice.url,consumerurl)
                                            }
                                    );
                               });

                                
                               importdialog.dialog( "open" );

                           }
                         });

                    });
	});
}

function load_service_iframe(authid,url,consumerurl) {

    var dataArr = {
        "url" : ""+url+"",
        "authid" : ""+authid+""
    }

    var data = $.param(dataArr)

     $.ajax({
       type: "POST",
       data: data,
       url: consumerurl,
       success: function(msg){
           m = $("<div style='padding:2px;align:left'><button id='aiClose'>Close</button></div><iframe src="+msg.authurl+" width='100%' height='100%'><p>Your browser does not support iframes.</p></iframe>" );
            $.blockUI({message: m, css: {
                top:  '50px',
                left:  '50px',
                width: ($(window).width() - 100) + 'px',
                height: ($(window).height() - 100) + 'px',
            }});
            $("#aiClose").button().click(function() {
                $.unblockUI();
            });
       },
       error: function(msg){
           showError("Error Loading Remote Service", "Sorry the service could not be loaded - "+ msg.responseText)
       }
     });
}

function create_new_choose_mfile_ui_dialog() {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    $( "#dialog-choose-mfile-dialog-form" ).dialog({
            autoOpen: false,
            height: 600,
            width: 800,
            modal: true,
            buttons: {
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            },
            close: function() {

            }
    });
    $( "#dialog-choose-mfile-dialog-form").dialog( "open" );
}