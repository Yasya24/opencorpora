var hideMentionsTypeSelector = function() {
   $('.m-floating-block').fadeOut(100);
};

var showMentionsTypeSelector = function(x, y) {
   var l = x - $('.m-floating-block').width() / 2;
   var t = y - $('.m-floating-block').height() - 10;
   if (l < 0) l = 3;
   $('.m-floating-block').css('left', l)
                       .css('top', t);
   $('.m-floating-block').fadeIn(100);
};

var clearMentionsHighlight = function() {
   $('.mentions-current-selection').removeClass('mentions-current-selection');
   $('.ner-token-highlighted-m').removeClass('ner-token-highlighted-m');
};

var clearMentionsSelectedTypes = function() {
    $('.mention-type-selector').find('.btn').removeClass('active');
};

var highlightMentionTokens = function($table_rows) {
  $('.ner-token.ner-token-highlighted-m').removeClass('ner-token-highlighted-m');
  $table_rows.each(function(i, row) {
    var tokens = $('.ner-token-border').filterByAttr('data-entity-id', $(row).attr('data-entity-id'))
      .parents('.ner-token');
    tokens.addClass('ner-token-highlighted-m');
  });
};

$(document).ready(function() {
   $(document).on('click', '.ner-mine .ner-table tr[data-entity-id]', function() {

      if ($(this).parents('.ner-row').find('.mentions-current-selection').length
         !== $('.mentions-current-selection').length) return false;

      $(this).toggleClass('mentions-current-selection');

      var current = $('.mentions-current-selection');
      highlightMentionTokens(current);

      if (!current.length) {
         hideMentionsTypeSelector();
      }
      else {
         var offset = current.first().offset();
         var X = offset.left + $(this).width() / 2;
         var Y = offset.top - 10;
         showMentionsTypeSelector(X, Y);
      }
   });

   $('.mention-type-selector > .btn').click(function() {
      var selected = $('.mentions-current-selection');
      var selectedText = '';

      selected.each(function() {
         selectedText += '[' + $(this).find('.ner-entity-text').text().trim() + '] ';
      });

      var type = $(this).attr('data-type-id');
      var selectedIds = selected.mapGetter('data-entity-id');

      var paragraph = selected.parents('.ner-row').find('.ner-paragraph');
      $.post('/ajax/ner.php', {
         act: 'newMention',
         entities: selectedIds,
         object_type: type
      }, function(response) {
         notify('Упоминание добавлено.', 'success');
         selected.each(function() {
            var text = $(this).find('.ner-entity-text');
            text.prepend($('<span>')
               .addClass('ner-entity-mention-link')
               .addClass('label-palette-' + (MENTION_TYPES[type]['color']))
               .attr('data-mention-id', response.id));
         });

         var t = $('table.mentions-table').filterByAttr('data-par-id', paragraph.attr('data-par-id'));
         var tr = $('.templates').find('.m-tr-template').clone().removeClass('m-tr-template');
         tr.add(tr.find('.remove-mention')).add(tr.find('.selectpicker-tpl'))
            .attr('data-mention-id', response.id);

         tr.find('.selectpicker-tpl').find('option').each(function(i, o) {
            if (type === $(o).text()) $(o).attr('selected', true);
         });

         tr.find('.selectpicker-tpl').removeClass('selectpicker-tpl').addClass('selectpicker').selectpicker();
         tr.find('td.ner-mention-text').text(selectedText);
         t.append(tr);

         clearMentionsHighlight();
         clearMentionsSelectedTypes();
         hideMentionsTypeSelector();
      });
   });

   $('.mentions-table').on('change', '.selectpicker', function(e) {
      var mentionId = $(this).parents('tr').attr('data-mention-id');
      var type = $(this).val().toString();
      log_event("mention", "updated types", mentionId, type);
      $.post('/ajax/ner.php', {
         act: 'setMentionType',
         mention: mentionId,
         object_type: type
      }, function(response) {
         notify("Тип упоминания сохранен.");
         $('.ner-entity-mention-link').filterByAttr('data-mention-id', mentionId)
            .removeClassRegex(/label-palette-\d/)
            .addClass('label-palette-' + MENTION_TYPES[type]['color']);
      });
      e.stopPropagation();
   });

   $('.mentions-table').on('click', '.remove-mention', function(e) {
      if (window.confirm("Вы действительно хотите удалить это упоминание?")) {
         var tr = $(this).parents('tr');
         var mentionId = tr.attr('data-mention-id');
         log_event("mention", "deleting mention", mentionId,
            tr.find('td.ner-mention-text').text().trim());

         $.post('/ajax/ner.php', {
            act: 'deleteMention',
            mention: mentionId
         },
         function(response) {
            notify("Упоминание удалено.");
            tr.remove();
            $('.ner-entity-mention-link').filterByAttr('data-mention-id', mentionId).remove();
        });
      }
      e.stopPropagation();
   });

   $('.tab-opener').on('click', function() {
      clearMentionsHighlight();
      clearMentionsSelectedTypes();
      hideMentionsTypeSelector();
   });
});
