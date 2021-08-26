$(document).on('click', '.finalize', function() {
  var warning = 'Realmente deseja finalizar seu turno?';
  if (confirm(warning)) {
  // Do something
    console.log('Turno finalizado.');
    window.location.href = "/reports/finalizework";
    return true;
  }else {
    // Do something else
    console.log('Operação cancelada.');
    return false;
  }
});