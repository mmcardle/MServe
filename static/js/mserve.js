

function mservetimeout(obj,mfileid,depth){
    $(obj).mserve('get_mfile_thumb', mfileid , depth )
}

function updatetasksetbuttons(serviceid, profileid, workflowid, taskset){

    $("#addbutton-task-"+taskset.id).button({icons: {primary: "ui-icon-disk"}}).click(
        function(){
                 data = $("#newtaskform-taskset-"+taskset.id).serialize()
                 $.ajax({
                   type: "POST",
                   data: data,
                   url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/',
                   success: function(newtask){
                        var tasktmpl = $("#taskTemplate" ).tmpl( newtask, { "tasksetid" : taskset.id }  )
                        tasktmpl.appendTo( "#tasksetbody-"+taskset.id );
                        updatetaskbuttons(serviceid, profileid, taskset.id, newtask.id)
                   },
                   error: function(msg){
                        showError("Error Adding Task",msg.responseText)
                    }
                 });
        }
    )

    deletefunction = function(){
         $.ajax({
           type: "DELETE",
           url: '/services/'+serviceid+'/profiles/'+profileid+'/tasksets/'+taskset.id+'/',
           success: function(msg){
               $( "#taskset-"+taskset.id ).remove();
           },
           error: function(msg){
                showError("Error Deleting Task", "")
            }
         });
    }
    $("#deletetasksetbutton-"+taskset.id).button({icons: {primary: "ui-icon-trash"}}).click(deletefunction)
}

function updatetaskbuttons(serviceid, profileid, tasksetid, taskid){
    deletefunction = function(){
         $.ajax({
           type: "DELETE",
           url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/'+taskid+'/',
           success: function(msg){
               $( "#task-"+taskid ).remove();
           },
           error: function(msg){
                showError("Error Deleting Task",msg.responseText)
            }
         });
    }
    updatefunction = function(){
            data = $("#taskform-task-"+taskid).serialize()
             $.ajax({
               type: "PUT",
               data: data,
               url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/'+taskid+'/',
               success: function(task){
                   var tasktmpl = $("#taskTemplate" ).tmpl( task, { "tasksetid" : tasksetid } )
                   console.log(task)
                   console.log(tasktmpl)
                    $( "#task-"+taskid ).replaceWith(tasktmpl);
                    updatetaskbuttons(serviceid, profileid, tasksetid, taskid)

               },
               error: function(msg){
                    showError("Error Updating Task",msg.responseText)
                }
             });
        }
    $("#edittaskbutton-"+taskid).button({icons: {primary: "ui-icon-disk"}}).click(updatefunction)
    $("#deletetaskbutton-"+taskid).button({icons: {primary: "ui-icon-trash"}}).click(deletefunction)
}

