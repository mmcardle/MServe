
function create_container(){
 $.ajax({
   type: "POST",
   data: "name=Container",
   url: '/container/',
   success: function(msg){

            loadContainers()
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
}

function loadContainers(){
    $.ajax({
       type: "GET",
       url: "/container/",
       success: function(msg){
            containers = msg;

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

                $( "#containerTemplate" ).tmpl( containers.slice(start,end) ) .appendTo( "#containerpaginator" );
                for(var i=start;i<end;i++) {
                    //var c = $("<div>"+containers[i].name+"  <a href='/browse/"+containers[i].id+"/'>"+containers[i].id+"</a>&nbsp;<em>"+containers[i].dataservice_set.length+" services</em></div>")
                    //$('#containerpaginator').append(c)
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