function create_new_render_ui_dialog(mfileid) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var start = $( "#start" ),
    end = $( "#end" ),
    allFields = $( [] ).add( start ).add( end ),
    tips = $( ".validateTips" );

    function updateTips( t ) {
            tips
                    .text( t )
                    .addClass( "ui-state-highlight" );
            setTimeout(function() {
                    tips.removeClass( "ui-state-highlight", 1500 );
            }, 500 );
    }

    function is_int(o){
      value = o.val()
      if((parseFloat(value) == parseInt(value)) && !isNaN(value)){
          return true;
      } else {
          o.addClass( "ui-state-error" );
          updateTips( "That is not a valid frame '" + o.val() + "'.");
          return false;
      }
    }

    function is_start_lt_end(so,eo){
      if(so.val() <= eo.val()){
          return true;
      } else {
          so.addClass( "ui-state-error" );
          eo.addClass( "ui-state-error" );
          updateTips( "Start frame " + so.val() + " must be less or equal to end frame " +eo.val() +"." );
          return false;
      }
    }


    $( "#dialog-form" ).dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                    "Create Render": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );


                            bValid = bValid && is_int( start);
                            bValid = bValid && is_int( end );
                            bValid = bValid && is_start_lt_end(start,end)

                            if ( bValid ) {
                                    mfile_render(mfileid,start.val(),end.val());
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

    $( "#create-render" )
        .button()
        .click(function() {
                $( "#dialog-form" ).dialog( "open" );
    });
}

function create_new_add_auth_ui_dialog(authid) {
		// a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
		$( "#dialog:ui-dialog" ).dialog( "destroy" );

		var authmethods = $( "#authmethods" ),
                        email = $( "#email" ),
			allFields = $( [] ).add( authmethods ).add( email ),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips
				.text( t )
				.addClass( "ui-state-highlight" );
			setTimeout(function() {
				tips.removeClass( "ui-state-highlight", 1500 );
			}, 500 );
		}


		$( "#dialog-add-methods-dialog-form" ).dialog({
			autoOpen: false,
			height: 300,
			width: 350,
			modal: true,
			buttons: {
				"Create an account": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );
					if ( bValid ) {
                                                var amethods = authmethods.val()
                                                $.ajax({
                                                   type: "POST",
                                                   url: '/auth/'+authid+"/",
                                                   data: "methods="+authmethods.val(),
                                                   success: function(msg){
                                                       var authhtml = $( "#authTemplate" ).tmpl( msg );
                                                       authhtml.prependTo( "#authcontent" )
                                                       authhtml.show('slide')
                                                   },
                                                   error: function(msg){
                                                     showError("Error", "Failure to add methods '" + authmethods.val()+ "'\nStatus: '" + msg.status+ "'\nResponse Text:\n" + msg.responseText);
                                                   }
                                                 });
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

		$( "#createauthbutton" )
                .button()
                .click(function() {
                        $( "#dialog-add-methods-dialog-form" ).dialog( "open" );
                });
	}

function create_new_task_ui_dialog(mfileid, tasktypes) {
  $.ajax({
   type: "GET",
   url: "/tasks/",
   success: function(msg){
       create_new_task_ui_dialog_internal(mfileid,msg['regular'])
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
}

function create_new_task_ui_dialog_internal(mfileid, tasktypes) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var task = $( "#tasktypes" )
    var args = $( "#args" )
    allFields = $( [] ).add( task ).add(args)
    tips = $( ".validateTips" );
    for( t in tasktypes){
        $("#tasktypes").append("<option value='"+tasktypes[t]+"'>"+tasktypes[t]+"</option>")
    }

    $("#tasktypes").change(function() {
        selected = task.val()
        $("#args").empty()

        targs = ["width","height"]
        for(t in targs){
            $("#args").append("<label for="+targs[t]+">"+targs[t]+"</label><input type='text' name="+targs[t]+" id="+targs[t]+"  value=''></input>")
        }
    });

    function updateTips( t ) {
        tips.text( t ).addClass( "ui-state-highlight" );
        setTimeout(function() {
                tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
    }

    $( "#dialog-new-task-dialog-form" ).dialog({
            autoOpen: false,
            height: 400,
            width: 450,
            modal: true,
            buttons: {
                    "Create Task": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );
                            if ( bValid ) {
                                    mfile_task_ajax(mfileid,task.val())
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

    $( "#newtaskbutton" )
        .button().click(function() {
                $( "#dialog-new-task-dialog-form").dialog( "open" );
    });
}

function create_new_add_method_ui_dialog(roleid) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var methods = $( "#methods" ),
    allFields = $( [] ).add( methods ),
    tips = $( ".validateTips" );

    function updateTips( t ) {
            tips
                    .text( t )
                    .addClass( "ui-state-highlight" );
            setTimeout(function() {
                    tips.removeClass( "ui-state-highlight", 1500 );
            }, 500 );
    }

    $( "#dialog-add-role-dialog-form" ).dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                    "Create Render": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );

                            if ( bValid ) {
                                        $.ajax({
                                           type: "PUT",
                                           url: '/roles/'+roleid+"/",
                                           data: "methods="+methods.value,
                                           success: function(msg){
                                               poplulate_methods(roleid,msg["methods"])
                                           },
                                           error: function(msg){
                                             showError("Error", "Failure to add methods '" + methods.value + "'\nStatus: '" + msg.status+ "'\nResponse Text:\n" + msg.responseText);
                                           }
                                         });
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

    $( ".addmethods" )
        .button()
        .click(function() {
                $( "#dialog-add-role-dialog-form").dialog( "open" );
    });
}

function poplulate_methods(roleid, methods){
   $('.methods'+roleid).empty()
   $.each(methods, function(i,item){
        id = $("&nbsp;&nbsp;<span>"+item+"&nbsp;</span>&nbsp;")
        $(id).appendTo('.methods'+roleid);
   });
}