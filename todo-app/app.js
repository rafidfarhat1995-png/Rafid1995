let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
let currentFilter = 'all';

// Show today's date
document.getElementById('today-date').textContent = new Date().toLocaleDateString('en-US', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Allow pressing Enter to add a task
document.getElementById('task-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') addTask();
});

function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

function addTask() {
  const input    = document.getElementById('task-input');
  const priority = document.getElementById('priority').value;
  const dueDate  = document.getElementById('due-date').value;
  const name     = input.value.trim();

  if (!name) {
    input.focus();
    return;
  }

  tasks.push({
    id: Date.now(),
    name,
    priority,
    dueDate,
    completed: false
  });

  input.value = '';
  document.getElementById('due-date').value = '';
  saveTasks();
  renderTasks();
}

function toggleTask(id) {
  tasks = tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
  saveTasks();
  renderTasks();
}

function deleteTask(id) {
  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  renderTasks();
}

function clearCompleted() {
  tasks = tasks.filter(t => !t.completed);
  saveTasks();
  renderTasks();
}

function filterTasks(filter, btn) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTasks();
}

function renderTasks() {
  const list = document.getElementById('task-list');
  list.innerHTML = '';

  let filtered = tasks;
  if (currentFilter === 'active')    filtered = tasks.filter(t => !t.completed);
  if (currentFilter === 'completed') filtered = tasks.filter(t => t.completed);

  if (filtered.length === 0) {
    list.innerHTML = '<p class="empty-msg">No tasks here!</p>';
  } else {
    filtered.forEach(task => {
      const li = document.createElement('li');
      li.className = `task-item ${task.priority} ${task.completed ? 'completed' : ''}`;
      li.innerHTML = `
        <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${task.id})" />
        <div class="task-info">
          <div class="task-name">${escapeHtml(task.name)}</div>
          <div class="task-meta">
            <span class="priority-badge ${task.priority}">${task.priority}</span>
            ${task.dueDate ? ' &nbsp; Due: ' + formatDate(task.dueDate) : ''}
          </div>
        </div>
        <button class="delete-btn" onclick="deleteTask(${task.id})">&#10005;</button>
      `;
      list.appendChild(li);
    });
  }

  const remaining = tasks.filter(t => !t.completed).length;
  document.getElementById('task-count').textContent =
    `${remaining} task${remaining !== 1 ? 's' : ''} remaining`;
}

function formatDate(dateStr) {
  const [y, m, d] = dateStr.split('-');
  return `${m}/${d}/${y}`;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// Initial render
renderTasks();
