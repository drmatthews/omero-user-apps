			
	var AnnotationView = Backbone.View.extend({
		
	    constructor: function (options) {
	      this.configure(options || {});
	      // ...
	      Backbone.View.prototype.constructor.apply(this, arguments);
	    },

	    configure: function (options) {
	      if (this.options) {
	        options = _.extend({}, _.result(this, 'options'), options);
	      }
	      this.options = options;
	    },
		
		el: '#annotation_form',
		
	    events: {
	        "submit": "submit",
	    },

	    initialize: function (options) {
			this.graphModel = this.options.graphModel;
			this.graphDialog();
	    },
		
		graphDialog: function() {
			var plotGraph = this.plotGraph;
			var model = this.options.graphModel;
	        $( "#graph_setup_dialog" ).dialog({
	            autoOpen: false,
	            draggable: false,
	            resizable: false,
	            closeOnEscape: true,
	            modal: true,
				width: 320,
				dialogClass: 'reddit',
	            buttons: {
	                "OK": function() { 
						plotGraph(model);
					},
	                "Cancel": function() {
	                    $( this ).dialog( "close" );
	                }
	            },
	            position: { 
	                my: 'center',
	                at: 'center',
	                of: this.$el,
	                collision: "flip",
	                offset: "10 0"
	            }
	        });
		},

	    submit: function (e) {
	        e.preventDefault();
			var header = $('#id_header').val(),
				sheet = $('#id_sheet').val(),
				annotation = $('#id_annotation').val(),
				model = this.model;
			console.log(annotation,header,sheet)
			$.ajax({
				traditional: true,
				type: "POST",
				url: this.$el.attr('action'),
				data : {'annotation' : annotation, 'header': header, 'sheet': sheet},
				success: function(results) {
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
					$("#graph_setup_dialog").dialog("open");
					model.save({'title': results.selected, 'xoptions': columns, 'yoptions': columns })
			  },
	          statusCode: {
	              400: function() {
	                  alert("Too many rows in annotation");
				  }
	          }
			});
	    },

	    plotGraph: function (model) {
			var x = $('#id_x').val(),
				y = $('#id_y').val(),
				title = $('#id_title').val(),
				xLabel = $('#id_xLabel').val(),
				yLabel = $('#id_yLabel').val(),
				seriesColors = $('#series_select'),
				annId = "{{ request.session.annotation_id }}";
			$.ajax({
				traditional: true,
				type: "POST",
				url: "/graph/plot/",
				data : {'x' : x, 'y': y, 'title': title, 'xLabel': xLabel, 'yLabel': yLabel },
				success: function(plotresults) {

					function generateData(fseriesdata) {
					    series = [];
					    for (fi = 0; fi < fseriesdata.length; fi++) {
							seriesColors.append($("<option />").val('Series'+String(fi)).text('Series'+String(fi)));
							
					        var fd = fseriesdata[fi];
				            series.push({
								label: y[fi],
				                data: fd
				            });
					    }
					    return series;
					};
					
					var ydata = generateData(plotresults.graph_data),
						xmax = plotresults.xmax,
						useCanvas = false,
						axisLabelPadding = 5,
						title = plotresults.title,
						xLabel = plotresults.xLabel,
						yLabel = plotresults.yLabel;
					model.set({'title': title, 'xLabel': xLabel, 'yLabel': yLabel, 'useCanvas': useCanvas,
					'axisLabelPadding': axisLabelPadding, 'ydata': ydata, 'xmax': xmax});
					model.plotGraph();
					$('#graph_setup_dialog').dialog('close');
			  },
			  error: function(error) {
			    console.log(error)
			  }
			});
	    }
	});
	
	
	var TooltipView = Backbone.View.extend({
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
	
	var TooltipCheckView = Backbone.View.extend({
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
	
	var omeroExportView = Backbone.View.extend({
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
	
	var graphEditView = Backbone.View.extend({
		el: '#graph_toolbar',
		
		initialize: function() {
			this.editDialog();
		},
		events: {
			"click #graph_edit": "openDialog"
		},
		
		openDialog: function(e) {
			$( "#graph_edit_dialog" ).dialog( "open" );
		},
		
		editDialog: function() {
			var updateGraph = this.updateGraph,
				model = this.model;
	        $( "#graph_edit_dialog" ).dialog({
	            autoOpen: false,
	            draggable: false,
	            resizable: false,
	            closeOnEscape: true,
	            modal: true,
	            width: 320,
	            buttons: {
	                "OK": function() {
						updateGraph(model);	                    
	                },
	                "Cancel": function() {
	                    $( this ).dialog( "close" );
	                }
	            },
	            position: { 
	                my: 'center',
	                at: 'center',
	                of: this.$el,
	                collision: "flip",
	                offset: "10 0"
	            }
	        });
		},
		
		updateGraph: function (model) {
			var title = $('#graph_title').val(),
				xLabel = $('#graph_xLabel').val(),
				yLabel = $('#graph_yLabel').val();
            model.set({'title': title, 'xLabel': xLabel, 'yLabel': yLabel});
			model.plotGraph();
			$('#graph_edit_dialog').dialog('close');
		}
	});
	
	var GraphPlotView = Backbone.View.extend({
			
		//el: '#plotform',
		el: '#graph_container',
	    /*events: {
	        "submit": "submit",
	    },*/

	    initialize: function () {
	        console.log("initialize");
			console.log(this.model);
			new omeroExportView({ model: this.model });
			new TooltipView();
			new TooltipCheckView();
			new graphEditView({ model: this.model });
	    },

	    /*submit: function (e) {
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
	    }*/
	});