(function( $ ){

  var methods = {
    init : function( options ) { 
            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this), data = $this.data('mserve')

                $table = $("#mserveTemplate").tmpl()
                $table.find("#mserve-new-folder-button").button(
                    { icons: { primary: "ui-icon-circle-plus"} }
                ).click( function(){
                    selected = $("#mfoldertreecontainer").jstree('get_selected')
                    alert("TODO - Create folder at "+selected)
                })
                $(obj).append($table);

                 // If the plugin hasn't been initialized yet

                 if ( ! data ) {
                   $(this).data('mserve', {
                       target : $this,
                       table : $table
                   });
                 }

            });
    },
    get_mfile_thumb: function(mfileid, depth){

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');

            if(depth>3){
               return
            }else{
               $.ajax({
                   type: "GET",
                   url: "/mfiles/"+mfileid+"/",
                   success: function(newmfile){
                        if(newmfile.thumb != ""){
                            var mfilecache = $(data.allcontent[0]).find("#mfile-table-"+mfileid)
                            mfilecache.css("background-image", "url('"+newmfile.thumburl+"')");
                            $("#mfile-table-"+mfileid).css("background-image", "url('"+newmfile.thumburl+"')");
                        }else{
                            setTimeout(mservetimeout,3000 ,obj,mfileid, depth+1)
                        }
                   }
               });
            }

        });
    },
    updatemfile : function( mfileid, options ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                $("#newjobbutton-"+mfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
                $('#newjobbutton-'+mfileid).click(function(){
                    $("#mfileid").val(mfileid);
                    $("#dialog-new-job-dialog-form").dialog( "open" );
                });
                $("#deletemfilebutton-"+mfileid ).button({ icons: { primary: "ui-icon-trash"}, text: false });
                $('#deletemfilebutton-'+mfileid).click(function(){
                    $("#mservetree").mserve('deletemfile', mfileid)
                });

                if(options.pollthumb){
                    obj.mserve('get_mfile_thumb', mfileid, 1)
                }
            });
    },
    showFolder : function( mfolderid ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');

                var $filteredData = $(data.allcontent[0]).find('li.'+mfolderid);

                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });
            });
    },
    deletemfile : function(mfileid) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');

                $( '#dialog-mfile-dialog' ).dialog({
                        resizable: false,
                        modal: true,
                        buttons: {
                                "Delete mfile?": function() {
                                     $.ajax({
                                       type: "DELETE",
                                       url: '/mfiles/'+mfileid+"/",
                                       success: function(msg){
                                            $(data.allcontent[0]).find("#mfileholder-"+mfileid).remove()
                                            $("#mfileholder-"+mfileid).hide('slide')
                                            $("#mfoldertreecontainer").jstree('delete_node',"#"+mfileid)
                                       },
                                       error: function(msg){
                                            alert( "Failure On Delete " + msg );
                                       }
                                     });
                                        $( this ).dialog( "close" );
                                },
                                Cancel: function() {
                                        $( this ).dialog( "close" );
                                }
                        }
                });
            });
    },
    add : function( mfile ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                // Update MFile before cloning
                $(obj).mserve('updatemfile', mfile.id, {"pollthumb":"true"})

                $(data.allcontent[0]).append($("#mfileholder-"+mfile.id).clone(true))
            });
    },
    serviceprofiles : function(serviceid){

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                $.ajax({
                   type: "GET",
                   url: "/tasks/",
                   success: function(tasks){
                        $.ajax({
                           type: "GET",
                           url: "/services/"+serviceid+"/profiles/",
                           success: function(profiles){

                                if(profiles.length==0){
                                     $("#profilemessages").append("<div id='noprofiles' class='message' >No profiles</div>");
                                    return False;
                                }else{
                                    $("#noprofiles").remove()
                                }
                                
                                var profiletabs = $( "<div></div>")
                                $( "#profileTabsTemplate" ).tmpl( {"profiles":profiles } ) .appendTo( profiletabs );
                                $( "#profileTemplate" ).tmpl( profiles ) .appendTo( profiletabs );
                                profiletabs.appendTo("#profilepaginator")
                                profiletabs.tabs()

                                $(".workflow-accordian").accordion({
                                    collapsible: true,
                                    autoHeight: false,
                                    navigation: true
                                }).accordion( "activate" , false )

                                $(profiles).each(function(pindex,profile){
                                    $(profile.workflows).each(function(windex,workflow){
                                        $("#addbutton-taskset-"+workflow.id).button({icons: {primary: "ui-icon-disk"}}).click(
                                        function(){
                                                 data = $("#newtasksetform-workflow-"+workflow.id).serialize()
                                                 $.ajax({
                                                   type: "POST",
                                                   data: data,
                                                   url: '/services/'+serviceid+'/profiles/'+profile.id+'/tasksets/',
                                                   success: function(newtaskset){
                                                       console.log(newtaskset)
                                                        var tasksettmpl = $("#taskSetTemplate" ).tmpl( newtaskset, { "workflowid" : workflow.id } )
                                                        tasksettmpl.appendTo("#workflowbody-"+workflow.id );
                                                        updatetasksetbuttons(serviceid, profile.id, workflow.id, newtaskset)
                                                   },
                                                   error: function(msg){
                                                        showError("Error Adding Task Set",msg.responseText)
                                                    }
                                                 });
                                            }
                                        )
                                        $("#workflowbody-"+workflow.id).sortable({
                                            update : function(event, ui){
                                                var tasksetid = $(ui.item[0]).attr("data-taskid")

                                                $("#workflowsavedmsg-"+workflow.id).show()
                                            }
                                        })
                                        $("#workflowbody-savebutton-"+workflow.id).button().click(
                                            function(){
                                                $("#workflowbody-"+workflow.id).find(".taskset").each( function(tindex,taskset){
                                                    $("#workflowsavedmsg-"+workflow.id).hide()
                                                    var tasksetid = $(taskset).attr("data-taskid")
                                                    var index = $(taskset).parent().children().index(taskset)
                                                    form = $(taskset).find("#tasksetupdateform-taskset-"+tasksetid)
                                                    form.find("input[name=order]").val(index)
                                                    data = form.serialize()
                                                     $.ajax({
                                                           type: "PUT",
                                                           data: data,
                                                           url: '/services/'+serviceid+'/profiles/'+profile.id+'/tasksets/'+tasksetid+'/',
                                                           success: function(updatedtaskset){
                                                               var tasksettmpl = $("#taskSetTemplate").tmpl( updatedtaskset , {"workflowid":workflow.id}  )
                                                               $( "#taskset-"+updatedtaskset.id ).replaceWith(tasksettmpl);
                                                               updatetasksetbuttons(serviceid, profile.id, workflow.id, updatedtaskset)
                                                               $(updatedtaskset.tasks).each(function(newtindex, task){
                                                                    updatetaskbuttons(serviceid, profile.id, updatedtaskset.id, task.id)
                                                                });
                                                           },
                                                           error: function(msg){
                                                                showError("Error Updating TaskSet ", "")
                                                            }
                                                         });

                                                    })
                                                }
                                        )

                                        $(workflow.tasksets).each(function(tsindex,taskset){
                                            updatetasksetbuttons(serviceid, profile.id, workflow.id, taskset)
                                            $(taskset.tasks).each(function(tindex, task){
                                                updatetaskbuttons(serviceid, profile.id, taskset.id, task.id)
                                            });
                                        });
                                    });
                                });

                                $(".task_name").autocomplete({
                                        source: tasks.regular
                                });

                                return false;
                           }
                         });
                    }
                });
            });

    },
    load : function( options ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var serviceid = o.serviceid
                var mfolder_set = o.mfolder_set
                var mfile_set =  o.mfile_set
                var folder_structure = o.folder_structure

                $("#mfolderTemplate").tmpl(mfolder_set).appendTo("#qscontainer")
                $("#mfileTemplate").tmpl(mfile_set).appendTo("#qscontainer")

                var $this = $(this),
                data = $this.data('mserve');

                // Update MFile before cloning
                $(mfile_set).each( function(index,mfile) {
                    $(obj).mserve( 'updatemfile', mfile.id, { "pollthumb":"false" })
                });

                var allcontent = $('#qscontainer').clone(true)
                data["allcontent"] = allcontent

                var $filteredData = allcontent.find('li.rootfolder');
                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });

                $("#mfoldertreecontainer").jstree({
                     "json_data" : folder_structure,
                     "themes" : { "theme" : "default" },
                     "plugins" : [ "themes", "json_data", "ui", "crrm"]
                    }
                ).bind("select_node.jstree", function (event, data) {
                        id = data.rslt.obj.attr('id');

                        if(id==serviceid){
                            var $filteredData = allcontent.find('li.rootfolder');

                            $('#qscontainer').quicksand($filteredData, {
                              duration: 800,
                              easing: 'easeInOutQuad'
                            });
                        }else{
                            mfile = $("#mfileholder-"+id)
                            if(mfile.length>0){
                                var $filteredData = allcontent.find('li.'+id);

                                $('#qscontainer').quicksand($filteredData, {
                                  duration: 800,
                                  easing: 'easeInOutQuad'
                                });
                            }else{
                                mfolder = $("#mfolderholder-"+id)
                                if(mfolder){
                                    var $filteredData = allcontent.find('li.'+id);

                                    $('#qscontainer').quicksand($filteredData, {
                                      duration: 800,
                                      easing: 'easeInOutQuad'
                                    });
                                }
                            }
                        }
                }).bind("loaded.jstree", function (event, data) {
                    $("#mfoldertreecontainer").jstree("open_all");
                });

            });
    }
  };

  $.fn.mserve = function( method ) {

    // Method calling logic
    if ( methods[method] ) {
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.tooltip' );
    }

  };

})( jQuery );

