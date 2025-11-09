// Calcula subtotal de una fila
function recalcRow(row) {
  if (!row) return;
  const qtyInput = row.querySelector('input[id$="-cantidad"]');
  const priceInput = row.querySelector('input[id$="-precio_unitario"]');
  const subtotalInput = row.querySelector('input[id$="-subtotal"]');

  if (!qtyInput || !priceInput || !subtotalInput) return;

  const qty = parseFloat((qtyInput.value || '0').replace(',', '.')) || 0;
  const price = parseFloat((priceInput.value || '0').replace(',', '.')) || 0;
  const subtotal = qty * price;

  subtotalInput.value = subtotal.toFixed(2);
}

// Suma todos los subtotales y actualiza el campo total de la venta
function recalcTotal() {
  let total = 0;
  const subtotalInputs = document.querySelectorAll('input[id$="-subtotal"]');

  subtotalInputs.forEach(function (input) {
    const val = parseFloat((input.value || '0').replace(',', '.'));
    if (!isNaN(val)) {
      total += val;
    }
  });

  const totalInput = document.querySelector('#id_total');
  if (totalInput) {
    totalInput.value = total.toFixed(2);
  }
}

// Añade listeners a una fila (cantidad y precio)
function attachRowListeners(row) {
  if (!row) return;
  const inputs = row.querySelectorAll('input[id$="-cantidad"], input[id$="-precio_unitario"]');
  inputs.forEach(function (input) {
    input.addEventListener('input', function () {
      recalcRow(row);
      recalcTotal();
    });
  });
}

function initDetalleVenta() {
  // Listeners para filas existentes
  const rows = document.querySelectorAll('.dynamic-detalleventa');
  rows.forEach(function (row) {
    attachRowListeners(row);
  });

  // Cuando Django agrega una nueva fila inline ("Add another Detalle venta")
  document.body.addEventListener('formset:added', function (event) {
    const row = event.target;
    if (row && row.classList.contains('dynamic-detalleventa')) {
      attachRowListeners(row);
    }
  });
}

document.addEventListener('DOMContentLoaded', initDetalleVenta);
