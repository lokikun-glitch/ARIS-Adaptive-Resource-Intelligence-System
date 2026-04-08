/* app.js — ARIS frontend */

// ── Mobile sidebar toggle ────────────────────────────────────────────────
(function () {
  const hamburger = document.getElementById('hamburger');
  const sidebar   = document.getElementById('sidebar');
  const overlay   = document.getElementById('sidebar-overlay');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('visible');
  }
  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
  }

  hamburger.addEventListener('click', openSidebar);
  overlay.addEventListener('click', closeSidebar);

  // Close sidebar when a nav item is clicked on mobile
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      if (window.innerWidth <= 768) closeSidebar();
    });
  });
})();

// ── Navigation ─────────────────────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.panel;

    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById('panel-' + target).classList.add('active');
  });
});

// ── Helpers ─────────────────────────────────────────────────────────────────
function show(id)  { document.getElementById(id).classList.remove('hidden'); }
function hide(id)  { document.getElementById(id).classList.add('hidden'); }
function el(id)    { return document.getElementById(id); }
function setText(id, text) { el(id).textContent = text; }

function setLoading(btn, yes) {
  if (yes) {
    btn._origText = btn.innerHTML;
    btn.innerHTML = '<span class="loader"></span> Running…';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._origText;
    btn.disabled = false;
  }
}

function showError(containerId, errors) {
  const box = document.createElement('div');
  box.className = 'error-box';
  box.textContent = Array.isArray(errors) ? errors.join('\n') : errors;

  const container = el(containerId);
  // remove any previous error
  container.querySelectorAll('.error-box').forEach(e => e.remove());
  container.prepend(box);
}

function clearErrors(containerId) {
  el(containerId).querySelectorAll('.error-box').forEach(e => e.remove());
}

