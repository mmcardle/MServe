
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

function create_new_job_ui_dialog(mfileid, servicepage) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var job = $( "#jobtype" )
    var args = $( "#args" )
    var inputs = $( "#inputs" )
    allFields = $( [] ).add( job ).add(args).add(inputs)
    tips = $( ".validateTips" );

    $("#args").empty()
    $("#argsmessage").empty()
    $("#inputs").empty()
    $("#inputsmessage").empty()

    $.ajax({
       type: "GET",
       url: "/mfiles/"+mfileid+"/",
       success: function(mfile){
            $( "#mfileNoActionTemplate" ).tmpl( mfile ).appendTo("#job-input-preview");
        }
    });

    $.ajax({
       type: "GET",
       url: tasks_url,
       success: function(jobdescriptions){

            jobtypes = jobdescriptions['regular']

            $("#jobtype").empty()
            for( t in jobtypes){
                $("#jobtype").append("<option value='"+jobtypes[t]+"'>"+jobtypes[t]+"</option>")
            }

            $("#jobtype").change(function() {
                selected = job.val()

                $("#args").empty()
                $("#argsmessage").empty()
                $("#inputs").empty()
                $("#inputsmessage").empty()

                if(jobdescriptions['descriptions'][selected]){
                   var targs = jobdescriptions['descriptions'][selected]['options']
                   var nbinputs = jobdescriptions['descriptions'][selected]['nbinputs']

                   if(targs.length == 0){
                        $("#argsmessage").append("<em>No arguments</em>")
                   }

                   for(t in targs){
                        $("#args").append("<label for="+targs[t]+">"+targs[t]+"</label><input type='text' name="+targs[t]+" id="+targs[t]+"  value=''></input>")
                   }

                    if(nbinputs == 0){
                        $("#inputsmessage").append("<em>No inputs</em>")
                    }

                    $("#job-extra-input-preview").empty();
                    ia = []
                    for (var i=0;i<nbinputs;i++){
                        ia.push(i)
                    }
                    $(ia).each(function(index,i)
                    {
                        inputkey = 'input-'+i
                        inputlabel = 'input-'+(i+1)
                        input = jobdescriptions['descriptions'][inputkey]
                        initialvalue = ""
                        if(i==0){
                            value=mfileid
                            $("#inputs").append("<input type='hidden' name="+inputkey+" id="+inputkey+"  value='"+value+"'></input>")
                        }else{
                            var $chooser = $( "#mfileChooserTemplate" ).tmpl( {"id" : "mfile-chooser-"+i} )
                            $chooser.appendTo("#job-extra-input-preview");
                            $chooser.find("button").button().click(function( ){
                                $.ajax({
                                   type: "GET",
                                   url: users_url,
                                   success: function(user){
                                        $("#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder").empty()
                                        create_new_choose_mfile_ui_dialog()
                                        $(user.mfiles).each(function(index,mfile){
                                            tmpl = $( "#mfileNoActionTemplate" ).tmpl( mfile )
                                            tmpl.appendTo( "#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder")
                                            tmpl.click(function(){
                                                $("#mfile-chooser-"+i).replaceWith(this)
                                                $("#dialog-choose-mfile-dialog-form").dialog( "close" )
                                                $("input[name='"+inputkey+"']").val(mfile.id)
                                            })

                                        })
                                        $(user.myauths).each(function(index,auth){
                                            tmpl = $( "#mfileNoActionTemplate" ).tmpl( auth )
                                            tmpl.appendTo( "#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder")
                                            tmpl.click(function(){
                                                $("#mfile-chooser-"+i).replaceWith(this)
                                                $( "#dialog-choose-mfile-dialog-form").dialog( "close" )
                                                $("input[name='"+inputkey+"']").val(auth.id)
                                            })

                                        })


                                    }
                                });
                            })
                            $("#inputs").append("<input type='hidden' name="+inputkey+" id="+inputkey+"  value=''></input>")
                        }

                    });
                }
             });
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
            height: 500,
            width: 750,
            modal: true,
            buttons: {
                    "Create Task": function() {
                            var bValid = true;
                            allFields.removeClass( "ui-state-error" );
                            if ( bValid ) {
                                    var data = $("#new-job-form").serialize()
                                    mfile_job_ajax(mfileid,data);
                                    if(servicepage){
                                        $("#tabs").tabs('select',"jobs-tab");
                                    }
                                    $( this ).dialog( "close" );
                            }
                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            },
            close: function() {
                    allFields.val( "" ).removeClass( "ui-state-error" );
                    $("#args").empty();
                    $("#argsmessage").empty();
                    $("#inputs").empty();
                    $("#inputsmessage").empty();
                    $("#job-extra-input-preview").empty()
                    if(servicepage){
                        $("#job-input-preview").empty()
                    }
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