
$(document).ready(function() {
    $(".relatize").relatizeDate();
});

var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var previousPoint = null;
var date = new Date();

FLOT_TRAFFIC_OPTIONS = {
    xaxis:{mode:'time'},
    points:{show:true},
    lines:{show:true},
    grid:{hoverable:true},
    legend: { show :true, position: "nw" }
}
FLOT_OPTIONS = {
    legend: {
        show: false
    }
}
FLOT_TIME_OPTIONS = {
    "type" : "time",
    "size" : "wide",
    "label" : "Last 24 Hours",
    xaxis:{mode:'time'},
    points:{show:true},
    lines:{show:true,fill:true},
    grid:{hoverable:true},
    legend: { show :true, position: "nw" }
}
FLOT_PIE_OPTIONS = {
    series: {
        pie: {
            show: true,
            radius: 1,
            label: {
                show: true,
                radius: 2/3,
                formatter: function(label, series){
                    return $("#graphLabelTemplate").tmpl( { "label" :  label,  "series" : series } ).html();
                },
                threshold: 0.1,
                background: {
                    opacity: 0.5,
                    color: '#FFF'
                }
            }
        }
    },
    legend: {
        show: true
    }
}

function showTooltip(x, y, contents) {
    $("#tooltip").remove();

    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #ccc',
        padding: '5px',
        'background-color': '#7CA0C7',
        'color': '#fff',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

(function( $ ){

  var methods = {
    init : function( options ) {
            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this), data = $this.data('mserveusage')

                if ( ! data ) {
                    $(this).data('mserve', {
                       target : $this,
                       table : $table
                    });
                }
            });
    },
    traffic: function(placeholder){

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {

            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');
                $.ajax({
                   type: "GET",
                   url: '/traffic/',

                   success: function(msg){

                       var plotdata = []
                       for(i in msg){
                            plotdata.push( {
                                label :  msg[i]["label"] ,
                                data : msg[i]["data"],
                                lines : { show : true , fill : true},
                                points : { show : true}
                                }
                            )
                        }

                        var plot = $.plot($this, plotdata, FLOT_TRAFFIC_OPTIONS );

                        $this.bind("plothover", function (event, pos, item) {
                            if (item) {
                                if (previousPoint != item.datapoint) {
                                    previousPoint = item.datapoint;

                                    date.setTime(item.datapoint[0]).toString;
                                    showTooltip(item.pageX, item.pageY, item.series.label + ' on ' + monthNames[date.getMonth()] + ' ' + date.getDate() + ' is ' + item.datapoint[1]);
                                }
                            } else {
                                $("#tooltip").remove();
                                previousPoint = null;
                            }
                        });
                   },
                   error: function(msg){
                     $this.html("Error loading chart")
                   }
                 })
        });
    },
    stats: function(types, statsurl){

        var defaults = {};
        var options = $.extend(defaults, options);
        url = statsurl+"?"+types.join('&')
        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');
            $.ajax({
               type: "GET",
               url: url,
               success: function(msg){
                    $this.empty()
                    $(msg).each( function(index, plot){
                        template_name = "#graphTemplate"
                        if(plot.size){
                            template_name = "#"+plot.size+"_graphTemplate"
                        }
                        $holder = $(template_name).tmpl( plot )
                        $this.append($holder)
                        $graph = $holder.find(".graph")
                        if(plot.type == "pie"){
                            $.plot($graph, plot.data , FLOT_PIE_OPTIONS );
                        }else if (plot.type == "time"){
                            $.plot($graph, plot.data , FLOT_TIME_OPTIONS );
                            $graph.bind("plothover", function (event, pos, item) {
                                if (item) {
                                    if (previousPoint != item.datapoint) {
                                        previousPoint = item.datapoint;
                                        date.setTime(item.datapoint[0]).toString;
                                        label = "Value"
                                        if(item.series.label){
                                            label = item.series.label
                                        }
                                        showTooltip(item.pageX, item.pageY, label+' at ' + date + ' is ' + item.datapoint[1]);
                                    }
                                } else {
                                    $("#tooltip").remove();
                                    previousPoint = null;
                                }
                            });
                        }else{
                            $.plot($graph, plot.data , FLOT_OPTIONS );
                        }
                    });
               }
            });
        });
    },
    usagesummary: function(usagesummaryurl){
        var defaults = {};
        var options = $.extend(defaults, options);
        url = usagesummaryurl
        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');
            $.ajax({
               type: "GET",
               url: url,
               success: function(usagesummarydata){
                   $this.empty()
                   $holderid = "usagetbodyholder"
                   $holder = $( "#usageSummaryTableTemplate" ).tmpl( {"usageholderid" : $holderid  } ).appendTo( $this );
                   $( "#usageSummaryTemplate" ).tmpl( usagesummarydata.usages ).appendTo( $holder.find("#"+$holderid) );
                   $(".togglevarbutton").button()
               }
            });
        });
    },
  };

  $.fn.mserveusage = function( method ) {

    // Method calling logic
    if ( methods[method] ) {
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.tooltip' );
    }

  };

})( jQuery );
