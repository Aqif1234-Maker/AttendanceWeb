(function () {
  const attendanceContainer = document.getElementById('attendanceList');
  const loadBtn = document.getElementById('loadStudents');
  const saveBtn = document.getElementById('saveAttendance');

  if (!attendanceContainer) {
    return;
  }

  function renderAttendanceList(students) {
    attendanceContainer.innerHTML = '';
    if (!students.length) {
      attendanceContainer.innerHTML = '<p class="text-muted">No students found for this class/section.</p>';
      return;
    }

    students.forEach((student) => {
      const row = document.createElement('div');
      row.className = 'card sa-card mb-2';
      row.innerHTML = `
        <div class="card-body d-flex flex-column flex-lg-row justify-content-between align-items-lg-center">
          <div>
            <h6 class="mb-0">${student.name}</h6>
            <small class="text-muted">Roll: ${student.roll_number}</small>
          </div>
          <div class="d-flex gap-3 mt-3 mt-lg-0">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="status-${student.id}" value="Present" checked>
              <label class="form-check-label text-success">Present</label>
            </div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="status-${student.id}" value="Absent">
              <label class="form-check-label text-danger">Absent</label>
            </div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="status-${student.id}" value="Late">
              <label class="form-check-label text-warning">Late</label>
            </div>
          </div>
        </div>
      `;
      attendanceContainer.appendChild(row);
    });
  }

  function fetchStudents() {
    const classSelect = document.getElementById('classSelect');
    const sectionSelect = document.getElementById('sectionSelect');
    const classValue = classSelect.value;
    const sectionValue = sectionSelect.value;

    fetch(`/api/students?class=${encodeURIComponent(classValue)}&section=${encodeURIComponent(sectionValue)}`)
      .then((response) => response.json())
      .then((data) => {
        renderAttendanceList(data);
      })
      .catch(() => {
        attendanceContainer.innerHTML = '<p class="text-danger">Failed to load students.</p>';
      });
  }

  function selectAll(status) {
    const inputs = attendanceContainer.querySelectorAll(`input[value="${status}"]`);
    inputs.forEach((input) => {
      input.checked = true;
    });
  }

  function submitAttendance() {
    const dateInput = document.getElementById('attendanceDate');
    const selectedDate = dateInput.value;
    if (!selectedDate) {
      showToast('Please select a date.', 'warning');
      return;
    }

    const records = {};
    const cards = attendanceContainer.querySelectorAll('.card');
    cards.forEach((card) => {
      const inputs = card.querySelectorAll('input[type="radio"]');
      inputs.forEach((input) => {
        if (input.checked) {
          const studentId = input.name.replace('status-', '');
          records[studentId] = input.value;
        }
      });
    });

    fetch('/api/attendance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: selectedDate, records: records })
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          showToast(data.error, 'danger');
          return;
        }
        showToast(`Attendance saved for ${data.saved} students.`, 'success');
      })
      .catch(() => showToast('Failed to submit attendance.', 'danger'));
  }

  if (loadBtn) {
    loadBtn.addEventListener('click', fetchStudents);
  }

  const presentAll = document.getElementById('selectAllPresent');
  const absentAll = document.getElementById('selectAllAbsent');
  if (presentAll) presentAll.addEventListener('click', () => selectAll('Present'));
  if (absentAll) absentAll.addEventListener('click', () => selectAll('Absent'));
  if (saveBtn) saveBtn.addEventListener('click', submitAttendance);
})();
