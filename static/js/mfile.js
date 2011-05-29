

function mfile_job_ajax(data){
     $.ajax({
       type: "POST",
       data: data,
       url: "/jobapi/",
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

function mfile_task(mfileid){
  $.ajax({
   type: "GET",
   url: "/tasks/",
   success: function(msg){
                var tasks = "<select id='selecttask' >"
                for(i in msg['regular']){
                    tasks += "<option>"+msg['regular'][i]+"</option>"
                }
                   tasks += "</select>"
                $("<div style='width:600px' title='Choose Task' >"+tasks+"</div>").dialog({
                    width: 500,
                    buttons: [
                    {
                        text: "Create",
                        click: function() {
                            var selected= $( "#selecttask" ).val()
                            mfile_job_ajax(mfileid,selected)
                            $(this).dialog("close");
                        }
                    }
                    ]
                });
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 }); 
}


function load_mfile_text(mfileid){
 $.ajax({
   type: "GET",
   url: "/mfiles/"+mfileid+"/file/",
   success: function(msg){
       $("#mfiletext-"+mfileid).text(msg);
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });

}