function load_user(userurl,consumerurl,template){
     $.ajax({
       type: "GET",
       url: userurl,
       success: function(msg){
            
            if(msg.mfiles.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Resources"  } )
                message.css("width","400px")
                message.appendTo( "#user_mfilemessages" );
                $( "#user-request-service" ).show()
            }else{
                $("#user_mfilemessages").empty()
            }

            if(msg.myauths.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Auths - Request a service using the form below "  } )
                message.css("width","400px")
                message.appendTo( "#user_authmessages" );
                $( "#user-request-service" ).show()
            }else{
                $("#user_authmessages").empty()
            }

            var mfiles = msg.mfiles

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>mfiles.length){
                    end=mfiles.length;
                }

                $( template ).tmpl( mfiles.slice(start,end) ) .appendTo( "#user_mfileholder" );
                return false;
            }


            // First Parameter: number of items
            // Second Parameter: options object
            $("#user_mfileholder").pagination(mfiles.length, {
                    items_per_page:4,
                    callback:handlePaginationClick
            });

            var myauths = msg.myauths

            function handlePaginationClick2(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>myauths.length){
                    end=myauths.length;
                }

                $( "#authTemplate" ).tmpl( myauths.slice(start,end) ) .appendTo( "#user_authholder" );
                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#user_authholder").pagination(myauths.length, {
                    items_per_page:4,
                    callback:handlePaginationClick2
            });

            oauth_token = getParameterByName("oauth_token")

            $(".infoholder input[type='checkbox']").each(function(index){
                $(this).button().click(
                function(){
                    var id = $(this).attr('id')
                    if($(this).is(':checked')){
                        ajax_update_consumer_oauth(id,oauth_token,consumerurl)
                    }else{
                        ajax_delete_consumer_oauth(id,oauth_token,consumerurl)
                    }
                });
            } );

       }
     });
}


