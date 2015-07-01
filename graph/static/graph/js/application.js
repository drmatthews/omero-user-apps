$(function(){
	var Annotation = Backbone.Model.extend({
		url: "/"
	});
	
	var AnnotationView = Backbone.View.extend({
		
	    events: {
	        "submit form": "submit",
	    },

	    initialize: function () {
	        console.log("initialize");
	    },

	    submit: function (e) {
	        e.preventDefault();
	        console.log("submit");
	    }
	});
	
	var currentAnn = new Annotation();

	var currentAnnView = new AnnotationView()({ model: currentAnn });
});