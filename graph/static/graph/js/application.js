$(function(){
	var app = {};
	
	app.Annotation = Backbone.Model.extend({
		url: "/graph/find"
	});

	app.Graph = Backbone.Model.extend({
		url: "/graph/plot",
		defaults: {
			title: '',
			colors: ['rgb(237,194,64)']
		},
		/*initialize: function(){
			this.on("change:title", function(model){
				console.log(model.get("title"))
				alert("title changed to" + model.get("title") );
			});
		},*/
		plotGraph: function(){
			var x = this.get('xLabel');
			var y = this.get('yLabel');
			var xmax = this.get('xmax');
			var ydata = this.get('ydata');
			var useCanvas = this.get('useCanvas');
			console.log("useCanvas",useCanvas)
			var axisLabelPadding = this.get('axisLabelPadding');
			var options = {
				axisLabels: {
				            show: true
				        },
				xaxes: [{
		            axisLabel: x,
					axisLabelUseCanvas: useCanvas,
					axisLabelPadding: axisLabelPadding
				        }],
		        yaxes: [{
		            position: 'left',
		            axisLabel: y,
					axisLabelUseCanvas: useCanvas,
					axisLabelPadding: axisLabelPadding
		        }],
				series: {
					lines: {
						show: true
					},
					points: {
						show: true
					}
				},
				colors: this.get('colors'),
				grid: {
					hoverable: true,
					clickable: true
				},
				xaxis: {
					tickDecimals: 0,
					tickSize: xmax / 10
		        }
			};

			$(".graph-container").show();
			$("#graph_toolbar").show();
			var plot = $.plot("#graph_placeholder", ydata, options);
			var canvas = plot.getCanvas();
			var c = canvas.getContext("2d");
			var cx = canvas.width / 2;
			var cy = canvas.height;
			var title = this.get('title');
			var xlabel = x;
			c.font = "bold 16px sans-serif";
			c.textAlign = 'center';
		    c.fillText(title,cx,30);
		}
	});
		
	app.AnnotationView = Backbone.View.extend({
		
		el: '#annotation_form',
		
	    events: {
	        "submit": "submit",
	    },

	    initialize: function () {
	        console.log("initialize");
			console.log(this.model);
	    },

	    submit: function (e) {
	        e.preventDefault();
	        console.log("submit");
			console.log(this.model);
			var header = $('#id_header').val();
			var sheet = $('#id_sheet').val();
			var annotation = $('#id_annotation').val();
			var model = this.model;
			$.ajax({
				traditional: true,
				type: "POST",
				url: this.$el.attr('action'),
				data : {'annotation' : annotation, 'header': header, 'sheet': sheet},
				success: function(results) {
					console.log(results)
					var xoptions = $("#id_x");
					var yoptions = $("#id_y");
					var columns = results.columns;
					$("#id_x").empty();
					$("#id_y").empty();
					for (i = 0; i < columns.length; i++) {
						xoptions.append($("<option />").val(columns[i][0]).text(columns[i][1]));
						yoptions.append($("<option />").val(columns[i][0]).text(columns[i][1]));
					}
					$("#id_x").trigger("chosen:updated");
					$('#id_x').val('').trigger('liszt:updated');
					$("#id_y").trigger("chosen:updated");
					$('#id_y').val('').trigger('liszt:updated');
					$("#graph_setup").show();
					model.save({'title': results.selected, 'xoptions': columns})
					console.log(model);
			  },
	          statusCode: {
	              400: function() {
	                  alert("Too many rows in annotation");
				  }
	          }
			});
	    }
	});

	app.GraphPlotView = Backbone.View.extend({
		
		el: '#plotform',
		
	    events: {
	        "submit": "submit",
	    },

	    initialize: function () {
	        console.log("initialize");
			console.log(this.model);
	    },

	    submit: function (e) {
			e.preventDefault();
			console.log(this.model)
			var model = this.model;
			var x = $('#id_x').val();
			var y = $('#id_y').val();
			var seriesColors = $('#series_select');
			var annId = "{{ request.session.annotation_id }}";
			console.log("the form has beeen submitted");
			console.log("x:",x,"y:",y)
			$.ajax({
				traditional: true,
				type: "POST",
				url: "/graph/plot/",
				data : {'x' : x, 'y': y},
				success: function(plotresults) {
					console.log(plotresults)
					console.log(plotresults.message)

					function generateData(fseriesdata) {
					    series = [];
					    for (fi = 0; fi < fseriesdata.length; fi++) {
							seriesColors.append($("<option />").val('Series'+String(fi)).text('Series'+String(fi)));
							
					        var fd = fseriesdata[fi];
				            series.push({
								label: 'Series'+String(fi),
				                data: fd
				            });
					    }
					    return series;
					};
					
					$('#id_annotation').val('').trigger('liszt:updated');
					var ydata = generateData(plotresults.graph_data);
					var xmax = plotresults.xmax;
					var useCanvas = false;
					var axisLabelPadding = 5;
					var title = plotresults.title;
					//model.set({'title': title});
					model.set({'title': title, 'xLabel': x, 'yLabel': y, 'useCanvas': useCanvas,
					'axisLabelPadding': axisLabelPadding, 'ydata': ydata, 'xmax': xmax});
					model.plotGraph();
			  },
			  error: function(error) {
			    console.log(error)
			  }
			});
	    }
	});
	
	app.TooltipView = Backbone.View.extend({
		id: "tooltip",
  	  	template: _.template("<%= label %>"),

	    initialize: function () {
			this.$el.css({
						 position: "absolute",
						 display: "none",
						 border: "1px solid #fdd",
						 padding: "2px",
						 "background-color": "#fee",
						 opacity: 0.80,
						 font: "18px/1.5em proxima-nova, Helvetica, Arial, sans-serif",
						 color: "#000000"}).appendTo("body");
	        this.render();
	    },
		
        render: function(){
          this.$el.html(this.template({'label':''}));
        }
	});
	
	app.TooltipCheckView = Backbone.View.extend({
		el: '#enableTooltip',
		
  	  	template: _.template("<%= label %>"),
		
	    events: {
	        'change [type="checkbox"]': 'enableToolTip',
	    },

	    initialize: function () {
	        console.log("initialize");
			console.log(this.model);
			this.renderTooltip($('#graph_placeholder'));
	    },
		
		renderTooltip: function(ph){
			var template = this.template,
				el = this.$el,
				tooltip = $("#tooltip");
				
			ph.bind("plothover", function (event, pos, item) {
				if (el.is(':checked')) {
					if (item) {
						var tipx = item.datapoint[0].toFixed(2),
							tipy = item.datapoint[1].toFixed(2);

						tooltip.html(template({'label':item.series.label + ", (x: " + tipx + " , y: " + tipy + ")"}))
							.css({top: item.pageY+5, left: item.pageX+5}).fadeIn(200);
					} else {
						tooltip.hide();
					}
				}
				
			});
		},
		
		enableToolTip: function(e) {
			var template = this.template,
				tooltip = $("#tooltip"),
				placeholder = $('#graph_placeholder');
			if (this.$el.is(':checked')) {
				console.log("checked");
				this.renderTooltip(placeholder);
			}
			else {
				console.log("unchecked");
				placeholder.off('mouseenter mouseleave');
				tooltip.hide();
			}
		}
	});
	
	app.omeroExportView = Backbone.View.extend({
		el: '#graph_toolbar',
		
		events: {
			"click #graph_save": "omeroExport"
		},
		
		omeroExport: function(e) {
			var model = this.model;
			model.set({'useCanvas': true });
			model.plotGraph();
			$("#graph_toolbar").hide();
			html2canvas($('#graph_container'), {
			    onrendered: function (fcanvas) {
			        img = fcanvas.toDataURL("image/png");
					$.ajax({
						traditional: true,
						type: "POST",
						url: "/graph/save",
						data : {'img' : img },
						success: function(saveresults) {
							console.log(saveresults)
							$("#graph_toolbar").show();
							model.set({'useCanvas': false });
							model.plotGraph();
							alert(saveresults.message);
					  },
			          statusCode: {
			              400: function() {
			                  alert(saveresults.message);
						  }
			          }
				  });
			    }
			});
		}
	});
	
	app.colorPickView = Backbone.View.extend({
		el: '#color_picker',
		initialize: function() {
			var model = this.model;
			this.$el.colorPicker();
		},
		events: {
			"click #color_picker": "colorPicker"
		},
		
		colorPicker: function(e) {
			var model = this.model;
			this.$el.spectrum({
				change: function(color) {
					console.log(color.toHexString())
					var seriesColor = color.toHexString();
					var seriesIndex = $('#series_selec')[0].selectedIndex;
					colors = model.get('colors');
					colors[seriesIndex] = seriesColor;
					model.set({'colors': colors });
					model.plotGraph();
				}
			});
		}
	});
		
	app.Ann = new app.Annotation();
	app.Graph = new app.Graph();

	app.AnnView = new app.AnnotationView({ model: app.Ann });
	app.GraphPlotView = new app.GraphPlotView({ model: app.Graph });
	app.TooltipView = new app.TooltipView();
	app.TooltipCheckView = new app.TooltipCheckView();
	app.omeroExportView = new app.omeroExportView({ model: app.Graph });
	app.colorPickView = new app.colorPickView({ model: app.Graph });
});