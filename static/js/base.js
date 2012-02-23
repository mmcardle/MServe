
Date.prototype.addHours= function(h){
    this.setHours(this.getHours()+h);
    return this;
}
String.prototype.startsWith = function(str){
    return (this.indexOf(str) === 0);
}

String.prototype.endsWith = function(str)
{
    var lastIndex = this.lastIndexOf(str);
    return (lastIndex != -1) && (lastIndex + str.length == this.length);
}

function replacer(key, value) {
    if (key === 'message') {
        
    }else{
        return value;
    }
}

function getLocation( ){
    return window.location.pathname;
}

function getParameterByName( name )
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if( results == null )
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}

function number_format( number, decimals, dec_point, thousands_sep ) {
    // http://kevin.vanzonneveld.net
    // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +     bugfix by: Michael White (http://crestidg.com)
    // +     bugfix by: Benjamin Lupton
    // +     bugfix by: Allan Jensen (http://www.winternet.no)
    // +    revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // *     example 1: number_format(1234.5678, 2, '.', '');
    // *     returns 1: 1234.57

    var n = number, c = isNaN(decimals = Math.abs(decimals)) ? 2 : decimals;
    var d = dec_point == undefined ? "." : dec_point;
    var t = thousands_sep == undefined ? "," : thousands_sep, s = n < 0 ? "-" : "";
    var i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;

    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
}

function scaleNumber( number, decimals, dec_point, thousands_sep ) {
    if (number >= 1073741824) {
         number = number_format(number / 1073741824, decimals, dec_point, thousands_sep) + ' G';
    } else {
            if (number >= 1048576) {
                number = number_format(number / 1048576, decimals, dec_point, thousands_sep) + ' M';
        } else {
                if (number >= 1024) {
                    number = number_format(number / 1024, decimals, dec_point, thousands_sep) + ' K';
                } else {
                    number = number_format(number, decimals, dec_point, thousands_sep) + ' ';
                };
             };
    };
  return number;
}

function formatSize( filesize ) {
    if (filesize >= 1073741824) {
         filesize = number_format(filesize / 1073741824, 2, '.', '') + ' Gb';
    } else {
            if (filesize >= 1048576) {
            filesize = number_format(filesize / 1048576, 2, '.', '') + ' Mb';
    } else {
                    if (filesize >= 1024) {
            filesize = number_format(filesize / 1024, 0) + ' Kb';
            } else {
            filesize = number_format(filesize, 0) + ' bytes';
                    };
            };
    };
  return filesize;
}

function getShort( name , len) {
    if(name.length>len){
        s = name.substr(0,len)+"..."
        return s;
    }else{
        return name;
    }
}

function objectToStringShallow(ob){
    var output = '';
    for (property in ob) {
        //alert(typeof ob[property])
        output += "<b>"+property + '</b>: ' + ob[property]+' <i>'+ (typeof ob[property]) +'</i><br /><br />';
    }
    return output;
}

function objectToString(ob){
    var output = '';
    for (property in ob) {
      if (typeof ob[property] == "object"){
            output += property + ': ' + objectToString(ob[property]) +'';
      }else{
            output += "<b>"+property + '</b>: ' + ob[property]+'<br /><br /><br />';
      }
    }
    return output;
}

function showMessage(title,message){
     var html = "<div id='dialog-message-mfile-delete' title='"+title+"'  ><p ><span class='ui-icon ui-icon-circle-check' style='float:left; margin:0 7px 50px 0;'></span>"+message+"</p></div>"
     $( html ).dialog({
            modal: true,
            buttons: {
                    Ok: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
}

function showError(title,message){
    var html =  "<div id='dialog-message-mfile-delete' title='"+title+"' style='width: 300px;'>"+
            "<div class='ui-state-error ui-corner-all' style='padding: 0 .7em;'><p>"+
            "<span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span>"+
            "<strong>Alert:</strong><div style='height:300px;overflow:auto'>"+message+"</div></p><div></div>"
     $( html ).dialog({
            width: 600,
            height:500,
            modal: true,
            buttons: {
                    Ok: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
}