(function () {
  const alerts = document.querySelectorAll('.alert');
  if (alerts.length) {
    setTimeout(() => {
      alerts.forEach((alert) => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      });
    }, 4000);
  }

  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }
})();

function showToast(message, variant = 'success') {
  const toastEl = document.getElementById('globalToast');
  if (!toastEl) return;

  const toastBody = toastEl.querySelector('.toast-body');
  toastBody.textContent = message;

  toastEl.classList.remove('text-bg-success', 'text-bg-danger', 'text-bg-warning', 'text-bg-info');
  toastEl.classList.add(`text-bg-${variant}`);

  const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
  toast.show();
}
