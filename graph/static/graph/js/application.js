$(function(){
	var Annotation = Backbone.Model.extend();
	
	var Annotations = Backbone.Collection.extend({
		url: '/',
		model: Annotation
	});
	
	var AnnotationView = Backbone.View.extend({
		
		el: $('#id_preview_annotation'),
		
		initialize: function(){
			_.bindAll(this,'render')
		},
		
		render: function(){
	            $(this.el).attr('value', this.model.get('id')).html(this.model.get('name'));
	            return this;
	    }
	});
});