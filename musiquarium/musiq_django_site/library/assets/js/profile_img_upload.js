(function($) {
  $(document).ready(function() {
      $("#input-b9").fileinput({
          showPreview: false,
          showUpload: true,
          elErrorContainer: '#kartik-file-errors',
          allowedFileExtensions: ["jpg", "png", "gif"],
          uploadUrl: "./assets/img/avatars/"
      });
  });
})(jQuery); // End of use strict
