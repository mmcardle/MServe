

function mfile_task_ajax(mfileid, jobtype){
     $.ajax({
       type: "POST",
       data: "jobtype="+jobtype+"&mfileid="+mfileid,
       url: "/jobapi/",
       success: function(msg){
                   showMessage("debug",msg)
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
                $("<div style='width:600px'>"+tasks+"</div>").dialog({ 
                    width: 500,
                    buttons: [
                    {
                        text: "Cancel",
                        click: function() { $(this).dialog("close"); }
                    },
                    {
                        text: "Create",
                        click: function() {
                            var selected= $( "#selecttask" ).val()
                            mfile_task_ajax(mfileid,selected)
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
   url: "/mfileapi/get/"+mfileid+"/",
   success: function(msg){
                $("#mfiletext-"+mfileid).append("<pre>"+msg+"</pre>");
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });

}
