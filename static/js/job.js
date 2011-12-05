function loadJobs(serviceid){
     $.ajax({
       type: "GET",
       url: '/services/'+serviceid+"/jobs/",
       success: function(msg){
            create_jobs_paginator(msg)
       }
     });
}

function create_jobs_paginator(jobs){

        var jobpaginator = $("#jobspaginator")

        function handlePaginationClick(new_page_index, jobpaginator) {
            // This selects elements from a content array
            start = new_page_index*this.items_per_page
            end   = (new_page_index+1)*this.items_per_page

            if(end>jobs.length){
                end=jobs.length;
            }

            $(jobs.slice(start,end)).each(function(index,job){

                create_job_holder(job,jobpaginator)
                if(!job.tasks.ready){
                    check_job(job,serviceid)
                }
            });

            return false;
        }

        // First Parameter: number of items
        // Second Parameter: options object
        jobpaginator.pagination(jobs.length, {
                items_per_page:10,
                callback:handlePaginationClick
        });
}

function create_job_output_paginator(job){

        var tasks = job.tasks
        var jobid = job.id
        var joboutputs = job.joboutput_set
        var jobresults = tasks.result
        
        var jobpaginator = $("#jobpreviewpaginator-"+jobid)

        function handlePaginationClick(new_page_index, jobpaginator) {
            // This selects elements from a content array
            start = new_page_index*this.items_per_page
            end   = (new_page_index+1)*this.items_per_page

            if(end>joboutputs.length){
                end=joboutputs.length;
            }

            $(joboutputs.slice(start,end)).each(function(index,joboutput){
                if(joboutput.file != ""){
                    $( "#jobOutputTemplate" ).tmpl( joboutput ) .appendTo( jobpaginator );
                }else{
                    $('<div></div>').html("<span class='red'>Output '"+joboutput.name+"' Empty&nbsp;</span>").appendTo( jobpaginator );
                }
            })

            for(var j=start;j<end;j++) {
                if(joboutputs[j].file != "" && joboutputs[j].mimetype && joboutputs[j].mimetype.startsWith('text')){
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
   url: "/joboutputs/"+id+"/contents/",
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
   url: "/mfiles/"+mfileid+"/jobs/",
   success: function(msg){
      var thumbs = []

      $(msg).each(function(index,job){
            tasks = job.tasks

            if(job.joboutput_set.length > 0){
                thumbs.push(job.joboutput_set[0].thumburl)
            }
        });

      for(i in msg){
            
      }
      $("#previewcontent").append("<div style='clear:both' ></div>")
      for(i in thumbs){
        $("#previewcontent").append("<img src='"+thumbs[i]+"' />")
      }
   }
 });
}

function load_jobs_mfile(mfileid){
     $.ajax({
       type: "GET",
       url: '/mfiles/'+mfileid+"/jobs/",
       success: function(msg){
            if(msg.length > 0){
                $("#jobspaginator").empty()
            }

            $(msg).each(function(index,job){
                create_job_holder(job,$("#jobspaginator"))
                if(!job.tasks.ready){
                    check_job(job,mfileid)
                }
            });
       }
     });
}

function create_job_holder(job, paginator){
    var tasks = job.tasks
    var jobholder = $("#job-"+job.id)
    if (jobholder.length == 0){

        $( "#jobTemplate" ).tmpl( job ) .prependTo( paginator );

        var allDone = true

        var jobs = $("#job-"+job.id)
        var percent = (job.tasks.completed_count/job.tasks.total)*100
        var info = $( "#jobinfo-"+job.id )
        var icon = $( "#jobicon-"+job.id )
        var progressbar = $( "#jobprogressbar-"+job.id )

        if(job.tasks.waiting){
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
        $('#jobheader-'+id).click(function() {      toggle_job(job);     });
        $('#jobicon-'+id).click(function() {        toggle_job(job);     });
        $('#jobinfo-'+id).click(function() {        toggle_job(job);     });
        $('#jobprogressbar-'+id).click(function() { toggle_job(job);     });

        $("#jobdeletebutton-"+id ).button({ icons: { primary: "ui-icon-circle-close"}, text: false });
        $("#jobdeletebutton-"+id ).click(function() {           delete_job(id) });

        update_job_outputs(job)

        if(job.tasks.failed){
            $('#jobinfo-'+job.id).addClass('ui-state-error ui-corner-all')
        }
    }
}

function update_job_outputs(job){
    $("#joboutputs-"+job.id).empty()
    $( "#jobTaskResultTemplate" ).tmpl(job.tasks.result).appendTo("#joboutputs-"+job.id)
}

function get_joboutput_thumb(job){
    function f(depth) {
       if(depth>3){ return }
       $.ajax({
           type: "GET",
           url: "/jobs/"+job.id+"/",
           success: function(newjob){
            $(newjob.joboutput_set).each(function(index, joboutput){
                if(joboutput.thumb != ""){
                    $("#joboutput-"+joboutput.id).attr("src",joboutput.thumburl);
                }else{
                    window.setTimeout(f, 3000, depth+1);
                }
            })
           }
       });
    }
    window.setTimeout(f, 3000, 0);
}

function show_job(job){
    $('#joboutputs-'+job.id).show('slide');
    $('#jobpreviewpaginator-'+job.id).show('blind');
    get_joboutput_thumb(job)

}

function toggle_job(job){
    $('#joboutputs-'+job.id).toggle('slide');
    $('#jobpreviewpaginator-'+job.id).toggle('blind');
}

function create_access_job(mfileid){
    var data = { name: 'access' };
    var result = decodeURIComponent($.param(data));
     $.ajax({
       type: "POST",
       data: result,
       url: "/mfiles/"+mfileid+"/workflows/",
       success: function(msg){
                create_job_holder(msg,$("#jobspaginator"))
                if(!msg.ready){
                    check_job(msg)
                }
       },
       error: function(msg){
            showError("Error starting job","Could not start an access job")
       }
     });
}

function mfile_job_ajax(mfileid,data){
     $.ajax({
       type: "POST",
       data: data,
       url: "/mfiles/"+mfileid+"/jobs/",
       success: function(msg){
                create_job_holder(msg,$("#jobspaginator"))
                if(!msg.ready){
                    check_job(msg)
                }
       },
       error: function(msg){
            json_response = eval('(' + msg.responseText + ')');
            if(json_response.error){
                showError("Error creating Job",json_response.error)
            }else{
                showError("Error creating Job",msg.responseText)
            }
       },

     });
}

function check_job(job){
    var tasks = job.tasks
     $.ajax({
       type: "GET",
       url: '/jobs/'+job.id+"/",
       success: function(msg){
        var allDone = true

        var jobs = $("#job-"+job.id)
        var percent = (msg.tasks.completed_count/msg.tasks.total)*100
        var info = $( "#jobinfo-"+job.id )
        var icon = $( "#jobicon-"+job.id )
        var progressbar = $( "#jobprogressbar-"+job.id )

        if(msg.tasks.waiting){
            icon.removeClass('ui-icon ui-icon-circle-check')
            icon.addClass('taskrunning')
        }else{
            icon.addClass('ui-icon ui-icon-circle-check')
            icon.removeClass('taskrunning')
        }

        info.html("<b>"+msg.tasks.completed_count+"</b> tasks of <b>"+msg.tasks.total+"</b> complete : "+Math.round(percent)+"%" )

        progressbar.progressbar({
                value: percent
        });

        if(msg.tasks.waiting){
            window.setTimeout(function(){ check_job(msg) },5000)
        }else{
            if(msg.tasks.failed){
                $('#jobinfo-'+job.id).addClass('ui-state-error')
            }else{
                create_job_holder(msg,$("#jobspaginator"))
                //create_job_output_paginator(msg)
                update_job_outputs(msg)
                show_job(msg)
            }
        }

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
                               url: '/jobs/'+jobid+"/",
                               success: function(msg){
                                    $('#job-'+jobid).hide('blind')
                                    $('#jobheader-'+jobid).hide()
                               },
                               error: function(msg){
                                    showError("Job Deleted Error","Could not delete the job")
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