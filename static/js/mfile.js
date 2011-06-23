
function load_mfile_text(mfileid){
    $.ajax({
        type: "GET",
        url: "/mfiles/"+mfileid+"/file/",
        success: function(msg){
           $("#mfiletext-"+mfileid).text(msg);
        }
    });
}
