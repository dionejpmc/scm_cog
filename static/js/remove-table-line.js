$(document).on('click', 'img.imgdel', function deleteRow() {
    var warning = 'Realmente deseja remover essa linha?';
    if (confirm(warning)) {
      // Do something
 
      //$(this).closest('tr').remove();

     
      var vug = $(this).closest('tr').find('.ug').text();
      var vpch = $(this).closest('tr').find('.pch').text();
      var datastop = $(this).closest('tr').find('.datain').text();
      ug = vug.replace(/\s/g, '');
      pch = vpch.replace(/\s/g, '');
      //datastop = vdatastop.replace(/\s/g, '');
      console.log(datastop);
      window.location.href = "/reports/removeline?ug="+ug+"&pch="+pch+"&datastop="+datastop;
    }else {
      // Do something else
      console.log('Remocao cancelada.');
      return false;
    }
  });