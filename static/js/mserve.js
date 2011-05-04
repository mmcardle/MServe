

function load_user(){

     $.ajax({
       type: "GET",
       url: '/users/',
       success: function(msg){
            $( "#mfileOAuthTemplate" ).tmpl( msg.mfiles ).appendTo( "#user_mfileholder" );
            $( "#mfolderOAuthTemplate" ).tmpl( msg.mfolders ).appendTo( "#user_mfileholder" );
            $( "#serviceOAuthTemplate" ).tmpl( msg.dataservices ).appendTo( "#user_mfileholder" );

            oauth_token = getParameterByName("oauth_token")

            $(".infoholder input[type='checkbox']").each(function(index){
                $(this).button().click(
                function(){
                    var id = $(this).attr('id')
                    ajax_update_consumer_oauth(id,oauth_token)
                });
            } );

       },
       error: function(msg){
            showError("Error Loading Jobs",objectToString(msg))
       }
     });
}

function ajax_update_consumer_oauth(id,oauth_token){

    var dataArr = {
        "oauthtoken" : ""+oauth_token+"",
        "id" : ""+id+""
    }

    var data = $.param(dataArr)

     $.ajax({
       type: "PUT",
       url: '/consumer/',
       data: data,
       success: function(msg){
            showMessage("Success",objectToString(msg))
       },
       error: function(msg){
            showError("Error Loading Jobs",objectToString(msg))
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
       url: "/service/"+serviceid+"/",
       success: function(msg){
            mfiles = msg[0].mfile_set;

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
                        $("#newjobbutton-"+gmfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
                        $('#newjobbutton-'+gmfileid).click(function(){
                            create_new_job_ui_dialog(gmfileid, serviceid)
                            $("#mfileid").val(gmfileid);
                            $("#serviceid").val(serviceid);
                            $("#dialog-new-job-dialog-form").dialog( "open" );
                        });
                    })();
                }

                if(newfileid != null){
                    $("#image-"+newfileid).show('bounce')
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
       },
       error: function(msg){
            showError( "Failure to get files",msg );
       }
     });
}

