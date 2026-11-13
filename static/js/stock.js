// FromRythu - Stock Record & History Helper
function fetchStockHistory(productId, productName) {
    const modalTitle = document.getElementById('stockHistoryModalTitle');
    const modalBody = document.getElementById('stockHistoryModalBody');
    if (modalTitle) modalTitle.innerText = `Stock History: ${productName}`;

    if (modalBody) {
        modalBody.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-success" role="status"></div><p class="mt-2 text-muted">Loading stock audit trail...</p></div>';
    }

    fetch(`/inventory/api/product/${productId}/history/`)
        .then(res => res.json())
        .then(data => {
            if (!modalBody) return;
            if (data.records && data.records.length > 0) {
                let html = `
                    <div class="mb-3 p-2 bg-light rounded d-flex justify-content-between align-items-center">
                        <strong>Available Stock:</strong> <span class="badge bg-success fs-6">${data.available_stock} units</span>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Quantity</th>
                                    <th>Batch</th>
                                    <th>Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                data.records.forEach(r => {
                    const badgeClass = r.type === 'IN' ? 'bg-success' : 'bg-danger';
                    const sign = r.type === 'IN' ? '+' : '-';
                    html += `
                        <tr>
                            <td><small>${r.created_at}</small></td>
                            <td><span class="badge ${badgeClass}">${r.type}</span></td>
                            <td><strong>${sign}${r.quantity}</strong></td>
                            <td><small>${r.batch_no || '-'}</small></td>
                            <td><small class="text-muted">${r.notes || '-'}</small></td>
                        </tr>
                    `;
                });
                html += '</tbody></table></div>';
                modalBody.innerHTML = html;
            } else {
                modalBody.innerHTML = '<div class="alert alert-info">No stock movements recorded yet for this product.</div>';
            }
        })
        .catch(err => {
            if (modalBody) {
                modalBody.innerHTML = '<div class="alert alert-danger">Error loading stock logs.</div>';
            }
        });
}

