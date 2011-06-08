function loadJobs(serviceid){
     $.ajax({
       type: "GET",
       url: '/services/'+serviceid+"/jobs/",
       success: function(msg){
        $(msg).each(function(index,job){
            create_job_holder(job)
                if(!job.tasks.ready){
                    check_job(job,serviceid)
                }
        });
       },
       error: function(msg){
            showError("Error Loading Jobs",objectToString(msg))
       }
     });
}

function create_job_paginator(job){

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
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });

}

function load_jobs_mfile(mfileid){
     $.ajax({
       type: "GET",
       url: '/mfiles/'+mfileid+"/jobs/",
       success: function(msg){
            if(msg.length > 0){
                $("#jobs").empty()
            }

            $(msg).each(function(index,job){
                create_job_holder(job)
                if(!job.tasks.ready){
                    check_job(job,mfileid)
                }

            });

       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function create_job_holder(job){
    var tasks = job.tasks
    var jobholder = $("#job-"+job.id)
    if (jobholder.length == 0){

        $( "#jobTemplate" ).tmpl( job ) .prependTo( "#jobs" );

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
        $('#jobheader-'+id).click(function() {          create_job_paginator(job);show_job(job);     });
        $('#jobicon-'+id).click(function() {            create_job_paginator(job);show_job(job);     });
        $('#jobinfo-'+id).click(function() {            create_job_paginator(job);show_job(job);     });
        $('#jobprogressbar-'+id).click(function() {     create_job_paginator(job);show_job(job);     });

        $("#jobdeletebutton-"+id ).button({ icons: { primary: "ui-icon-circle-close"}, text: false });
        $("#jobdeletebutton-"+id ).click(function() {           delete_job(id) });

        update_job_outputs(job)

        if(job.tasks.failed){
            $('#job-'+job.id).addClass('ui-state-error')
        }else{
            //update_job_outputs(task)
            //show_job(task)
        }

    }
}

function update_job_outputs(job){
    id = job.id
    $("#joboutputs-"+id).empty()
    for(i in job.tasks.result){
        var resultdict = job.tasks.result[i]
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

function show_job(job){
    id = job.id
    if(job.joboutput_set.length > 0){
        $('#jobpreviewpaginator-'+id).toggle('blind');
    }
    if(job.tasks.result.length > 0){
        $('#joboutputs-'+id).toggle('slide');
    }
}

function mfile_job_ajax(mfileid,data){
     $.ajax({
       type: "POST",
       data: data,
       url: "/mfiles/"+mfileid+"/jobs/",
       success: function(msg){
                create_job_holder(msg)
                //create_job_paginator(msg)
                if(!msg.ready){
                    check_job(msg)
                }
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
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