function user_request_service(requesturl){

    data = $("#user-request-service-form").serialize()

    var errorfield = $("#user-request-service-form-errors")
    errorfield.empty()

    var namefield = $("#user-request-service-form #id_name")
    namefield.removeClass( "ui-state-error" );
    if ( namefield.val() == "" || namefield.val() == null ) {
            namefield.addClass( "ui-state-error" );
            errorfield.text("Name field must not be empty")
            return false;
    }

    var reasonfield = $("#user-request-service-form #id_reason")
    reasonfield.removeClass( "ui-state-error" );
    if ( reasonfield.val() == "" || reasonfield.val() == null ) {S
            reasonfield.addClass( "ui-state-error" );
            errorfield.text("Please enter a reason!")
            return false;
    }

     $.ajax({
       type: "POST",
       url: requesturl,
       data: data,
       success: function(req){
            errorfield.empty()
            namefield.removeClass( "ui-state-error" );
            namefield.val("")
            reasonfield.removeClass( "ui-state-error" );
            reasonfield.val("")
            $("#requestTemplate").tmpl(req).prependTo("#pending-requests")
            $("#pending-requests .amessage").remove()
            make_request_buttons(requesturl,req)
            
       }
     });
}

function delete_service_request(url,request){

     $.ajax({
       type: "DELETE",
       url: url+request.id+"/",
       success: function(msg){
            $("#request-"+request.id).remove()
       }
     });
}
function update_service_request(requesturl,request,data){

     $.ajax({
       type: "PUT",
       url: requesturl+request.id+"/",
       data: data,
       success: function(request){
            $("#request-"+request.id).remove()
            if(!$("#pending-requests").html().trim()){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Pending Requests","cl":"amessage","isStaff": isStaff })
                message.appendTo( "#pending-requests" );
            }
            $("#requestTemplate").tmpl(request).prependTo("#done-requests")
            make_request_buttons(requesturl,request)
       }
     });
}

