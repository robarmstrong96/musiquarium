// (function($) {
//     $(document).ready(function(){
//       $("#dataTable").dataTable({
//         responsive: {
//           details: {
//               display: $.fn.dataTable.Responsive.display.modal( {
//                   header: function (row) {
//                       var data = row.data();
//                       return 'Details for '+data[1]+' '+data[2];
//                   }
//               } ),
//               renderer: $.fn.dataTable.Responsive.renderer.tableAll()
//           }
//         },
//         "columnDefs": [
//           { "orderable": false, "targets": 5 } // Disables sorting of album artwork
//         ]
//       });
//     });
// })(jQuery); // End of use strict
