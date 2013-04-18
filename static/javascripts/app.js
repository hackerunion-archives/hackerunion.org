$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});


function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&#]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(window.location.search);
    if(results === null) return "";
    else return decodeURIComponent(results[1].replace(/\+/g, " "));
}

function isValidEmailAddress(emailAddress) {
    var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
    return pattern.test(emailAddress);
};


;(function ($, window, undefined) {
  'use strict';
  
  var $doc = $(document),
      Modernizr = window.Modernizr;

  $(document).ready(function() {
    $.fn.foundationAlerts           ? $doc.foundationAlerts() : null;
    $.fn.foundationButtons          ? $doc.foundationButtons() : null;
    $.fn.foundationAccordion        ? $doc.foundationAccordion() : null;
    $.fn.foundationNavigation       ? $doc.foundationNavigation() : null;
    $.fn.foundationTopBar           ? $doc.foundationTopBar() : null;
    $.fn.foundationCustomForms      ? $doc.foundationCustomForms() : null;
    $.fn.foundationTabs             ? $doc.foundationTabs({callback : $.foundation.customForms.appendCustomMarkup}) : null;
    $.fn.foundationTooltips         ? $doc.foundationTooltips() : null;
    $.fn.foundationMagellan         ? $doc.foundationMagellan() : null;
    $.fn.foundationClearing         ? $doc.foundationClearing() : null;


    $.fn.placeholder                ? $('input, textarea').placeholder() : null;


    // Hack to make the tabs work, zurb doesn't seem
    // to be working correctly here
    var History = window.History;

    $('.talk-tab').find('a').click(function() {
      History.replaceState({state:'talk'}, "Hacker Union (Talk)", "?state=talk");
    });
    $('.event-tab').find('a').click(function() {
      History.replaceState({state:'event'}, "Hacker Union (Events)", "?state=event");
    });
    $('.intro-tab').find('a').click(function() {
      History.replaceState({state:'intro'}, "Hacker Union (Help)", "?state=intro");
    });
    $('.leader-tab').find('a').click(function() {
      History.replaceState({state:'leader'}, "Hacker Union (Admin)", "?state=leader");
    });
    var state = getParameterByName("state");
    if(state !== "") {
      if(state === "talk") {
        $('.talk-tab').find('a').click();
      }
      if(state === "event") {
        $('.event-tab').find('a').click();
      }
      if(state === "intro") {
        $('.intro-tab').find('a').click();
      }
      if(state === "leader") {
        $('.leader-tab').find('a').click();
      }
    }

    var cleanURL = function(url) {
      return url.replace(/\/\/+/g,'\/');
    };

    $('.fake-save').click(function() {
        window.location = window.location.href;
    });

    $('.talk-content-input').redactor({minHeight: 100, source: false});
    $('.event-content-input').redactor({minHeight: 100, source: false});
    $('.edit-event-content-input').redactor({minHeight: 100, source: false});
    $('.comment-content-input').redactor({minHeight: 100, source: false});
    $('.pending-content-input').redactor({minHeight: 100, source: false});
    $('.intro-content-input').redactor({minHeight: 100, source: false});
    $('.edit-bulletin-input').redactor({minHeight: 100, source: false});
    $('.project-content-input').redactor({minHeight: 100, source: false});
    $('.edit-project-content-input').redactor({minHeight: 100, source: false});

    var clearEventModal = function() {
      $('.event-time-start-input').val("");
      $('.event-time-end-input').val("");
      $('.event-where-input').val("");
      $('.event-title-input').val("");
      $('.event-content-input').setCode("");
    };

    var edit_id = -1;

    var togglePromote = function(event) {
      if (!$(event.target).data('leader')) {
        if ($(event.target).closest('.post').hasClass('promoted')) {
          return false;
        }
      }

      $.ajax({
        type: "POST",
        url: cleanURL(window.location.pathname + '/posts/' + $(event.target).data('id') + '/promote/'),
        success: function(data) {
          if ($(event.target).data('leader')) {
            $(event.target).closest('.post').toggleClass('promoted');
            $(event.target).closest('.post').find('.icon-promoted').toggleClass('hidden');
            $(event.target).closest('.promote').toggleClass('active');
          } else {
            alert("Your promotion request has been submitted to the moderators.");
            updateSidebar(data.value.sidebar);
          }
        }
      });
      return false;
    };

    var makeLeader = function(event) {
      if (!confirm("Make this recruit a guide?")) {
        return false;
      }

      $.ajax({
        type: "POST",
        url: cleanURL('/accounts/guide/'),
        data: {
            username: $(event.target).data('username'),
            grant: true
        },
        success: function(data) {
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var removeMentee = function(event) {
      if (!confirm("Stop guiding this user?")) {
        return false;
      }

      $.ajax({
        type: "POST",
        url: cleanURL('/accounts/abandon/'),
        data: {
            user: $(event.target).data('user') 
        },
        success: function(data) {
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var makeModerator = function(event) {
      if (!confirm("Make this recruit a moderator?")) {
        return false;
      }

      $.ajax({
        type: "POST",
        url: cleanURL('/accounts/moderator/'),
        data: {
            username: $(event.target).data('username'),
            grant: true
        },
        success: function(data) {
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var banMentee = function(event) {
      if (prompt("Permanently ban this user? Type \"BAN\" to proceed.") != "BAN") {
        return false;
      }

      $.ajax({
        type: "POST",
        url: cleanURL('/accounts/ban/'),
        data: {
            username: $(event.target).data('username') 
        },
        success: function(data) {
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var toggleFollow = function(event, url) {
      if(!url) {
        url = cleanURL(window.location.pathname + '/posts/' + $(event.target).data('id') + '/follow/');
      }
      $.ajax({
        type: "POST",
        url: url,
        success: function(data) {
          $(event.target).closest('.attending').toggleClass('active');
          var newCount;
          if(data.value.followed) {
              newCount = parseInt($(event.target).closest('.event').find('.hacker-count').text(), 10) + 1;
              $(event.target).closest('.event').find('.hacker-count').text(newCount + " ");
            $(event.target).closest('.event').find('.faces').append("<span><img src='" + data.value.url + "' class='has-tip tip-top' data-id='" + data.value.id + "' title='" + data.value.username + "'/></span>");
          } else {
            newCount = parseInt($(event.target).closest('.event').find('.hacker-count').text(), 10) - 1;
            $(event.target).closest('.event').find('.hacker-count').text(newCount + " ");
            $(event.target).closest('.event').find('.faces').find("*[data-id='" + data.value.id + "']").closest('span').remove();
          }
          if (newCount == 1) {
            $('.hacker-count-label').text('hacker is in. ');
          } else if(newCount === 0 || newCount == 2) {
            $('.hacker-count-label').text('hackers are in. ');
          }
        }
      });
      return false;
    };

    $('.event-perma-attending').click(function(event) {
      toggleFollow(event, cleanURL(window.location.pathname.substr(0, window.location.pathname.indexOf('/posts/')) + '/posts/' + $(event.target).data('id') + '/follow/'));
    });

    $('.project-attending').click(function(event) {
      $.ajax({
        type: "POST",
        url: cleanURL(window.location.pathname.substr(0, window.location.pathname.indexOf('/posts/')) + '/posts/' + $(event.target).data('id') + '/follow/'),
        success: function(data) {
          $(event.target).closest('.attending').toggleClass('active');
          var newCount;
          if(data.value.followed) {
            newCount = parseInt($(event.target).closest('.project').find('.hacker-count').text(), 10) + 1;
            $(event.target).closest('.project').find('.hacker-count').text(newCount + " ");
            $(event.target).closest('.project').find('.faces').append("<span><img src='" + data.value.url + "' class='has-tip tip-top' data-id='" + data.value.id + "' title='" + data.value.username + "'/></span>");
          } else {
            newCount = parseInt($(event.target).closest('.project').find('.hacker-count').text(), 10) - 1;
            $(event.target).closest('.project').find('.hacker-count').text(newCount + " ");
            $(event.target).closest('.project').find('.faces').find("*[data-id='" + data.value.id + "']").closest('span').remove();
          }
          if (newCount == 1) {
            $('.hacker-count-label').text('hacker is in. ');
          } else if(newCount === 0 || newCount == 2) {
            $('.hacker-count-label').text('hackers are in. ');
          }
        }
      });
      return false;
    });

    var introEditModal = function(event) {
      // populate the modal with the correct nah-m sayuns.
      var $post = $(event.target).closest('.post');
      edit_id = $post.data('id');
      $('.edit-bulletin-input').setCode($post.find('.post-content').data('content'));

      $('.save-post').unbind().click(function() {
        if(validateEdit()) {
          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/intro/' + edit_id + '/'),
            data: {
              content: $('.edit-bulletin-input').getCode()
            },
            success: function(data) {
              $('#editBulletin').trigger('reveal:close');
              updateIntroFeed(data);
            }
          });
        }
      });
      $('.delete-post').unbind().click(function() {
          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/intro/' + edit_id + '/'),
            data: {
              content: $('.edit-bulletin-input').getCode(),
              delete: true
            },
            success: function(data) {
              $('#editBulletin').trigger('reveal:close');
              updateIntroFeed(data);
            }
          });
      });
    };

    $('.all-talk').click(function() {
      $('.talk-filter').find('.selected').removeClass('selected');
      $(this).addClass('selected');
      $('.talk').show();
    });
    $('.promoted-talk').click(function() {
      $('.talk-filter').find('.selected').removeClass('selected');
      $(this).addClass('selected');
      $('.talk').hide();
      $('.talk.promoted').show();
    });
    $('.all-event').click(function() {
      $('.event-filter').find('.selected').removeClass('selected');
      $(this).addClass('selected');
      $('.event').show();
    });
    $('.promoted-event').click(function() {
      $('.event-filter').find('.selected').removeClass('selected');
      $(this).addClass('selected');
      $('.event').hide();
      $('.event.promoted').show();
    });
    
    var talkEditModal = function(event) {
      // populate the modal with the correct nah-m sayuns.
      var $post = $(event.target).closest('.post');
      edit_id = $post.data('id');
      $('.edit-bulletin-input').setCode($post.find('.post-content').data('content'));

      $('.save-post').unbind().click(function() {
        if(validateEdit()) {
          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/talk/' + edit_id + '/'),
            data: {
              content: $('.edit-bulletin-input').getCode()
            },
            success: function(data) {
              $('#editBulletin').trigger('reveal:close');
              updateTalkFeed(data);
            }
          });
        }
      });
      $('.delete-post').unbind().click(function() {
        $.ajax({
          type: "POST",
          url: cleanURL(window.location.pathname + '/talk/' + edit_id + '/'),
          data: {
            content: $('.edit-bulletin-input').getCode(),
            delete: true
          },
          success: function(data) {
            $('#editBulletin').trigger('reveal:close');
            updateTalkFeed(data);
          }
        });
      });
    };
    

    var eventEditModal = function(event) {
      // populate the modal with the correct nah-m sayuns.
      var $post = $(event.target).closest('.post');
      edit_id = $post.data('id');

      $('.edit-event-content-input').setCode($post.find('.post-content').data('content'));
      $('.edit-event-title-input').val($post.find('.title').text());

      var start = $post.find('.start-date');
      var end = $post.find('.end-date');

      $('.edit-event-day-start').val(start.data('date'));
      $('.edit-event-time-start').val(start.data('time'));
      $('.edit-event-day-end').val(end.data('date'));
      $('.edit-event-time-end').val(end.data('time'));
      $('.edit-event-where-input').val($post.find('.where').text());
      // open the modal.

      // figure out how to submit currently
      $('.save-event').unbind().click(function() {
        if(validateEventEdit()) {
          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/event/' + edit_id + '/'),
            data: {
              'start': $('.edit-event-day-start').val().trim() + ' ' + $('.edit-event-time-start').val().trim(),
              'end': $('.edit-event-day-end').val().trim() + ' ' + $('.edit-event-time-end').val().trim(),
              'where': $('.edit-event-where-input').val(),
              'title': $('.edit-event-title-input').val(),
              'content': $('.edit-event-content-input').getCode()
            },
            success: function(data) {
              $('#editEvent').trigger('reveal:close');
              $('.event-feed').html(data.value.feed);
              bindEventButtons();
            }
          });
        }
      });
      $('.delete-event').unbind().click(function() {
          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/event/' + edit_id + '/'),
            data: {
              'start': $('.edit-event-day-start').val().trim() + ' ' + $('.edit-event-time-start').val().trim(),
              'end': $('.edit-event-day-end').val().trim() + ' ' + $('.edit-event-time-end').val().trim(),
              'where': $('.edit-event-where-input').val(),
              'title': $('.edit-event-title-input').val(),
              'content': $('.edit-event-content-input').getCode(),
              delete: true
            },
            success: function(data) {
              $('#editEvent').trigger('reveal:close');
              $('.event-feed').html(data.value.feed);
              bindEventButtons();
            }
          });
      });
    };


    $('.project-edit').click(function(event) {
      var $post = $(event.target).closest('.project');
      edit_id = $(event.target).data('id');

      $('.edit-project-title-input').val($post.find('.project-title').data("title"));
      $('.edit-project-content-input').setCode($post.find('.project-content').html());
      $('.edit-project-image-input').val($post.find('.project-picture').attr('src'));
    });

    $('.delete-project').click(function() {
      $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname.substr(0, window.location.pathname.indexOf('/posts/')) + '/projects/' + edit_id + '/'),
            data: {
              'title': $('.edit-project-title-input').val(),
              'content': $('.edit-project-content-input').getCode(),
              'url': $('.edit-project-image-input').val(),
              delete: true
            },
            success: function(data) {
              $('#editProject').trigger('reveal:close');
              window.location = cleanURL(window.location.pathname.substr(0, window.location.pathname.indexOf('/posts/')) + '/projects/');
            }
      });
    });
    $('.save-project').click(function() {
      if(validateEmpty([$('.edit-project-title-input')], [$('.edit-project-content-input')])) {
        $.ajax({
              type: "POST",
              url: cleanURL(window.location.pathname.substr(0, window.location.pathname.indexOf('/posts/')) + '/projects/' + edit_id + '/'),
              data: {
                'title': $('.edit-project-title-input').val(),
                'content': $('.edit-project-content-input').getCode(),
                'url': $('.edit-project-image-input').val()
              },
              success: function(data) {
                $('#editProject').trigger('reveal:close');
                location.reload();
              }
        });
      }
    });

    var bindTalkButtons = function() {
      $('.talk-promote').unbind().click(togglePromote);
      $('.talk-edit').click(talkEditModal);
    };
    
    var bindEventButtons = function() {
      $('.event-promote').unbind().click(togglePromote);
      $('.event-attending').unbind().click(toggleFollow);
      $('.event-edit').unbind().click(eventEditModal);
      $('a.recommend').unbind().click(function (event) {
        var post_id = $(event.target).data('id');
        
        $('.group-message-content').val($(this).data("message") + ': http://' + cleanURL(window.location.host + "/" + window.location.pathname + (post_id ? ('/posts/' + $(event.target).data('id') + "/") : "")));
        $('#sendGroupMessage').reveal();
      });
    };

    var bindIntroButtons = function() {
      $('.intro-edit').click(introEditModal);
    };

    var updateSidebar = function(data) {
      $('.sidebar').html(data);
      reloadFoundation();
      bindUserMessage();
      bindSidebar();
    };

    var bindSidebar = function() {
      $('.request-active').unbind().click(request_handler(4));
      $('.request-deny').unbind().click(request_handler(3));
      $('.request-approve').unbind().click(request_handler(2));
      $('.make-leader').unbind().click(makeLeader);
      $('.remove-mentee').unbind().click(removeMentee);
      $('.ban-mentee').unbind().click(banMentee);
      $('.make-moderator').unbind().click(makeModerator);
      $('.official-notice-toggle').unbind().checkbox(manageNotices({ "official": true }), manageNotices({ "official": false }));
      $('.discuss-notice-toggle').unbind().checkbox(manageNotices({ "discuss": true }), manageNotices({ "discuss": false }));
      $('.announce-notice-toggle').unbind().checkbox(manageNotices({ "announce": true }), manageNotices({ "announce": false }));
      $('.digest-notice-toggle').unbind().checkbox(manageDigest(true, true), manageDigest(false, true));
      $('.digest-notice-select').unbind().change(manageDigest(true));
    };

    var manageDigest = function(subscribe, toggle) {
        return function(nxt) {
            if (toggle) {
                if (!subscribe) {
                    if (!confirm("Unsubscribe from the curated digest?")) {
                        return true;
                    }
                    
                    $('.digest-notice-select').attr("disabled", true);
                } else {
                    $('.digest-notice-select').removeAttr("disabled");
                }
            }

            $.ajax({
              type: "POST",
              data: { 
                digest: subscribe ? parseInt($('.digest-notice-select').val()) : 1
              },
              url: cleanURL('/accounts/settings/notice'),
              success: function(data) {
              }
            });

            return subscribe;
        };
    };

    var manageNotices = function(opts) {
        return function(nxt) {
            var subscribe = false;

            $.each(opts, function (k, v) {
                subscribe = v;
                return false;
            });
            
            if (!subscribe) {
              if (!confirm("Unsubscribe from this mailing list?")) {
                  return true;
              }
            }

            $.ajax({
              type: "POST",
              data: opts,
              url: cleanURL('/accounts/settings/notice'),
              success: function(data) {
              }
            });

            return subscribe;
        };
    };

    var updateIntroFeed = function(data) {
        $('.intro-feed').html(data.value.feed);
        $('.intro-content-input').setCode('');
        bindIntroButtons();
    };

    var updateTalkFeed = function(data) {
        $('.talk-feed').html(data.value.feed);
        $('.talk-content-input').setCode('');
        $('.talk-leader-toggle').removeAttr('checked');
        bindTalkButtons();
    };

    var reloadFoundation = function() {
        $(document).unbind("click.fndtn");
        $(document).foundationTabs("events");
        $(document).foundationButtons();
        $(document).foundationTooltips();
        $(document).foundationAlerts();
    };

    var request_handler = function(resp) {
        return function(event) {
          var req = $(event.target).data('request');
          
          if (req) {
            switch(parseInt(req)) {
              case 1:
              case 3:
                if (!confirm("Approval will make you this person's guide. Continue?")) {
                    return false;
                }

                break;

              default:
                break;
            }
          }

          $.ajax({
            type: "POST",
            url: cleanURL(window.location.pathname + '/lead/' + $(event.target).data('pk') + '/' + $(event.target).data('name') + '/'),
            data: {
                'response': resp
            },
            success: function(data) {
              if (resp == 4) {
                // TODO: decide on what to do with "active" requests
                $(event.target).closest('.post').addClass('leadership-active');
              } else {
                $(event.target).closest('.post').fadeOut();
              }
              updateSidebar(data.value.sidebar);
            }
          });
          return false;
        };
    };

    var validateEmail = function(selector) {
      if(isValidEmailAddress(selector.val()))
        return true;
      selector.addClass('error');
      return false;
    };

    var validateEmails = function(selector) {
      var valid = true;
      $.each(selector.val().split(", "), function(i, v) {
        if(isValidEmailAddress(v))
          return true;
        
        selector.addClass('error');
        valid = false;

        return false;
      });

      return valid;
    };

    var validateEmpty = function(selectorList, redactorSelectorList) {
      var allGood = true;
      for (var i in selectorList) {
        if (selectorList[i].val().trim() === "") {
          allGood = false;
          selectorList[i].addClass("error");
        }
      }
      for (i in redactorSelectorList) {
        var rSelector = redactorSelectorList[i];
        if (rSelector.getText().trim() === "" && rSelector.getCode().indexOf("img") < 0 && rSelector.getCode().indexOf("iframe") < 0) {
          allGood = false;
          rSelector.addClass("error");
        }
      }
      return allGood;
    };

    var validateTalk = function() {
      $('.talk-content-input').removeClass('error');
      return validateEmpty([], [$('.talk-content-input')]);
    };
    var validateIntro = function() {
      $('.intro-content-input').removeClass('error');
      return validateEmpty([], [$('.intro-content-input')]);
    };
    var validateEvent = function() {
      $('#createEvent').find('.error').removeClass('error');
      var nonEmpty = validateEmpty([$('.event-title-input'), $('.event-time-start'),$('.event-day-start'), $('.event-time-end'),$('.event-day-end'), $('.event-where-input')], [$('.event-content-input')]);

      if (!nonEmpty) return false;
      
      var $where = $('.event-where-input');
      if ($where.val().length < 3) {
        $where.addClass('error');
        return false;
      }
      
      var startTime = new Date($('.event-day-start').val().trim() + ' ' + $('.event-time-start').val().trim());
      var endTime = new Date($('.event-day-end').val().trim() + ' ' + $('.event-time-end').val().trim());
      if (startTime < endTime) return true;
      $('.event-time-start').addClass('error');
      $('.event-day-start').addClass('error');
      $('.event-time-end').addClass('error');
      $('.event-day-end').addClass('error');
      return false;
    };
    var validateEventEdit = function() {
      $('#eventEditModal').find('.error').removeClass('error');
      var nonEmpty = validateEmpty([$('.edit-event-title-input'), $('.edit-event-time-start'),$('.edit-event-day-start'), $('.edit-event-time-end'),$('.edit-event-day-end'), $('.edit-event-where-input')], [$('.edit-event-content-input')]);

      if (!nonEmpty) return false;

      var $where = $('.edit-event-where-input');
      if ($where.val().length < 3) {
        $where.addClass('error');
        return false;
      }
      var startTime = new Date($('.edit-event-day-start').val().trim() + ' ' + $('.edit-event-time-start').val().trim());
      var endTime = new Date($('.edit-event-day-end').val().trim() + ' ' + $('.edit-event-time-end').val().trim());
      if (startTime < endTime) return true;
      $('.edit-event-time-start').addClass('error');
      $('.edit-event-day-start').addClass('error');
      $('.edit-event-time-end').addClass('error');
      $('.edit-event-day-end').addClass('error');
      return false;
    };

    var validateEdit = function() {
      $('.edit-bulletin-input').removeClass('error');
      return validateEmpty([], [$('.edit-bulletin-input')]);
    };

    var validateModal = function(modalSelector) {
      $(modalSelector).find('.error').removeClass('error');
      return validateEmpty([$(modalSelector).find('textarea')], []);
    };

    var submitReferral = function() {
      $('.referral-email-input').removeClass('error');
      if(validateEmpty([$('.referral-email-input')], []) && validateEmails($('.referral-email-input'))) {
        $.ajax({
          type: "POST",
          data: {
            'target': $('.referral-email-input').val()
          },
          url: cleanURL('/accounts/invite/'),
          success: function(data) {
            $('.referral-email-input').val();
            $('#confirmInvite').reveal();
          }
        });
      }
      return false;
    };

    var submitInvite = function() {
      $('.invite-email-input').removeClass('error');
      if(validateEmpty([$('.invite-email-input')], []) && validateEmail($('.invite-email-input'))) {
        $.ajax({
          type: "POST",
          data: {
            'target': $('.invite-email-input').val()
          },
          url: cleanURL('/accounts/invite/'),
          success: function(data) {
            $('.invite-email-input').val("");
            $('#confirmInvite').reveal();
          }
        });
      }
      return false;
    };

    var banUser = function() {
      $.ajax({
        type: "POST",
        data: {
          'username': $('.ban-user-input').select2("val")
        },
        url: cleanURL('/accounts/ban/'),
        success: function(data) {
          $('.ban-user-input').select2("val", "");
          $('#confirmBan').reveal();
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var doMentee = function() {
      $.ajax({
        type: "POST",
        data: {
          'mentee': $('.transfer-mentee-input').select2("val"),
          'leader': $('.transfer-leader-input').select2("val")
        },
        url: cleanURL('/accounts/transfer/'),
        success: function(data) {
          $('.transfer-mentee-input').select2("val", "");
          $('.transfer-leader-input').select2("val", "");
          $('#confirmGeneral').reveal();
          updateSidebar(data.value.sidebar);
        }
      });
      return false;
    };

    var doModerator = function(grant) {
      return function() { 
        $.ajax({
          type: "POST",
          data: {
            'username': $('.moderator-user-input').select2("val"),
            'grant': grant
          },
          url: cleanURL('/accounts/moderator/'),
          success: function(data) {
            $('.moderator-user-input').select2("val", "");
            $('#confirmGeneral').reveal();
            updateSidebar(data.value.sidebar);
          }
        });
        return false;
      };
    };

    var doGuide = function(grant) {
      return function() { 
        $.ajax({
          type: "POST",
          data: {
            'username': $('.guide-user-input').select2("val"),
            'grant': grant
          },
          url: cleanURL('/accounts/guide/'),
          success: function(data) {
            $('.guide-user-input').select2("val", "");
            $('#confirmGeneral').reveal();
            updateSidebar(data.value.sidebar);
          }
        });
        return false;
      };
    };

    var injectMarkup = function() {
      $.ajax({
        type: "POST",
        data: {
          'markup': $('.markup-content').val()
        },
        url: cleanURL('/accounts/markup/'),
        success: function(data) {
          $('.markup-content').val();
          $('#confirmGeneral').reveal();
        }
      });
      return false;
    };

    var submitMessage = function(toArray, message, successCallback) {
      $('.group-message-content').removeClass('error');
      var from = "";
      if ($('.group-message-email-input').length) {
        $('.group-message-email-input').removeClass('error');
        from = $('.group-message-email-input').val();
        if(!validateEmail($('.group-message-email-input'))) return;
      }
      if(validateEmpty([$('.group-message-content')], [])) {
        $.ajax({
            type: "POST",
            data: {
              'to': toArray,
              'from': from,
              'message': message
            },
            url: cleanURL('/accounts/message/'),
            success: function(data) {
              successCallback();
            }
          });
      }
    };

    $('.group-message-submit').click(function() {
      submitMessage($('.group-message-select').select2("val"), $('.group-message-content').val(), function() {
        $('#sendGroupMessage').trigger('reveal:close');
        $('.group-message-content').val('');
      });
    });

    var bindUserMessage = function() {
      $('.user-message').unbind().click( function(event) {
        $('#sendGroupMessage').reveal();
        $(".member-message-select,.group-message-select").select2("val", [$(event.target).data('username')]);
      });
    };

    bindUserMessage();

    var bindLeaderTemplates = function() {
        $('.group-message-template').change(function() {
            var $this = $(this);

            if ($this.val()) {
                $this.closest(".reveal-modal").find("textarea").val($this.val());
            }

            return true;
        });
    };

    bindLeaderTemplates();

    $('.member-message-submit').click(function() {
      submitMessage($('.member-message-select').select2("val"), $('.group-message-content').val(), function() {
        $('#sendGroupMessage').trigger('reveal:close');
        $('.group-message-content').val('');
        $(".member-message-select").select2("val", []);
      });
    });

    $('.pair-request').click(function() {
        $.ajax({
            type: "POST",
            data: {
              'content': "I would like @" + $(this).data('username') + " to be my mentor"
            },
            url: cleanURL('/' + $(this).data('chapter') + '/lead/pair/'),
            success: function() {
              $("#confirmRequest").reveal();
            }
          });
    });

    $('.referral-submit').click(submitReferral);
    $('.referral-email-input').keydown(function(e) {
        if (e.keyCode == 13) {
          e.preventDefault();
          return submitReferral();
        }
    });

    $('.invite-submit').click(submitInvite);
    $('.invite-email-input').keydown(function(e) {
        if (e.keyCode == 13) {
          e.preventDefault();
          return submitInvite();
        }
    });

    $('.ban-user-submit').click(banUser);
    
    $('.transfer-mentee-submit').click(doMentee);

    $('.add-moderator-submit').click(doModerator(true));
    $('.remove-moderator-submit').click(doModerator(false));

    $('.add-guide-submit').click(doGuide(true));
    $('.remove-guide-submit').click(doGuide(false));
    
    $('.inject-markup-submit').click(injectMarkup);

    $('.righteous').click(function() {
      $(this).closest('.reveal-modal').trigger('reveal:close');
    });

    $('.talk-submit').click(function() {
      if(validateTalk()) {
        $.ajax({
          type: "POST",
          data: {
            'content': $('.talk-content-input').getCode(),
            'is_announcement': false,
            'is_official': $('.talk-leader-toggle').is(':checked') || false
          },
          url: cleanURL(window.location.pathname + '/talk/'),
          success: updateTalkFeed
        });
      }
      $('.talk-content-input').setCode(""); // Hack a debounce for this button.
      return false;
    });

    

    $('.pending-submit').click(function() {
      $.ajax({
        type: "POST",
        data: {
          'content': $('.pending-content-input').getCode(),
          'is_announcement': false
        },
        url: '/pending/',
        success: function(data) {
          $('.pending-feed').html(data.value.feed);
          $('.pending-content-input').setCode('');
        }
      });
      return false;
    });

    $('.event-submit').click(function() {
      if(validateEvent()) {
        $.ajax({
          type: "POST",
          data: {
            'start': $('.event-day-start').val().trim() + ' ' + $('.event-time-start').val().trim(),
            'end': $('.event-day-end').val().trim() + ' ' + $('.event-time-end').val().trim(),
            'where': $('.event-where-input').val(),
            'title': $('.event-title-input').val(),
            'content': $('.event-content-input').getCode()
          },
          url: cleanURL(window.location.pathname + '/event/'),
          success: function(data) {
            $('.event-feed').html(data.value.feed);
            $('#createEvent').trigger('reveal:close');
            bindEventButtons();
            clearEventModal();
          }
        });
      }
      return false;
    });

    $('.new-mentor-submit').click(function() {
      if(validateModal('#newMentor')) {
        $.ajax({
          type: "POST",
          data: {
            'content': $('.new-mentor-content').val()
          },
          url: cleanURL(window.location.pathname + '/lead/pair/'),
          success: function(data) {
            $('#newMentor').trigger('reveal:close');
            $('.new-mentor-content').val('');
            updateSidebar(data.value.sidebar);
          }
        });
      }
      return false;
    });

    $('.mentor-help-submit').click(function() {
      if(validateModal('#help')) {
        $.ajax({
          type: "POST",
          data: {
            'content': $('.mentor-help-content').val()
          },
          url: cleanURL(window.location.pathname + '/lead/help/'),
          success: function(data) {
            $('#help').trigger('reveal:close');
            $('.mentor-help-content').val('');
            updateSidebar(data.value.sidebar);
          }
        });
      }
      return false;
    });
    $('.become-mentor-submit').click(function() {
      if(validateModal('#becomeLeader')) {
        $.ajax({
          type: "POST",
          data: {
            'content': $('.become-mentor-content').val()
          },
          url: cleanURL(window.location.pathname + '/lead/volunteer/'),
          success: function(data) {
            $('#becomeLeader').trigger('reveal:close');
            $('.become-mentor-content').val('');
            updateSidebar(data.value.sidebar);
          }
        });
      }
      return false;
    });

    $('.intro-submit').click(function() {
      if(validateIntro()) {
        $.ajax({
          type: "POST",
          data: {
            'content': $('.intro-content-input').getCode()
          },
          url: cleanURL(window.location.pathname + '/intro/'),
          success: updateIntroFeed
        });
      }
      return false;
    });

    $('.comment-submit').click(function() {
      $.ajax({
        type: "POST",
        data: {
          'content': $('.comment-content-input').val()
        },
        url: cleanURL(window.location.pathname + '/comment/'),
        success: function(data) {
          $('.comment-feed').html(data.value.feed);
          $('.comment-content-input').setCode('');
        }
      });
      return false;
    });
    $('.close-guide').click(function() {
      $.ajax({
        type: "POST",
        data: {
          'remove': 1
        },
        url: '/accounts/guide/',
        success: function(data) {
        }
      });
      $('.to-do').fadeOut();
      return false;
    });

    $('.invite-button').click(function() {
      $(this).addClass("active");
      $('.no-invite-button').removeClass("active");
      $('.no-invite-content').fadeOut('fast', function() {
        $('.invite-content').fadeIn('fast');
      });
    });
    $('.no-invite-button').click(function() {
      $(this).addClass("active");
      $('.invite-button').removeClass("active");
      $('.invite-content').fadeOut('fast', function() {
        $('.no-invite-content').fadeIn("fast");
      });
    });
    $('.add-comment-toggle').click(function() {
      $('.add-comment-form').fadeToggle();
    });

    $('.open-leader').click(function() {
      $('.sidebar').find('.leader-message').click();
    });

    $('.open-events').click(function() {
      $('.event-tab').find('a').click();
    });
    $('.open-introductions').click(function() {
      $('.intro-tab').find('a').click();
    });
    $('.open-talk').click(function() {
      $('.talk-tab').find('a').click();
    });

    var filterMembers = function() {
      $('.box').removeClass('hide-item');
      if($('.search-by-name').val().trim() !== "") {
        var $boxClosest = $('.box').closest('.box');
        $boxClosest.find(".name:not(:contains('" + $('.search-by-name').val() + "'))").closest('.box').addClass('hide-item');
        $boxClosest.find(".username:contains('" + $('.search-by-name').val() + "')").closest('.box').removeClass('hide-item');
      }
      if($('.ambassadors-only').is(':checked')) {
        $('.box').not(':has(.ambassador)').closest('.box').addClass('hide-item');
      }


      if($(".member-skill-input").select2("val").length) {
        var $hideSet = $('.box');
        var skills = $(".member-skill-input").select2("val");

        for(var skill in skills) {
          $('.box').each(function() {
            var foundSet = $(this).find(".tags li").filter(function() {
              return $(this).text().trim() === skills[skill];
            });
            if(!foundSet.length) {
              $(this).addClass('hide-item');
            }
          });
        }
      }

      $('.isotope').isotope({ filter: ":not(.hide-item)", transformsEnabled: false });

    };

    $('.ambassadors-only, .member-skill-input').change(filterMembers);
    $('.search-by-name').change(filterMembers);
    $('.search-by-name').keyup(filterMembers);
    $('.members-filter-submit').click(filterMembers);

    // Date Picker
    $('.day-start, .day-end').datepicker();

    // Time Picker
    $(".time-start, .time-end").timePicker();

    function addToggle(container) {

      $('#' + container + ' .toggle-this').click(
  
        function() {
            var $holder = $("#" + container);
    
            if ($('.toggle-content', $holder).is(':visible')) {
    
                $('.toggle-arrow', $holder).text('+');
                $('.toggle-content', $holder).hide();
    
            } else {
                $('.toggle-arrow', $holder).text('-');
                $('.toggle-content', $holder).show();
            }
    
            return false;
        });
    }

  addToggle("member-toggle");
  addToggle("event-toggle");
  addToggle("comment-toggle");
  addToggle("application-toggle");



  // Select2 on Members Search
  $(".group-message-select").select2({
    tags: members
  });

  // $(".event-skill-input").select2({
  //   tags: skills
  // });
  if(typeof skills !== 'undefined') {
    $(".account-skill-input").select2({
      tags: skills
    });
    $(".account-affiliation-input").select2({
      tags: affiliations
    });

    $(".member-skill-input").select2({
      tags: skills.concat(affiliations, initiatives)
    });
    $('.member-message-select').select2({
      tags: members
    });
    $('.user-select').select2({
      tags: members,
      multiple: false,
      maximumSelectionSize: 1
    });
  }

  bindTalkButtons();
  bindIntroButtons();
  bindEventButtons();
  bindSidebar();


  // Masonry on members page
  // $('.member-grid .row').masonry({
  //   itemSelector: '.box',
  // });

  // $('.member-grid').hide();

  $('.isotope').isotope({
    // options
    masonry: {
      columnWidth: 310
    },
    transformsEnabled: false,
    itemSelector : '.box',
    onLayout: function() {
        $(".isotope").css("visibility", "visible");
        $(".isotope-loading").hide();
    }
  });

  var tags = getParameterByName("s");
  if(tags !== "") {
    tags = tags.split();
    $(".member-skill-input").select2("val", tags);
  }
  var name = getParameterByName("n");
  if(name !== "") {
    $(".search-by-name").val(name);
  }

  if(name !== "" || tags !== "") {
    filterMembers();
    $('.toggle-arrow').click();
  }
  // $('.member-grid').show();
  



  // $('.member-grid').show();

  // // Masonry on members page
  // $('.chapter-grid .row').masonry({
  //   itemSelector: '.box',
  //   columnWidth: 320,
  //   isFitWidth: true
  // });


  // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
  // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
  // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
  // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
  // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

  // Hide address bar on mobile devices (except if #hash present, so we don't mess up deep linking).
  if (Modernizr.touch && !window.location.hash) {
    $(window).load(function () {
      setTimeout(function () {
        window.scrollTo(0, 1);
      }, 0);
    });
  }

  /******** Nav Bar Notifications ***********/
  $.ajax({
      type: "GET",
      url: cleanURL('/notifications/get'),
      success: function(data) {
        var notifBox = $('#navdropshow');
        var notifs = data['value']['notifs'];
        var chapter = data['value']['chapter'];
        for(var i=0;i < notifs.length;i++) {
          var noti = notifs[i];
          var bull_url = cleanURL("/"+chapter+'/posts/'+noti['bulletin_id']);
          bull_url = encodeURIComponent(bull_url);
          var redir_url = "url="+bull_url+"&notif_id="+noti['notif_id'];
          var newNotiStr = '<li class="notifli" style="text-align:left;"><a href="/notifications/read?'+redir_url+'">' +noti['bulletin_title'];
          if('comment_str' in noti) {
            newNotiStr += ' <span class="notifcomment">'+noti['comment_str']+'</span></a></li>';
          }

          var newNoti = $(newNotiStr);
          notifBox.append(newNoti);
        }

        if(notifs.length == 1 ) {
          $('#numNotifs').css('display','inline-block');
          $('#numNotifs').attr('src','/static/images/notif_circle_1.png');
        } else if( notifs.length == 2) {
          $('#numNotifs').css('display','inline-block');
          $('#numNotifs').attr('src','/static/images/notif_circle_2.png');
        } else if( notifs.length == 3) {
          $('#numNotifs').css('display','inline-block');
          $('#numNotifs').attr('src','/static/images/notif_circle_3.png');
        } else if( notifs.length > 3) {
          $('#numNotifs').attr('src','/static/images/notif_circle_3plus.png');
          $('#numNotifs').css('display','inline-block');
        }
        if(notifs.length > 0) {
          $('#notifDrop').on('mouseover',function() {
            $('#navdropshow').css('display','block');
          });
          $('#notifDrop').on('mouseout',function() {
            $('#navdropshow').css('display','none');
          });
        }
      },
      fail: function(e) { try {console.log(e);} catch(err){} }
  });

  /******** END Nav Bar Notifications ***********/
});

})(jQuery, this);
