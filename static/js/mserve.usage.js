
$(document).ready(function() {
    $(".relatize").relatizeDate();
});

var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var previousPoint = null;
var date = new Date();

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
    lines:{show:true},
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

                        var plotoptions = {
                            xaxis:{mode:'time'},
                            points:{show:true},
                            lines:{show:true},
                            grid:{hoverable:true},
                            legend: { show :true, position: "nw" }
                        };

                        var plot = $.plot($this, plotdata, plotoptions );


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
    stats: function(types, serviceid){

        var defaults = {};
        var options = $.extend(defaults, options);
        url = "/stats/?"+types.join('&')
        if(serviceid){
            url = "/stats/"+serviceid+"/?"+types.join('&')
        }
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
                        $holder = $("#graphTemplate").tmpl( plot )
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
                                        showTooltip(item.pageX, item.pageY, 'Value at ' + date + ' is ' + item.datapoint[1]);
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
