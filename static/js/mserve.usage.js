
$(document).ready(function() {
    $(".relatize").relatizeDate();
});

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
                   url: '/stats/?traffic',

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
                        var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                        var previousPoint = null;
                        var date = new Date();

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
    stats: function(){

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');
            $.ajax({
               type: "GET",
               url: "/stats/?jobs&jobtype",
               success: function(msg){
                    $(msg).each( function(index, plot){
                        $holder = $("#graphTemplate").tmpl( plot.options )
                        $this.append($holder)
                        $graph = $holder.find(".graph")
                        if(plot.options.type=="pie"){
                            $.plot($graph, plot.data,
                                {
                                    fillColor: "#FF0000",
                                    series: {
                                        pie: {
                                            show: true,
                                            radius: 1,
                                            label: {
                                                show: true,
                                                radius: 2/3,
                                                formatter: function(label, series){
                                                    return '<div class="ui-widget-content ui-corner-all" style="font-size:8pt;text-align:center;padding:2px;color:black;">'+label+'<br/>'+Math.round(series.percent)+'%</div>';
                                                },
                                                threshold: 0.01,
                                                background: { opacity: 0.8, }
                                            },
                                            combine: {
                                                threshold: 0.01
                                            }
                                        },
                                    legend: {
                                        show: false
                                    }
                                }
                           });
                        }else{
                            $.plot($graph, [plot.data] , plot.options );
                        }
                    })
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