async function post(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function getRandom(url, textareaId) {
  const res = await fetch(url);
  const data = await res.json();
  if (data.text) el(textareaId).value = data.text;
}

function setChart(imgId, wrapId, b64) {
  if (b64) {
    el(imgId).src = 'data:image/png;base64,' + b64;
    show(wrapId);
  } else {
    hide(wrapId);
  }
}

function setSteps(codeId, wrapId, steps, show_steps) {
  if (show_steps && steps && steps.length) {
    el(codeId).textContent = steps.join('\n');
    show(wrapId);
  } else {
    hide(wrapId);
  }
}

// ── Algorithm Selector ──────────────────────────────────────────────────────
el('sel-run').addEventListener('click', async () => {
  const btn = el('sel-run');
  const desc = el('sel-input').value.trim();
  clearErrors('panel-selector');

  if (!desc) {
    showError('panel-selector', 'Please enter a problem description.');
    return;
  }

  setLoading(btn, true);
  try {
    const data = await post('/api/selector', { description: desc });
    const resultEl = el('sel-result');
    resultEl.innerHTML = '';

    if (!data.matched) {
      resultEl.innerHTML = `<div class="sel-alert fail">${data.message}</div>`;
    } else {
      const signals = (data.matched_signals || []).length
        ? `<div class="sel-result-item">
            <span class="sel-key">Signals</span>
            <span class="sel-val" style="font-family:var(--font-mono);font-size:12px;color:var(--text-muted)">${data.matched_signals.join(', ')}</span>
           </div>`
        : '';
      resultEl.innerHTML = `
        <div class="sel-alert success" style="margin-bottom:14px">
          Match found — <strong>${data.module}</strong>
        </div>
        <div class="sel-result-item">
          <span class="sel-key">Algorithm</span>
          <span class="sel-val">${data.algorithm}</span>
        </div>
        <div class="sel-result-item">
          <span class="sel-key">Complexity</span>
          <span class="sel-val">${data.complexity}</span>
        </div>
        <div class="sel-result-item">
          <span class="sel-key">Confidence</span>
          <span class="sel-val">${data.confidence}</span>
        </div>
        <div class="sel-result-item">
          <span class="sel-key">Reason</span>
          <span class="sel-val">${data.reason}</span>
        </div>
        ${signals}
      `;
    }
    show('sel-output');
  } catch {
    showError('panel-selector', 'Request failed. Is the server running?');
  } finally {
    setLoading(btn, false);
  }
});

// ── Cargo Optimization ──────────────────────────────────────────────────────
el('cargo-rand').addEventListener('click', () => getRandom('/api/cargo/random', 'cargo-items'));

el('cargo-run').addEventListener('click', async () => {
  const btn = el('cargo-run');
  clearErrors('panel-cargo');
  hide('cargo-output'); hide('cargo-chart'); hide('cargo-steps-out');

  setLoading(btn, true);
  try {
    const data = await post('/api/cargo', {
      items: el('cargo-items').value,
      capacity: parseFloat(el('cargo-cap').value),
    });

    if (data.error) {
      showError('panel-cargo', data.error);
      return;
    }

    const sel = data.selected;
    let lines = '  Name          Weight    Taken       Profit\n';
    lines += '  ' + '─'.repeat(50) + '\n';
    sel.forEach(s => {
      const frac = s.fraction === 1.0 ? '100%' : (s.fraction * 100).toFixed(1) + '%';
      lines += `  ${s.name.padEnd(12)}  ${String(s.weight).padEnd(8)}  ${frac.padEnd(10)}  ${s.profit_gained.toFixed(2)}\n`;
    });
    lines += '  ' + '─'.repeat(50) + '\n';
    lines += `  Total profit:  ${data.total_profit.toFixed(2)}\n`;
    lines += `  Exec time:     ${data.exec_time_ms.toFixed(4)} ms`;

    setText('cargo-result', lines);
    show('cargo-output');
    setChart('cargo-chart-img', 'cargo-chart', data.chart);
    setSteps('cargo-steps-code', 'cargo-steps-out', data.steps, el('cargo-steps').checked);

  } catch {
    showError('panel-cargo', 'Request failed. Is the server running?');
  } finally {
    setLoading(btn, false);
  }
});

// ── Job Scheduling ──────────────────────────────────────────────────────────
el('sched-rand').addEventListener('click', () => getRandom('/api/scheduling/random', 'sched-jobs'));

el('sched-run').addEventListener('click', async () => {
  const btn = el('sched-run');
  clearErrors('panel-scheduling');
  hide('sched-output'); hide('sched-chart'); hide('sched-steps-out');

  setLoading(btn, true);
  try {
    const data = await post('/api/scheduling', { jobs: el('sched-jobs').value });

    if (data.error) {
      showError('panel-scheduling', data.error);
      return;
    }

    const sel = data.selected;
    let lines = '  Name       Start   End\n';
    lines += '  ' + '─'.repeat(28) + '\n';
    sel.forEach(j => {
      lines += `  ${j.name.padEnd(9)}  ${String(j.start).padEnd(6)}  ${j.end}\n`;
    });
    lines += '  ' + '─'.repeat(28) + '\n';
    lines += `  Total selected:  ${data.total_selected}\n`;
    lines += `  Exec time:       ${data.exec_time_ms.toFixed(4)} ms`;

    setText('sched-result', lines);
    show('sched-output');
    setChart('sched-chart-img', 'sched-chart', data.chart);
    setSteps('sched-steps-code', 'sched-steps-out', data.steps, el('sched-steps').checked);

  } catch {
    showError('panel-scheduling', 'Request failed. Is the server running?');
  } finally {
    setLoading(btn, false);
  }
});

// ── Network Optimization ────────────────────────────────────────────────────
el('net-rand').addEventListener('click', () => getRandom('/api/network/random', 'net-graph'));

el('net-run').addEventListener('click', async () => {
  const btn = el('net-run');
  clearErrors('panel-network');
  hide('net-output'); hide('net-chart'); hide('net-steps-out');

  setLoading(btn, true);
  try {
    const data = await post('/api/network', { graph: el('net-graph').value });

    if (data.error) {
      showError('panel-network', data.error);
      return;
    }

    const mst = data.mst_edges;
    let lines = '  Edge           Weight\n';
    lines += '  ' + '─'.repeat(24) + '\n';
    mst.forEach(e => {
      const edge = `${e.u} ─── ${e.v}`;
      lines += `  ${edge.padEnd(14)}  ${e.weight}\n`;
    });
    lines += '  ' + '─'.repeat(24) + '\n';
    lines += `  Total weight:  ${data.total_weight}\n`;
    lines += `  Exec time:     ${data.exec_time_ms.toFixed(4)} ms`;

    setText('net-result', lines);
    show('net-output');
    setChart('net-chart-img', 'net-chart', data.chart);
    setSteps('net-steps-code', 'net-steps-out', data.steps, el('net-steps').checked);

  } catch {
    showError('panel-network', 'Request failed. Is the server running?');
  } finally {
    setLoading(btn, false);
  }
});

// ── Conflict Resolution ─────────────────────────────────────────────────────
el('conf-rand').addEventListener('click', () => getRandom('/api/conflict/random', 'conf-graph'));

el('conf-run').addEventListener('click', async () => {
  const btn = el('conf-run');
  clearErrors('panel-conflict');
  hide('conf-output'); hide('conf-chart'); hide('conf-steps-out');

  setLoading(btn, true);
  try {
    const data = await post('/api/conflict', {
      graph: el('conf-graph').value,
      max_colors: parseInt(el('conf-colors').value),
    });

    if (data.error) {
      showError('panel-conflict', data.error);
      return;
    }

    let lines = '';
    if (!data.success) {
      lines = 'No valid coloring found with the given max colors.\n';
    } else {
      lines = '  Node       Color\n';
      lines += '  ' + '─'.repeat(20) + '\n';
      Object.entries(data.coloring).forEach(([node, color]) => {
        lines += `  ${node.padEnd(10)} Color ${color}\n`;
      });
      lines += '  ' + '─'.repeat(20) + '\n';
      lines += `  Colors used:  ${data.colors_used}\n`;
    }
    lines += `  Exec time:    ${data.exec_time_ms.toFixed(4)} ms`;

    setText('conf-result', lines);
    show('conf-output');
    setChart('conf-chart-img', 'conf-chart', data.chart);
    setSteps('conf-steps-code', 'conf-steps-out', data.steps, el('conf-steps').checked);

  } catch {
    showError('panel-conflict', 'Request failed. Is the server running?');
  } finally {
    setLoading(btn, false);
  }
});
