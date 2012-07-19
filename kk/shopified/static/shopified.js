/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

(function ($) {
    $(document).ready(function () {
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
            // it's not realistic to think we can deal with all the bugs
            // of IE 6 and lower. Fortunately, all this is just progressive
            // enhancement.
            return;
        }
        var current, toggleBoxes = $('.details').hide();
        $('a.show-details').on("click", function (e) {
            e.preventDefault();
            current = $(this).next('.details');
            $('.details').not(current).slideUp('slow');
            current.toggle('slow');
        });
    });
}(jQuery));
