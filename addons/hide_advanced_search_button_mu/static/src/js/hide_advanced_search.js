odoo.define("hide_advanced_search_button_mu.hide_advanced_search_button", function(require) {
	"use strict";
		
	var ControlPanelRenderer = require('web.ControlPanelRenderer');
	
	ControlPanelRenderer.include({
		init: function (parent, state, params) {
	        this._super(parent, state, params);
	        this.isAdvancedSearchDisabled = odoo.session_info.isAdvancedSearchDisabled;
	    },
	    start: function (){
	    	if(this.isAdvancedSearchDisabled){
	    		this.displaySearchMenu = false;	    		
//	    		this.$('.o_searchview_more')
//	            .toggleClass('fa-search-minus', this.displaySearchMenu);
//			    this.$('.o_search_options')
//			        .toggleClass('o_hidden', !this.displaySearchMenu);
	        	this.$el.find(".o_searchview_more").remove()
				this.$buttons = false;
	        }
	        this._super();
	    }
	});
});