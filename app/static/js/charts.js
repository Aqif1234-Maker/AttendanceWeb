function renderBarChart(canvasId, data, titleText) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (ctx.chartInstance) {
    ctx.chartInstance.destroy();
  }

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Present', 'Absent', 'Late'],
      datasets: [
        {
          label: titleText,
          data: [data.present, data.absent, data.late],
          backgroundColor: ['#28a745', '#dc3545', '#ffc107']
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      }
    }
  });

  ctx.chartInstance = chart;
  return chart;
}
