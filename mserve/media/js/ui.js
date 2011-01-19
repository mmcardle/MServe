function create_new_render_ui(mfileid) {
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