function load_user_requests(requesturl){

     $.ajax({
       type: "GET",
       url: requesturl,
       success: function(requests){

            pending = []
            done = []

            $(requests).each(function(index,request){
                if(request.state == "P"){
                    pending.push(request)
                }else{
                    done.push(request)
                }
            })

            if(pending.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Pending Requests","cl":"amessage","isStaff": isStaff })
                message.appendTo( "#pending-requests" );
            }

            if(done.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Requests","cl":"amessage","isStaff": isStaff })
                message.appendTo( "#done-requests" );
            }

            $("#requestTemplate").tmpl(pending).appendTo("#pending-requests")
            $("#requestTemplate").tmpl(done).appendTo("#done-requests")
            $(requests).each(function(index,request){
                make_request_buttons(requesturl,request)
            })
       }
     });
}

function make_request_buttons(requesturl,request){
    $("#delete-button-"+request.id).button().click(function(){
        delete_service_request(requesturl,request)
    })
    $("#approve-button-"+request.id).button().click(function(){
        //update_service_request(requesturl,request,{"state":"A"})

        data = {"requesturl":requesturl,"request":request,"state":"A" }

        chooseContainer(data)
    })
    $("#reject-button-"+request.id).button().click(function(){
        update_service_request(requesturl,request,{"state":"R"})
    })
}

function mycallback(val,data){
    update_service_request(data.requesturl,data.request,{"state":data.state,"cid":val})
}

function chooseContainer(data){
    $.ajax({
       type: "GET",
       url: "/containers/",
       success: function(msg){
            containers = msg;
            choices = []
            $(containers).each(function(index,container){
               choices.push( {"name":container.name,"value":container.id} )
            })
            choose_dialog_ui(choices,"Input Needed", "Choose a Container", mycallback, data)
       }
     });
}

function choose_dialog_ui(choices, title, message, callback, data) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var containers = $( "#containers" ),
    allFields = $( [] ).add( containers ),
    tips = $( ".validateTips" );

    id = "dialog-id-"+Math.floor(Math.random()*1000)

    cdialog = $("#dialogTemplate").tmpl( {"id": id , "message" : message, "title": title } )

    inputbox = $('<select type="radio" >')

    $(choices).each(function(index,choice){
        $('<option value="'+choice.value+'" >'+choice.name+'</option>').appendTo(inputbox)
    })

    cdialog.append(inputbox)

    cdialog.dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                    "Choose Container": function() {
                        callback(inputbox.val(),data)
                        $( this ).dialog( "close" );

                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            },
            close: function() {
                    allFields.val( "" ).removeClass( "ui-state-error" );
            }
    });

    cdialog.dialog( "open" );

}

function ajax_update_consumer_oauth(id,oauth_token,consumerurl){

    var dataArr = {
        "oauthtoken" : ""+oauth_token+"",
        "id" : ""+id+""
    }

    var data = $.param(dataArr)

     $.ajax({
       type: "PUT",
       url: consumerurl,
       data: data,
       success: function(msg){
            
       }
     });
}

function ajax_delete_consumer_oauth(id,oauth_token,consumerurl){
     $.ajax({
       type: "DELETE",
       url: consumerurl+"/"+id+"/"+oauth_token+"/",
       success: function(msg){

       }
     });
}

var serviceid = ""
function loadMFiles(sid){
    serviceid = sid
    reloadMFiles();
}

function reloadMFiles(newfileid){
    $.ajax({
       type: "GET",
       url: "/services/"+serviceid+"/mfiles/",
       success: function(msg){
            mfiles = msg;

            if(mfiles.length==0){
                 $("#mfilemessages").append("<div id='nofiles' class='message' >No Files</div>");
                return;
            }else{
                $("#nofiles").remove()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>mfiles.length){
                    end=mfiles.length;
                }

                $( "#managedresourcesmfilescontent" ).empty()
                $( "#mfileTemplate" ).tmpl( mfiles.slice(start,end) ) .appendTo( "#managedresourcesmfilescontent" );

                for(var i=start; i<end; i++){
                    (function() {
                        var gid = i;
                        var gmfileid = mfiles[gid].id;
                        mfile_buttons(gmfileid)
                    })();
                }

                if(newfileid != null){
                    $("#image-"+newfileid).show('drop')
                }

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object

            // Render the template with the data and insert
            // the rendered HTML under the "mfilepaginator" element
            $("#mfilepaginator").pagination(mfiles.length, {
                    items_per_page:12,
                    callback:handlePaginationClick
            });
       }
     });
}

