/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: ivan@reciprocitylabs.com
    Maintained By: ivan@reciprocitylabs.com
*/

(function (can, $) {
  'use strict';

  GGRC.Components('inline-edit', {
    tag: 'inline-edit',
    template: can.view(
      GGRC.mustache_path +
      '/components/inline_edit/inline.mustache'
    ),
    scope: {
      instance: null,
      type: '@',
      caId: null,
      property: null,
      values: null,
      isSaving: false,
      context: {
        isEdit: false,
        value: null,
        values: null
      },
      enableEdit: function (ctx, el, ev) {
        ev.preventDefault();

        this.attr('context.isEdit', true);
      },
      onCancel: function (ctx, el, ev) {
        ev.preventDefault();
        this.attr('context.isEdit', false);
        this.attr('context.value', this.attr('property'));
      },
      onSave: function (ctx, el, ev) {
        var caid = this.attr('caId');
        var prop = this.attr('property');
        var instance = this.attr('instance');
        var oldValue = this.attr('property');
        var value = this.attr('context.value');

        ev.preventDefault();
        this.attr('context.isEdit', false);

        if (oldValue === value) {
          return;
        }

        this.attr('isSaving', true);
        instance.refresh().then(function () {
          if (this.attr('caId')) {
            if (this.attr('type') === 'checkbox') {
              value = value ? 1 : 0;
            }
            instance.attr('custom_attributes.' + caid, value);
          } else {
            instance.attr(prop, value);
          }

          instance.save()
            .done(function () {
              $(document.body).trigger('ajax:flash', {
                success: 'Saved'
              });
            })
            .fail(function () {
              $(document.body).trigger('ajax:flash', {
                error: 'There was a problem saving'
              });
            })
            .always(function () {
              this.attr('isSaving', false);
            }.bind(this));
        }.bind(this));
      }
    },
    init: function () {
      var scope = this.scope;
      var value = scope.attr('property');

      if (!scope.instance.custom_attributes) {
        _.defer(scope.instance.setup_custom_attributes.bind(scope.instance));
      }

      if (scope.attr('caId') && scope.attr('type') === 'checkbox') {
        value = value === '1';
      }
      scope.attr('context.value', value);
      if (_.isString(scope.attr('values'))) {
        scope.attr('context.values', scope.attr('values').split(','));
      }
    },
    events: {
      click: function () {
        this.scope.attr('isInside', true);
      },
      '{window} click': function (el, ev) {
        if (this.scope.attr('context.isEdit') &&
            !this.scope.attr('isInside')) {
          this.scope.onSave(this.scope, el, ev);
        }
        this.scope.attr('isInside', false);
      }
    }
  });
})(window.can, window.can.$);
