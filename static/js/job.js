function loadJobs(url){
     $.ajax({
       type: "GET",
       url: url,
       success: function(msg){
            create_jobs_paginator(msg)
       }
     });
}

function create_jobs_paginator(jobs){

        var jobspaginatorheader = $("#jobspaginatorheader")
        var jobpaginator = $("#jobspaginator")
        var jobsperpage = 10
        function onChangePage(new_page_index) {
            jobpaginator.empty()
            // This selects elements from a content array
            start = (new_page_index-1)*jobsperpage
            end   = (new_page_index)*jobsperpage

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
        sp = jobspaginatorheader.smartpaginator({ totalrecords: jobs.length, recordsperpage: jobsperpage, initval:1 , next: 'Next',
            prev: 'Prev', first: 'First', last: 'Last', theme: 'smartpagewhite', onchange: onChangePage
        });
        onChangePage(1)
}

function create_job_output_paginator(job){

        var tasks = job.tasks
        var jobid = job.id
        var joboutputs = job.joboutput_set
        var jobresults = tasks.result
        
        var jobspaginatorheader = $("#jobpreviewpaginatorheader-"+jobid)
        var jobpaginator = $("#jobpreviewpaginator-"+jobid)
        var joboutputsperpage = 4
        function onChangePage(new_page_index) {
            jobpaginator.empty()
            // This selects elements from a content array
            start = (new_page_index-1)*joboutputsperpage
            end   = (new_page_index)*joboutputsperpage

            if(end>joboutputs.length){
                end=joboutputs.length;
            }

            $(joboutputs.slice(start,end)).each(function(index,joboutput){
                if(joboutput.file != ""){
                    $( "#jobOutputTemplate" ).tmpl( joboutput ) .appendTo( jobpaginator );
                    $("#joboutput-"+joboutput.id+"-createmfile-button").button().click(function(){create_mfile_from_joboutput(joboutput)})
                }else{
                    $('<div></div>').html("<span class='red'>Output '"+joboutput.name+"' Empty&nbsp;</span>").appendTo( jobpaginator );
                }
            })

            return false;
        }
        jobspaginatorheader.smartpaginator({ totalrecords: joboutputs.length, recordsperpage: joboutputsperpage, initval:1 , next: 'Next',
            prev: 'Prev', first: 'First', last: 'Last', theme: 'smartpagewhite', onchange: onChangePage
        });
        onChangePage(1)
}

function create_mfile_from_joboutput(joboutput){
     name = $("#joboutput-"+joboutput.id+"-createmfile-name").val()
     $.ajax({
       type: "POST",
       url: joboutput.mfile_url,
       data: "name="+name,
       success: function(mfile){
           $("#mserve").mserve('addMFile',mfile)
       },
       error: function(msg){
           showError("Error creating new file","Could not create a new file from this job output")
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
        $('#jobpreviewpaginatorheader-'+id).hide()
        $('#jobpreviewpaginator-'+id).hide()
        $("#joboutputs-"+id).hide()
        $('#jobheader-'+id).click(function() {      toggle_job(job);     });
        $('#jobicon-'+id).click(function() {        toggle_job(job);     });
        $('#jobinfo-'+id).click(function() {        toggle_job(job);     });
        $('#jobprogressbar-'+id).click(function() { toggle_job(job);     });

        $("#jobdeletebutton-"+id ).button({ icons: { primary: "ui-icon-circle-close"}, text: false });
        $("#jobdeletebutton-"+id ).click(function() { delete_job(job) });

        update_job_outputs(job)

        if(job.tasks.failed){
            $('#jobinfo-'+job.id).addClass('ui-state-error ui-corner-all')
        }
    }
}

function update_job_outputs(job){
    $("#joboutputs-"+job.id).empty()
    $("#jobTaskResultTemplate" ).tmpl(job.tasks.result).appendTo("#joboutputs-"+job.id)
    $("#jobpreviewpaginator-"+job.id ).empty()
    $(job.joboutput_set).each(function(index, joboutput){
        if(joboutput.file != ""){
            $( "#jobOutputTemplate" ).tmpl( joboutput ) .appendTo( "#jobpreviewpaginator-"+job.id );
            $("#joboutput-"+joboutput.id+"-createmfile-button").button().click(function(){create_mfile_from_joboutput(joboutput)})
        }else{
            $('<div></div>').html("<span class='red'>Output '"+joboutput.name+"' Empty&nbsp;</span>").appendTo( "#jobpreviewpaginator-"+job.id  );
        }
    })
}

function get_joboutput_thumb(job){
    function f(depth) {
       if(depth>3){ return }
       $.ajax({
           type: "GET",
           url: job.url,
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
    $('#jobpreviewpaginatorheader-'+job.id).show('blind');
    $('#jobpreviewpaginator-'+job.id).show('blind');
    get_joboutput_thumb(job)

}

function toggle_job(job){
    $('#joboutputs-'+job.id).toggle('slide');
    $('#jobpreviewpaginatorheader-'+job.id).show('blind');
    $('#jobpreviewpaginator-'+job.id).toggle('blind');
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
       url: job.url,
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
function delete_job(job){
    $( '#dialog-job-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete Job?": function() {
                              $.ajax({
                               type: "DELETE",
                               url: job.url,
                               success: function(msg){
                                    $('#job-'+job.id).hide('blind')
                                    $('#jobheader-'+job.id).hide()
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