// --- Student CRUD ---
async function fetchStudents() {
  const res = await fetch('/students/');
  const students = await res.json();
  const tbody = document.getElementById('studentsTable').querySelector('tbody');
  tbody.innerHTML = '';
  students.forEach(s => {
    const row = `<tr id="student-row-${s.id}">
      <td>${s.id}</td>
      <td id="student-name-${s.id}">${s.name}</td>
      <td id="student-email-${s.id}">${s.email}</td>
      <td>
        <button onclick="showUpdateForm(${s.id}, '${s.name}', '${s.email}')">Edit</button>
      </td>
    </tr>
    <tr id="update-form-row-${s.id}" style="display:none;">
      <td colspan="4">
        <form onsubmit="return updateStudent(event, ${s.id})">
          <input type="text" id="update-name-${s.id}" value="${s.name}" required>
          <input type="email" id="update-email-${s.id}" value="${s.email}" required>
          <button type="submit">Save</button>
          <button type="button" onclick="hideUpdateForm(${s.id})">Cancel</button>
          <span id="update-result-${s.id}" class="result"></span>
        </form>
      </td>
    </tr>`;
    tbody.innerHTML += row;
  });
}

window.showUpdateForm = function(id, name, email) {
  document.getElementById(`update-form-row-${id}`).style.display = '';
  document.getElementById(`student-row-${id}`).style.display = 'none';
};

window.hideUpdateForm = function(id) {
  document.getElementById(`update-form-row-${id}`).style.display = 'none';
  document.getElementById(`student-row-${id}`).style.display = '';
};

window.updateStudent = async function(event, id) {
  event.preventDefault();
  const name = document.getElementById(`update-name-${id}`).value;
  const email = document.getElementById(`update-email-${id}`).value;
  const res = await fetch(`/students/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ name, email })
  });
  const resultSpan = document.getElementById(`update-result-${id}`);
  if (res.ok) {
    resultSpan.textContent = 'Updated!';
    resultSpan.className = 'result';
    await fetchStudents();
    await fetchMatrix();
  } else {
    const err = await res.json();
    resultSpan.textContent = err.detail || 'Error';
    resultSpan.className = 'result error';
  }
  setTimeout(() => {
    hideUpdateForm(id);
  }, 1000);
  return false;
};

document.getElementById('studentForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = {
    name: document.getElementById('student_name').value,
    email: document.getElementById('student_email').value
  };
  const res = await fetch('/students/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const result = document.getElementById('studentResult');
  if (res.ok) {
    result.textContent = 'Student created!';
    result.className = 'result';
    fetchStudents();
    fetchMatrix();
  } else {
    const err = await res.json();
    result.textContent = err.detail || 'Error';
    result.className = 'result error';
  }
};

// --- Assignment CRUD ---
async function fetchAssignments() {
  const res = await fetch('/assignments/');
  const assignments = await res.json();
  const tbody = document.getElementById('assignmentsTable').querySelector('tbody');
  tbody.innerHTML = '';
  assignments.forEach(a => {
    const due = new Date(a.due_date).toLocaleString();
    const row = `<tr>
      <td>${a.id}</td>
      <td>${a.title}</td>
      <td>${a.description}</td>
      <td>${due}</td>
      <td>
        <button onclick="deleteAssignment(${a.id})">Delete</button>
      </td>
    </tr>`;
    tbody.innerHTML += row;
  });
}

async function deleteAssignment(id) {
  if (!confirm('Are you sure you want to delete this assignment?')) return;
  const res = await fetch(`/assignments/${id}`, { method: 'DELETE' });
  if (res.ok) {
    fetchAssignments();
    fetchMatrix();
  } else {
    alert('Failed to delete assignment');
  }
}

document.getElementById('assignmentForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = {
    title: document.getElementById('title').value,
    description: document.getElementById('description').value,
    due_date: document.getElementById('due_date').value
  };
  const res = await fetch('/assignments/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const result = document.getElementById('assignmentResult');
  if (res.ok) {
    result.textContent = 'Assignment created!';
    result.className = 'result';
    fetchAssignments();
    fetchMatrix();
  } else {
    result.textContent = 'Error';
    result.className = 'result error';
  }
};

// --- Student-Assignment Matrix ---
async function fetchMatrix() {
  const [studentsRes, assignmentsRes, submissionsRes] = await Promise.all([
    fetch('/students/'),
    fetch('/assignments/'),
    fetch('/submissions/')
  ]);
  const students = await studentsRes.json();
  const assignments = await assignmentsRes.json();
  const submissions = await submissionsRes.json();

  // Build header
  const headerRow = document.getElementById('matrixHeader');
  headerRow.innerHTML = '<th>Student</th><th>Email</th>';
  assignments.forEach(a => {
    headerRow.innerHTML += `<th>${a.title}</th>`;
  });

  // Build body
  const tbody = document.getElementById('matrixTable').querySelector('tbody');
  tbody.innerHTML = '';
  students.forEach(student => {
    let row = `<tr><td>${student.name}</td><td>${student.email}</td>`;
    assignments.forEach(assignment => {
      const submitted = submissions.some(
        s => s.student_id === student.id && s.assignment_id === assignment.id
      );
      row += `<td>
        <input type="checkbox" 
          data-student="${student.id}" 
          data-assignment="${assignment.id}" 
          ${submitted ? 'checked' : ''}>
      </td>`;
    });
    row += '</tr>';
    tbody.innerHTML += row;
  });

  // Add event listeners to checkboxes
  document.querySelectorAll('#matrixTable input[type="checkbox"]').forEach(cb => {
    cb.onchange = async function() {
      const student_id = this.getAttribute('data-student');
      const assignment_id = this.getAttribute('data-assignment');
      const url = `/submissions/?student_id=${student_id}&assignment_id=${assignment_id}`;
      const res = this.checked
        ? await fetch(url, { method: 'POST' })
        : await fetch(url, { method: 'DELETE' });
      if (!res.ok) {
        alert('Failed to update submission');
        this.checked = !this.checked;
      }
    };
  });
}

window.onload = function() {
  fetchStudents();
  fetchAssignments();
  fetchMatrix();
};