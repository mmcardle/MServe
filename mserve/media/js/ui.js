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

function create_new_job_ui_dialog(mfileid, jobtypes) {
  $.ajax({
   type: "GET",
   url: "/tasks/",
   success: function(msg){
       create_new_task_ui_dialog_internal(mfileid,msg)
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
}

function create_new_task_ui_dialog_internal(mfileid, jobdescriptions) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var job = $( "#jobtype" )
    var args = $( "#args" )
    allFields = $( [] ).add( job ).add(args)
    tips = $( ".validateTips" );

    $("#job-mfileid").val(mfileid)
    $("#args").empty()
    $("#argsmessage").empty()


    jobtypes = jobdescriptions['regular']

    for( t in jobtypes){
        $("#jobtype").append("<option value='"+jobtypes[t]+"'>"+jobtypes[t]+"</option>")
    }

    $("#jobtype").change(function() {
        selected = job.val()

        $("#args").empty()
        $("#argsmessage").empty()

        if(jobdescriptions['descriptions'][selected]){
           var targs = jobdescriptions['descriptions'][selected]['options']
           if(targs.length == 0){
                $("#argsmessage").append("<em>No arguments</em>")
            }

           for(t in targs){
                $("#args").append("<label for="+targs[t]+">"+targs[t]+"</label><input type='text' name="+targs[t]+" id="+targs[t]+"  value=''></input>")
           }
        }else{
            $("#argsmessage").append("<em>No arguments</em>")
        }
     });


        

    function updateTips( t ) {
        tips.text( t ).addClass( "ui-state-highlight" );
        setTimeout(function() {
                tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
    }

    $( "#dialog-new-job-dialog-form" ).dialog({
            autoOpen: false,
            height: 400,
            width: 450,
            modal: true,
            buttons: {
                    "Create Task": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );
                            if ( bValid ) {
                                    var data = $("#new-job-form").serialize()
                                    mfile_task_ajax(data)
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

    $( "#newjobbutton" )
        .button().click(function() {
                $( "#dialog-new-job-dialog-form").dialog( "open" );
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
                    "Add Methods": function() {
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