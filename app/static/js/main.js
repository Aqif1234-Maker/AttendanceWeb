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

  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('sa-theme') || 'dark';
  document.body.setAttribute('data-theme', savedTheme);
  const icon = themeToggle?.querySelector('i');
  if (icon) {
    icon.className = savedTheme === 'light' ? 'bi bi-sun' : 'bi bi-moon-stars';
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.body.setAttribute('data-theme', next);
      localStorage.setItem('sa-theme', next);
      const icon = themeToggle.querySelector('i');
      if (icon) {
        icon.className = next === 'light' ? 'bi bi-sun' : 'bi bi-moon-stars';
      }
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
