(function($) {
  $.fn.checkbox = function(on, off) {
    return this.each(function() {
      $(this).click(function() {
        var $this = $(this);
        
        // important: checked property has already been updated
        if($this.is(":checked")) {
          var ret = $.proxy(on, this)(function(nxt) { 
            if(nxt) {
              $this.attr("checked", true);
            } else {
              $this.attr("checked", false);
            }
          });
          
          // support async callback or return value based transition
          if(ret !== undefined) {
            return ret;
          }

          return false;
        }

        var ret = $.proxy(off, this)(function(nxt) { 
          if(nxt) {
            $this.attr("checked", true);
          } else {
            $this.attr("checked", false);
          }
        });
        
        if(ret !== undefined) {
          return !ret;
        }

        return false;
      });
    });
  };
})(jQuery);
