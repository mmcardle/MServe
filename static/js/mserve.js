
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
                console.log($("#pending-requests").html())
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

function get_mfile_thumb(mfile){
    function f(depth) {
       if(depth>3){ return }
       $.ajax({
           type: "GET",
           url: "/mfiles/"+mfile.id+"/",
           success: function(newmfile){
                if(newmfile.thumb != ""){
                    $("#mfile-table-"+mfile.id).css("background-image", "url('"+newmfile.thumburl+"')");
                }else{
                    window.setTimeout(f, 3000, depth+1);
                }
           }
       });
    }
    window.setTimeout(f, 3000, 0);
}

function loadMFile(mfile){
    $("#nofiles").remove()
    $("#mfileTemplate" ).tmpl( mfile ) .prependTo( "#managedresourcesmfilescontent" );
    $("#image-"+mfile.id).show('drop');

    (function() {
        var gid = mfile.id;
        var gmfileid = mfile.id;
        mfile_buttons(gmfileid)
        get_mfile_thumb(mfile)
    })();
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
        mfile_delete(gmfileid)
    });
}

function mfile_delete(mfileid){
    $( '#dialog-mfile-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete mfile?": function() {
                         $.ajax({
                           type: "DELETE",
                           url: '/mfiles/'+mfileid+"/",
                           success: function(msg){
                                $("#mfileholder-"+mfileid).hide('slide')
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