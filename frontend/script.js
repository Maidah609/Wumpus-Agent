const gridEl = document.getElementById("grid");
const statusText = document.getElementById("statusText");
const positionText = document.getElementById("positionText");
const perceptsText = document.getElementById("perceptsText");
const inferenceText = document.getElementById("inferenceText");
const visitedText = document.getElementById("visitedText");
const safeText = document.getElementById("safeText");
const unknownText = document.getElementById("unknownText");
const logList = document.getElementById("logList");

const rowsInput = document.getElementById("rows");
const colsInput = document.getElementById("cols");
const pitProbInput = document.getElementById("pitProbability");
const seedInput = document.getElementById("seed");
const revealTruthInput = document.getElementById("revealTruth");

const resetBtn = document.getElementById("resetBtn");
const stepBtn = document.getElementById("stepBtn");
const autoBtn = document.getElementById("autoBtn");
const autoAnimatedBtn = document.getElementById("autoAnimatedBtn");
let isAnimating = false;
let isBusy = false;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return response.json();
}

function renderGrid(state) {
  gridEl.style.gridTemplateColumns = `repeat(${state.cols}, 50px)`;
  gridEl.innerHTML = "";
  const revealTruth = revealTruthInput.checked;

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const status = state.grid[r][c];
      const cell = document.createElement("div");
      cell.className = `cell ${status}`;
      cell.textContent = `${r},${c}`;
      if (revealTruth) {
        if (state.truth_grid[r][c] === "pit") cell.classList.add("truth-pit");
        if (state.truth_grid[r][c] === "wumpus") cell.classList.add("truth-wumpus");
      }
      gridEl.appendChild(cell);
    }
  }
}

function renderDecisionLog(state) {
  logList.innerHTML = "";
  const logs = state.decision_log || [];
  const recent = logs.slice().reverse();
  for (const item of recent) {
    const div = document.createElement("div");
    div.className = "log-item";
    div.textContent = item;
    logList.appendChild(div);
  }
}

function perceptText(percepts) {
  const items = [];
  if (percepts.breeze) items.push("Breeze");
  if (percepts.stench) items.push("Stench");
  if (!items.length) return "None";
  return items.join(", ");
}

function updateDashboard(state) {
  const isFinished = !state.alive || state.won;
  let status = "Exploring";
  if (!state.alive) status = "Agent Died";
  if (state.won) status = "No Safe Move / Episode Complete";
  statusText.textContent = status;
  positionText.textContent = `(${state.position[0]}, ${state.position[1]})`;
  perceptsText.textContent = perceptText(state.percepts);
  inferenceText.textContent = state.inference_steps;
  visitedText.textContent = state.visited_count;
  safeText.textContent = state.safe_count;
  unknownText.textContent = state.unknown_count;
  stepBtn.disabled = isFinished || isBusy;
  autoBtn.disabled = isFinished || isAnimating || isBusy;
  autoAnimatedBtn.disabled = isFinished || isAnimating || isBusy;
}

function render(state) {
  renderGrid(state);
  updateDashboard(state);
  renderDecisionLog(state);
}

async function loadState() {
  const state = await api("/api/state");
  render(state);
}

async function runAction(action) {
  if (isBusy) return;
  isBusy = true;
  statusText.textContent = "Processing...";
  try {
    const state = await action();
    render(state);
  } catch (error) {
    statusText.textContent = "Request failed. Try again.";
    throw error;
  } finally {
    isBusy = false;
  }
}

resetBtn.addEventListener("click", async () => {
  await runAction(async () => {
    const payload = {
      rows: Number(rowsInput.value),
      cols: Number(colsInput.value),
      pitProbability: Number(pitProbInput.value),
      seed: seedInput.value === "" ? null : Number(seedInput.value),
    };
    return api("/api/reset", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  });
});

stepBtn.addEventListener("click", async () => {
  await runAction(async () => api("/api/step", { method: "POST", body: "{}" }));
});

autoBtn.addEventListener("click", async () => {
  await runAction(async () =>
    api("/api/auto", {
      method: "POST",
      body: JSON.stringify({ maxSteps: 25 }),
    }),
  );
});

autoAnimatedBtn.addEventListener("click", async () => {
  if (isAnimating || isBusy) return;
  isAnimating = true;
  isBusy = true;
  try {
    for (let i = 0; i < 25; i++) {
      statusText.textContent = "Processing...";
      const state = await api("/api/step", { method: "POST", body: "{}" });
      render(state);
      if (!state.alive || state.won) break;
      await new Promise((resolve) => setTimeout(resolve, 280));
    }
  } finally {
    isAnimating = false;
    isBusy = false;
    const state = await api("/api/state");
    render(state);
  }
});

revealTruthInput.addEventListener("change", async () => {
  await runAction(async () => api("/api/state"));
});

loadState().catch(() => {
  statusText.textContent = "Unable to connect to server.";
});
