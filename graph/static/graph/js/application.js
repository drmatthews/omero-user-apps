$(function(){	
	var Ann = new AnnotationModel();
	var Graph = new GraphModel();

	new AnnotationView({ model: Ann, graphModel: Graph });
	new GraphPlotView({ model: Graph });
});