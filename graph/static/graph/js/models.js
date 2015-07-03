
	var AnnotationModel = Backbone.Model.extend({
		url: "/graph/find"
	});

	var GraphModel = Backbone.Model.extend({
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