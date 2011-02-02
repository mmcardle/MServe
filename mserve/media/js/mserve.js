
function loadContainers(){
    $.ajax({
       type: "GET",
       url: "/container/",
       success: function(msg){
            containers = msg;

            $(".numcontainers").html(containers.length);
            if(containers.length==0){
                 $("#containermessages").append("<div id='nocontainers' class='message'>No Containers</div>");
                return;
            }else{
                $("#nocontainers").remove()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>containers.length){
                    end=containers.length;
                }
                for(var i=start;i<end;i++) {
                    var c = $("<div>"+containers[i].name+"  <a href='/browse/"+containers[i].id+"/'>"+containers[i].id+"</a>&nbsp;<em>"+containers[i].dataservice_set.length+" services</em></div>")
                    $('#containerpaginator').append(c)
                }
                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#containerpaginator").pagination(msg.length, {
                    items_per_page:20,
                    callback:handlePaginationClick
            });
       },
       error: function(msg){
            showError( "Failure to get containers ",msg );
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

                for(var i=start;i<end;i++) {
                    var c = $("<div>"+services[i].name+"  <a href='/browse/"+services[i].id+"/'>"+services[i].id+"</a>&nbsp;<em>"+services[i].mfile_set.length+" files</em></div>")
                    $('#servicepaginator').append(c)
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

                $( "#mfileList" ).empty()
                $( "#mfileTemplate" ).tmpl( mfiles.slice(start,end) ) .appendTo( "#mfileList" );

                if(newfileid != null){
                    $("#image-"+newfileid).show('bounce')
                }

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object

            // Render the template with the movies data and insert
            // the rendered HTML under the "movieList" element
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

function load_mfile(mfileid){
         $.ajax({
           type: "GET",
           url: "/mfileapi/thumb/"+mfileid+"/",
           success: function(msg){
                $("#mfilelist").prepend(msg);
                $("#image-"+mfileid).show('bounce')
           },
           error: function(msg){
                showError( "Failure to get mfile thumb " );
           }
         });
}

function loadJobs(serviceid){
     $.ajax({
       type: "GET",
       url: '/serviceapi/getjobs/'+serviceid+"/",
       success: function(msg){
            for (i in msg){
                create_job_holder(msg[i])
                if(!msg[i].ready){
                    check_job(msg[i].job,serviceid)
                }
            }
       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function load_jobs_mfile(mfileid){
     $.ajax({
       type: "GET",
       url: '/jobapi/getjobs/'+mfileid+"/",
       success: function(msg){

            for (i in msg){
                create_job_holder(msg[i])

                var jobid = msg[i].job.id

                joboutputs = msg[i].job.joboutput_set

                var jobpaginator = $("#jobpreviewpaginator-"+jobid)

                function handlePaginationClick(new_page_index, jobpaginator) {
                    // This selects elements from a content array
                    start = new_page_index*this.items_per_page
                    end   = (new_page_index+1)*this.items_per_page
                    if(end>joboutputs.length){
                        end=joboutputs.length;
                    }
                    for(var j=start;j<end;j++) {
                        var im = $("<a target='_blank' href='/jobapi/contents/"+joboutputs[j].id+"/' ><img src='"+joboutputs[j].thumburl+"' /></a>")
                        jobpaginator.append(im)
                    }
                    return false;
                }

                // First Parameter: number of items
                // Second Parameter: options object
                jobpaginator.pagination(joboutputs.length, {
                        items_per_page:4,
                        callback:handlePaginationClick
                });

                if(!msg[i].ready){
                    check_job(msg[i].job,mfileid)
                }
   
            }

       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function create_job_holder(task){
    job = task.job
    var jobholder = $("#job-"+job.id)
    if (jobholder.length == 0){

        $( "#jobTemplate" ).tmpl( task ) .appendTo( "#jobs" );

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
        $('#jobheader-'+id).click(function() {          $('#jobpreviewpaginator-'+id).toggle('blind');      });
        $('#jobicon-'+id).click(function() {            $('#jobpreviewpaginator-'+id).toggle('blind')        });
        $('#jobinfo-'+id).click(function() {            $('#jobpreviewpaginator-'+id).toggle('blind')        });
        $('#jobprogressbar-'+id).click(function() {            $('#jobpreviewpaginator-'+id).toggle('blind')        });

    }
}

function mfile_render(mfileid){
    mfile_render(mfileid,0,10)
}
function mfile_render(mfileid,start,end){
     $.ajax({
       type: "POST",
       url: '/jobapi/render/'+mfileid+"/"+start+"/"+end+"/",
       success: function(msg){
            create_job_holder(msg)
            check_job(msg.job,mfileid)
       },
       error: function(msg){
            showError("Render",objectToString(msg))
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

function check_job(job,mfileid){
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
            icon.addClass('taskrunning')
        }else{
            icon.addClass('ui-icon-check')
            icon.removeClass('taskrunning')
        }

        info.html("<b>"+msg.completed_count+"</b> frames of <b>"+msg.total+"</b> complete : "+Math.round(percent)+"%" )

        progressbar.progressbar({
                value: percent
        });

        if(msg.waiting){
            window.setTimeout(function(){ check_job(job,mfileid) },3000)
        }else{
            if(msg.failed){
                $('#job-'+job.id).addClass('ui-state-error')
            }else{
                load_render_preview_output(job.id)
                $('#jobpreview-'+job.id).show('blind')
            }
        }

       },
       error: function(msg){
            showError("Render",objectToString(msg))
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


function mfile_file_corrupt(mfileid){
     $.ajax({
       type: "PUT",
       url: '/mfileapi/corrupt/'+mfileid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
 }

function mfile_backup_corrupt(mfileid){
     $.ajax({
       type: "PUT",
       url: '/mfileapi/corruptbackup/'+mfileid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
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