function loadMFile(mfile){
    $("#nofiles").remove()
    $("#mfileTemplate" ).tmpl( mfile ) .prependTo( "#managedresourcesmfilescontent" );
    $("#image-"+mfile.id).show('bounce');

    (function() {
        var gid = mfile.id;
        var gmfileid = mfile.id;
        $("#newjobbutton-"+gmfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
        $('#newjobbutton-'+gmfileid).click(function(){
            create_new_job_ui_dialog(gmfileid, serviceid)
            $("#mfileid").val(gmfileid);
            $("#serviceid").val(serviceid);
            $("#dialog-new-job-dialog-form").dialog( "open" );
        });
    })();

}

function loadJobs(serviceid){
     $.ajax({
       type: "GET",
       url: '/serviceapi/getjobs/'+serviceid+"/",
       success: function(msg){
            for (i in msg){
                create_job_holder(msg[i])
                if(!msg[i].ready){
                    check_job(msg[i],serviceid)
                }
            }
       },
       error: function(msg){
            showError("Error Loading Jobs",objectToString(msg))
       }
     });
}

function create_job_paginator(task){

        var job = task.job
        var jobid = job.id
        var joboutputs = job.joboutput_set
        var jobresults = task.result
        
        var jobpaginator = $("#jobpreviewpaginator-"+jobid)

        function handlePaginationClick(new_page_index, jobpaginator) {
            // This selects elements from a content array
            start = new_page_index*this.items_per_page
            end   = (new_page_index+1)*this.items_per_page

            if(end>joboutputs.length){
                end=joboutputs.length;
            }

            $( "#jobOutputTemplate" ).tmpl( joboutputs.slice(start,end) ) .appendTo( jobpaginator );

            for(var j=start;j<end;j++) {
                if(joboutputs[j].mimetype && joboutputs[j].mimetype.startsWith('text')){
                    load_joboutput_text(joboutputs[j].id)
                }
            }
            return false;
        }

        // First Parameter: number of items
        // Second Parameter: options object
        jobpaginator.pagination(joboutputs.length, {
                items_per_page:4,
                callback:handlePaginationClick
        });
}

function load_joboutput_text(id){

 $.ajax({
   type: "GET",
   url: "/jobapi/contents/"+id+"/",
   success: function(msg){
                $("#text-"+id).append("<pre>"+msg+"</pre>");
   },
   error: function(msg){
                $("#text-"+id).append("<h3 class='error'>Error</h3><pre>"+msg+"</pre>");
   }
 });
}

function load_render_preview(mfileid){

 $.ajax({
   type: "GET",
   url: "/jobapi/getjobs/"+mfileid+"/",
   success: function(msg){
      var thumbs = []
      for(i in msg){
            task = msg[i]
            job = task.job
            job.joboutput_set[0].thumburl
            
            if(job.joboutput_set.length > 0){
                thumbs.push(job.joboutput_set[0].thumburl)
            }
      }
        $("#previewcontent").append("<div style='clear:both' ></div>")
      for(i in thumbs){
        $("#previewcontent").append("<img src='"+thumbs[i]+"' />")
      }
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });

}

function load_jobs_mfile(mfileid){
     $.ajax({
       type: "GET",
       url: '/jobapi/getjobs/'+mfileid+"/",
       success: function(msg){
        if(msg.length > 0){
            $("#jobs").empty()
        }
            for (i in msg){
                create_job_holder(msg[i])
                if(!msg[i].ready){
                    check_job(msg[i],mfileid)
                }
            }
       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function create_job_holder(task){
    var job = task.job
    var jobholder = $("#job-"+job.id)
    if (jobholder.length == 0){

        $( "#jobTemplate" ).tmpl( task ) .prependTo( "#jobs" );

        var allDone = true

        var jobs = $("#job-"+job.id)
        var percent = (task.completed_count/task.total)*100
        var info = $( "#jobinfo-"+job.id )
        var icon = $( "#jobicon-"+job.id )
        var progressbar = $( "#jobprogressbar-"+job.id )

        if(job.waiting){
            icon.addClass('taskrunning')
        }else{
            icon.addClass('ui-icon-check')
            icon.removeClass('taskrunning')
        }

        progressbar.progressbar({
                value: percent
        });


        var id = job.id
        $('#jobpreviewpaginator-'+id).hide()
        $("#joboutputs-"+id).hide()
        $('#jobheader-'+id).click(function() {          create_job_paginator(task);show_job(task);     });
        $('#jobicon-'+id).click(function() {            create_job_paginator(task);show_job(task);     });
        $('#jobinfo-'+id).click(function() {            create_job_paginator(task);show_job(task);     });
        $('#jobprogressbar-'+id).click(function() {     create_job_paginator(task);show_job(task);     });

        $("#jobdeletebutton-"+id ).button({ icons: { primary: "ui-icon-circle-close"}, text: false });
        $("#jobdeletebutton-"+id ).click(function() {           delete_job(id) });

        update_job_outputs(task)

        if(task.failed){
            $('#job-'+job.id).addClass('ui-state-error')
        }else{
            //update_job_outputs(task)
            //show_job(task)
        }

    }
}

function update_job_outputs(task){
    id = task.job.id
    $("#joboutputs-"+id).empty()
    for(i in task.result){
        var resultdict = task.result[i]
        result = ""
        for(k in resultdict){
            result += " <span style='color:green' >"+k+"</span> : <span style='color:blue' >"+resultdict[k] + "</span>"
        }
        if(result != ""){
            v = 1 + parseInt(i)
            $("#joboutputs-"+id).append("<div><b>Result "+v+" :</b> "+result+"</div>")
        }
    }
}

function show_job(task){
    id = task.job.id
    if(task.job.joboutput_set.length > 0){
        $('#jobpreviewpaginator-'+id).toggle('blind');
    }
    if(task.result.length > 0){
        $('#joboutputs-'+id).toggle('slide');
    }
}

function check_job(task){
    var job = task.job
     $.ajax({
       type: "GET",
       url: '/jobapi/'+job.id+"/",
       success: function(msg){
        var allDone = true

        var jobs = $("#job-"+job.id)
        var percent = (msg.completed_count/msg.total)*100
        var info = $( "#jobinfo-"+job.id )
        var icon = $( "#jobicon-"+job.id )
        var progressbar = $( "#jobprogressbar-"+job.id )

        if(msg.waiting){
            icon.removeClass('ui-icon ui-icon-circle-check')
            icon.addClass('taskrunning')
        }else{
            icon.addClass('ui-icon ui-icon-circle-check')
            icon.removeClass('taskrunning')
        }

        info.html("<b>"+msg.completed_count+"</b> frames of <b>"+msg.total+"</b> complete : "+Math.round(percent)+"%" )

        progressbar.progressbar({
                value: percent
        });

        if(msg.waiting){
            window.setTimeout(function(){ check_job(msg) },5000)
        }else{
            if(msg.failed){
                $('#job-'+job.id).addClass('ui-state-error')
            }else{
                create_job_holder(msg)
                create_job_paginator(msg)
                update_job_outputs(msg)
                show_job(msg)
            }
        }

       },
       error: function(msg){
            showError("Error Checking Job",objectToString(msg))
       }
     });
 }
function delete_job(jobid){
    $( '#dialog-job-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete Job?": function() {
                              $.ajax({
                               type: "DELETE",
                               url: '/jobapi/'+jobid+"/",
                               success: function(msg){
                                    $('#job-'+jobid).hide('blind')
                                    $('#jobheader-'+jobid).hide()
                               },
                               error: function(msg){
                                    showError("Job Deleted Error",objectToString(msg))
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
function mfile_delete(mfileid){
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