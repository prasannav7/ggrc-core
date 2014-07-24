/*!
    Copyright (C) 2014 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: brad@reciprocitylabs.com
    Maintained By: brad@reciprocitylabs.com
*/

;(function(can, $, GGRC, CMS) {

GGRC.Controllers.Modals("GGRC.Controllers.ApprovalWorkflow", {
  defaults : {
    original_object : null,
    new_object_form: true,
    model: CMS.ModelHelpers.ApprovalWorkflow,
    modal_title: "Submit for review",
    content_view: GGRC.mustache_path + "/wf_objects/approval_modal_content.mustache",
    button_view : GGRC.Controllers.Modals.BUTTON_VIEW_SAVE_CANCEL
  }
}, {
  init : function() {
    this.options.button_view = GGRC.Controllers.Modals.BUTTON_VIEW_SAVE_CANCEL;
    this._super.apply(this, arguments);
    this.options.attr("instance", new CMS.ModelHelpers.ApprovalWorkflow({
      original_object : this.options.instance
    }));
  },

});

GGRC.register_modal_hook("approvalform", function($target, $trigger, option) {
  var instance,
      object_params = JSON.parse($trigger.attr('data-object-params') || "{}");

  if($trigger.attr('data-object-id') === "page") {
    instance = GGRC.page_instance();
  } else {
    instance = CMS.Models.get_instance(
      $trigger.data('object-singular'),
      $trigger.attr('data-object-id')
    );
  }

  $target
  .modal_form(option, $trigger)
  .ggrc_controllers_approval_workflow({
    object_params : object_params,
    current_user : GGRC.current_user,
    instance : instance
  });
});

})(this.can, this.can.$, this.GGRC, this.CMS);
