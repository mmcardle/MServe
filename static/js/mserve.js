
function load_user(userurl,consumerurl,template){
     $.ajax({
       type: "GET",
       url: userurl,
       success: function(msg){
            
            if(msg.mfiles.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Resources - Request a service using the form below "  } )
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

            $( template ).tmpl( msg.mfiles ).appendTo( "#user_mfileholder" );
            $( "#authTemplate" ).tmpl( msg.myauths ).appendTo( "#user_authholder" );

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
            $("#requestTemplate").tmpl(req).appendTo("#user-requests")
            $("#user-requests .amessage").remove()
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
            $("#request-"+request.id).replaceWith($("#requestTemplate").tmpl(request))
            make_request_buttons(requesturl,request)
       }
     });
}
function load_user_requests(requesturl){

     $.ajax({
       type: "GET",
       url: requesturl,
       success: function(requests){
            if(requests.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Pending Requests","cl":"amessage","isStaff": isStaff })
                message.css("width","400px")
                message.appendTo( "#user-requests" );
            }
            $("#requestTemplate").tmpl(requests).appendTo("#user-requests")
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
        update_service_request(requesturl,request,{"state":"A"})
    })
    $("#reject-button-"+request.id).button().click(function(){
        update_service_request(requesturl,request,{"state":"R"})
    })
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