function showMFolder(mfolderid){
    $("#mservetree").mserve( 'showFolder' , mfolderid);
}

function loadMFile(mfile){
    $("#nofiles").remove()
    var $mft = $("#mfileTemplate" ).tmpl( mfile )
    $mft.appendTo( "#qscontainer" );

    $("#mservetree").mserve( 'add' , mfile );

    pnode = $("#mfoldertreecontainer .service")

    $("#mfoldertreecontainer").jstree("create", pnode, "first",
        { "data" : {
                "title" : mfile.name,
                "icon" : mfile.thumburl
                },
            "attr" : {
                "id": mfile.id,
                "class" : "mfile"
                }
        }, null, true    );

}

function doMFileButtons(mfile){
    (function() {
        var gid = mfile.id;
        var gmfileid = mfile.id;
        mfile_buttons(gmfileid)
        get_mfile_thumb(mfile)
    })();
}

function showmfiledialog(gmfileid){
        create_new_job_ui_dialog(gmfileid,true)
        $("#mfileid").val(gmfileid);
        $("#dialog-new-job-dialog-form").dialog( "open" );
}

function mfile_buttons(gmfileid){
    $("#newjobbutton-"+gmfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
    $('#newjobbutton-'+gmfileid).click(function(){
        create_new_job_ui_dialog(gmfileid,true)
        $("#mfileid").val(gmfileid);
        $("#dialog-new-job-dialog-form").dialog( "open" );
    });
    $("#deletemfilebutton-"+gmfileid ).button({ icons: { primary: "ui-icon-trash"}, text: false });
    $('#deletemfilebutton-'+gmfileid).click(function(){
        $("#mservetree").mserve('deletemfile', gmfileid)
    });
}

function mfile_delete(mfileid){
        $("#mservetree").mserve('deletemfile', mfileid)
 }

$(document).ready(function(){
	$('.accordion .head').click(function() {
		$(this).next().toggle('slow');
		return false;
	}).next().hide();
});

function mfile_get(mfileid){
        window.open("/mfileapi/get/"+mfileid+"/")
}

function getPoster(mfileid){
    url = '/mfile/'+mfileid+'/'
    $.getJSON(url, function(data) {
        if(data.poster!=""){
            $("#mfileposter").attr("src", "/"+data.posterurl)
        }else{
            window.setTimeout("getPoster(\'"+mfileid+"\')",1000)
        }
    });
 }

 function mfile_verify(mfileid){
     url = '/mfileapi/verify/'+mfileid+'/'
     $.getJSON(url, function(data) {
        if(data.md5==data.mfile.checksum){
            showMessage("Success: Verification OK","MD5: "+data.md5+"<br>Checksum: "+data.mfile.checksum)
            //id = $("<div class='passed'><div>Success: Verification OK</div>"+ data.md5 + "</div>")
            //$(id).appendTo("#message");
        }else{
            showError("Error: Verification has failed","MD5: "+data.md5+"<br>Checksum: "+data.mfile.checksum)
        }
    });
 }

 function add_auth_method(roleid){


    $( '#dialog-mfile-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete mfile?": function() {
                         $.ajax({
                           type: "DELETE",
                           url: '/mfile/'+mfileid+"/",
                           success: function(msg){
                                showMessage("File Deleted","The mfile has been deleted.")
                           },
                           error: function(msg){
                             alert( "Failure On Delete " + msg );
                           }
                         });
                            $( this ).dialog( "close" );
                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });

    var methods = prompt("What methods do you wish to add\nComma separated", "");
    if (methods == null)
        return;
    if (methods == "")
        return;
    $.ajax({
       type: "PUT",
       url: '/roles/'+roleid+"/",
       data: "methods="+methods,
       success: function(msg){
           poplulate_methods(roleid,msg["methods"])
       },
       error: function(msg){
         alert( "Failure to add methods '" + methods + "'\nStatus: '" + msg.status+ "'\nResponse Text:\n" + msg.responseText);
       }
     });
 }