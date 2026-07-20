const state = {
  cv: null,
  canonical: null,
  selected: {},
  lastResult: null,
  activeTab: "cvResult",
  providers: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function toast(message, tone = "ok") {
  const box = $("#toast");
  box.textContent = message;
  box.className = `toast ${tone}`;
  box.hidden = false;
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => (box.hidden = true), 3800);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatInline(text) {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>");
}

function markdown(text) {
  const lines = String(text ?? "").split(/\r?\n/);
  let html = "";
  let inList = false;
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${formatInline(line.replace(/^[-*]\s+/, ""))}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<p>${formatInline(line)}</p>`;
    }
  }
  if (inList) html += "</ul>";
  return html || "<p>No content yet.</p>";
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    throw new Error("Local server is not responding. Start the app server and reload this page.");
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = (await response.json()).detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return response;
}

function setBusy(button, busy, label) {
  if (!button) return;
  if (busy) {
    button.dataset.label = button.textContent;
    button.textContent = label || "Working...";
    button.disabled = true;
  } else {
    button.textContent = button.dataset.label || button.textContent;
    button.disabled = false;
  }
}

function setCvExportEnabled(enabled) {
  [
    "#exportFullCvBtn",
    "#exportFilteredCvBtn",
    "#exportWebCvBtn",
  ].forEach((selector) => {
    const button = $(selector);
    if (button) button.disabled = !enabled;
  });
}

function useAiParser() {
  return $("input[name='parserMode']:checked")?.value !== "heuristic";
}

function selectedWorkMode() {
  return $("input[name='workMode']:checked")?.value || "Any";
}

function selectedCvExportFormats() {
  const formats = $$("input[name='cvExportFormat']:checked").map((input) => input.value);
  return formats.length ? formats : ["md"];
}

async function checkHealth() {
  try {
    const response = await api("/api/health");
    const data = await response.json();
    $("#statusTitle").textContent = data.llm_configured ? `${data.provider_label} ready` : "No LLM configured";
    $("#statusText").textContent = data.model || "Local server";
    $("#statusDot").classList.toggle("warn", !data.llm_configured);
    $("#statusDot").classList.remove("bad");
  } catch (error) {
    $("#statusTitle").textContent = "Disconnected";
    $("#statusText").textContent = error.message;
    $("#statusDot").classList.add("bad");
  }
}

async function loadProviders() {
  try {
    const response = await api("/api/providers");
    state.providers = await response.json();
    renderProviderForm();
  } catch (error) {
    toast(error.message, "bad");
  }
}

function renderProviderForm() {
  const select = $("#providerSelect");
  if (!state.providers || !select) return;
  select.innerHTML = Object.entries(state.providers.providers)
    .map(([key, provider]) => `<option value="${escapeHtml(key)}">${escapeHtml(provider.label)}</option>`)
    .join("");
  select.value = state.providers.active_provider;
  fillProviderFields(select.value);
}

function fillProviderFields(providerName) {
  const provider = state.providers?.providers?.[providerName];
  if (!provider) return;
  $("#providerModelInput").value = provider.model || "";
  $("#providerBaseUrlInput").value = provider.base_url || "";
  $("#providerKeyInput").value = "";
  $("#providerKeyInput").placeholder = provider.api_key_present ? provider.api_key_mask : "Paste API key";
  $("#providerKeyStatus").textContent = provider.api_key_present ? `Key: ${provider.api_key_mask}` : "No key loaded";
  $("#providerActiveStatus").textContent =
    providerName === state.providers.active_provider ? "Active engine" : "Available";
}

async function saveProvider(button, options = {}) {
  setBusy(button, true, options.clear ? "Clearing..." : "Saving...");
  try {
    const provider = $("#providerSelect").value;
    const payload = {
      active_provider: provider,
      provider,
      model: $("#providerModelInput").value.trim(),
      base_url: $("#providerBaseUrlInput").value.trim(),
      api_key: options.clear ? null : $("#providerKeyInput").value.trim() || null,
      clear_api_key: Boolean(options.clear),
    };
    const response = await api("/api/providers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.providers = await response.json();
    renderProviderForm();
    await checkHealth();
    toast(options.clear ? "API key cleared." : "AI engine saved.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

async function refreshProviderStatus(button) {
  setBusy(button, true, "Refreshing...");
  try {
    await loadProviders();
    await checkHealth();
    toast("AI engine status refreshed.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

async function testProvider(button) {
  setBusy(button, true, "Testing...");
  try {
    await saveProvider($("#saveProviderBtn"));
    const response = await api("/api/providers/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider: $("#providerSelect").value }),
    });
    const data = await response.json();
    toast(`${data.provider} connected: ${data.model}`);
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

async function fetchJobUrl(button) {
  const url = $("#jobUrlInput").value.trim();
  if (!url) {
    toast("Paste a job posting URL first.", "bad");
    return;
  }
  setBusy(button, true, "Fetching...");
  try {
    const response = await api("/api/fetch-job", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();
    if (data.job_text) $("#jobText").value = data.job_text;
    if (data.company && !$("#companyInput").value.trim()) $("#companyInput").value = data.company;
    if (data.position && !$("#positionInput").value.trim()) $("#positionInput").value = data.position;
    toast("Job posting imported.");
  } catch (error) {
    toast(`Could not fetch URL: ${error.message}`, "bad");
  } finally {
    setBusy(button, false);
  }
}

function initSelection(cv) {
  state.selected = {};
  for (const [section, value] of Object.entries(cv || {})) {
    if (Array.isArray(value)) state.selected[section] = value.map(() => true);
  }
}

function renderCv(cv, resetSelection = true) {
  state.cv = cv;
  if (resetSelection) initSelection(cv);
  const editor = $("#cvEditor");
  editor.classList.remove("empty-state");
  editor.innerHTML = "";

  for (const [section, value] of Object.entries(cv)) {
    if (section === "source_notes") continue;
    const card = document.createElement("section");
    card.className = "cv-card";
    card.innerHTML = `<h3>${title(section)}</h3>`;
    if (Array.isArray(value)) {
      value.forEach((item, index) => card.appendChild(renderArrayItem(section, item, index)));
    } else if (value && typeof value === "object") {
      for (const [key, fieldValue] of Object.entries(value)) card.appendChild(renderField(section, key, fieldValue));
    } else {
      card.appendChild(renderField(section, "value", value));
    }
    editor.appendChild(card);
  }
  renderSelectionSummary();
  setCvExportEnabled(true);
}

function renderCvSource(data) {
  const meta = $("#cvSourceMeta");
  if (!meta) return;
  if (!data?.source) {
    meta.hidden = true;
    return;
  }
  const parts = [
    `Source: ${data.source}`,
    data.text_pages ? `${data.text_pages} pages` : null,
    data.text_chars ? `${data.text_chars.toLocaleString()} characters` : null,
  ].filter(Boolean);
  meta.textContent = parts.join(" · ");
  meta.hidden = false;
}

function renderArrayItem(section, item, index) {
  const wrap = document.createElement("div");
  wrap.className = "item-card";
  const checked = state.selected[section]?.[index] !== false;
  wrap.innerHTML = `
    <label class="toggle-row">
      <span>${title(section)} ${index + 1}</span>
      <input type="checkbox" ${checked ? "checked" : ""} data-toggle-section="${section}" data-toggle-index="${index}" />
    </label>
  `;
  if (item && typeof item === "object") {
    for (const [key, value] of Object.entries(item)) wrap.appendChild(renderField(section, key, value, index));
  } else {
    wrap.appendChild(renderField(section, "value", item, index));
  }
  return wrap;
}

function renderField(section, key, value, index = null) {
  const label = document.createElement("label");
  label.className = "field";
  const isLong = String(value ?? "").length > 80 || key === "description" || key === "summary";
  label.innerHTML = `<span>${title(key)}</span>`;
  const input = document.createElement(isLong ? "textarea" : "input");
  if (isLong) input.rows = 4;
  input.value = Array.isArray(value) ? value.join("\n") : String(value ?? "");
  input.dataset.path = JSON.stringify({ section, key, index });
  input.addEventListener("input", updateCvField);
  label.appendChild(input);
  return label;
}

function updateCvField(event) {
  const { section, key, index } = JSON.parse(event.target.dataset.path);
  const value = event.target.value;
  if (index === null) {
    state.cv[section][key] = key === "links" ? value.split(/\n+/).filter(Boolean) : value;
  } else if (typeof state.cv[section][index] === "object") {
    state.cv[section][index][key] = value;
  } else {
    state.cv[section][index] = value;
  }
}

function title(value) {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function renderSelectionSummary() {
  if (!state.cv) {
    $("#selectionSummary").textContent = "No CV loaded yet.";
    return;
  }
  $("#selectionSummary").innerHTML = Object.entries(state.selected)
    .map(([section, flags]) => `<span>${title(section)}: <strong>${flags.filter(Boolean).length}/${flags.length}</strong></span>`)
    .join("");
}

function selectedCv() {
  const cv = {};
  for (const [section, value] of Object.entries(state.cv || {})) {
    cv[section] = Array.isArray(value)
      ? value.filter((_, index) => state.selected[section]?.[index] !== false)
      : value;
  }
  return cv;
}

async function loadSavedCv(button) {
  setBusy(button, true, "Loading...");
  try {
    const response = await api("/api/cv");
    const data = await response.json();
    renderCv(data.cv);
    try {
      const canonicalResponse = await api("/api/cv-canonical");
      const canonicalData = await canonicalResponse.json();
      state.canonical = canonicalData.canonical || null;
    } catch {
      state.canonical = null;
    }
    $("#exportWebCvBtn").disabled = !state.canonical;
    renderCvSource({ source: "Saved CV JSON" });
    toast("Saved CV loaded.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

async function uploadCv(file) {
  const form = new FormData();
  form.append("file", file);
  form.append("use_ai", useAiParser() ? "true" : "false");
  try {
    toast("Extracting and parsing CV...");
    const response = await api("/api/upload-cv", { method: "POST", body: form });
    const data = await response.json();
    state.canonical = data.canonical || null;
    renderCv(data.cv);
    renderCvSource(data);
    toast(data.parse_mode === "local_heuristic" ? "CV parsed locally without AI credits." : "CV uploaded and parsed.");
  } catch (error) {
    toast(error.message, "bad");
  }
}

function chooseCvFromPc() {
  $("#cvFile")?.click();
}

async function exportParsedCv(format, selectedOnly = false, button = null) {
  if (!state.cv) {
    toast("Parse or load a CV first.", "bad");
    return;
  }
  setBusy(button, true, "Exporting...");
  try {
    const payload = {
      cv: selectedOnly ? selectedCv() : state.cv,
      format,
      filename_prefix: selectedOnly ? "parsed_cv_selected_fields" : "parsed_cv_full",
    };
    const response = await api("/api/export-cv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const stamp = new Date().toISOString().slice(0, 10);
    a.href = url;
    a.download = `${payload.filename_prefix}_${stamp}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
    toast(selectedOnly ? "Selected CV fields exported." : "Parsed CV exported.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

async function exportParsedCvBatch(selectedOnly = false, button = null) {
  for (const format of selectedCvExportFormats()) {
    await exportParsedCv(format, selectedOnly, button);
  }
}

async function exportProfessionalWebCv(button) {
  if (!state.canonical) {
    toast("Import or open a parsed CV first.", "bad");
    return;
  }
  setBusy(button, true, "Rendering HTML...");
  try {
    const payload = {
      canonical: state.canonical,
      page_title: $("#webCvTitleInput").value.trim(),
      include_contact: $("#webCvContactOpt").checked,
      filename_prefix: "professional_web_cv",
    };
    const response = await api("/api/export-web-cv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `professional_web_cv_${new Date().toISOString().slice(0, 10)}.html`;
    a.click();
    URL.revokeObjectURL(url);
    toast("Professional HTML CV exported. Review it before publishing.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

function suggestByRole() {
  if (!state.cv) return;
  const role = selectedRole();
  const scientific = /scientific/i.test(role);
  const commercial = /commercial/i.test(role);
  for (const section of Object.keys(state.selected)) {
    state.selected[section] = state.selected[section].map((_, index) => {
      const item = JSON.stringify(state.cv[section][index]).toLowerCase();
      if (scientific && section === "experience") return !/(sales|account|proquinorte|commercial)/.test(item);
      if (commercial && (section === "publications" || section === "projects")) {
        return /(pagbiomics|sales|b2b|consult|diagnostic|industrial)/.test(item);
      }
      return true;
    });
  }
  renderCv(state.cv, false);
  toast(`Selection adjusted for ${role}.`);
}

function selectedRole() {
  return $("input[name='roleType']:checked")?.value || "Hybrid";
}

async function runMatch(button) {
  if (!state.cv) {
    toast("Load the CV first.", "bad");
    return;
  }
  const jobText = $("#jobText").value.trim();
  if (jobText.length < 40) {
    toast("Paste or fetch a fuller job description.", "bad");
    return;
  }
  setBusy(button, true, "Generating...");
  try {
    const payload = {
      job_text: jobText,
      role_type: `${selectedRole()} | Work mode: ${selectedWorkMode()}`,
      selected_cv: selectedCv(),
      job_url: $("#jobUrlInput").value.trim(),
      company: $("#companyInput").value.trim(),
      position: $("#positionInput").value.trim(),
    };
    const response = await api("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    state.lastResult = data.result;
    renderResults(data.result);
    loadHistory();
    toast(data.saved_markdown ? "Match generated and saved to exports." : "Match generated.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

function renderResults(result) {
  $("#resultShell").hidden = false;
  $("#cvResult").innerHTML = markdown(result.adapted_cv);
  $("#letterResult").innerHTML = markdown(result.cover_letter);
  $("#interviewResult").innerHTML = renderQuestions(result.interview_questions);
  $("#atsBadge").textContent = `ATS ${result.ats_score ?? "--"} · ${result.language || "EN"}`;
  setTab(state.activeTab);
}

function renderQuestions(questions) {
  if (typeof questions === "string") return markdown(questions);
  return (questions || [])
    .map((item, index) => `
      <section class="qa">
        <h3>${index + 1}. ${escapeHtml(item.question || "Interview question")}</h3>
        <p>${escapeHtml(item.answer || "")}</p>
      </section>
    `)
    .join("") || "<p>No questions yet.</p>";
}

function setTab(tabId) {
  state.activeTab = tabId;
  $$(".tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.tab === tabId));
  $$(".result-pane").forEach((pane) => pane.classList.toggle("is-active", pane.id === tabId));
}

function currentResultText() {
  if (!state.lastResult) return "";
  if (state.activeTab === "letterResult") return state.lastResult.cover_letter || "";
  if (state.activeTab === "interviewResult") {
    return typeof state.lastResult.interview_questions === "string"
      ? state.lastResult.interview_questions
      : JSON.stringify(state.lastResult.interview_questions, null, 2);
  }
  return state.lastResult.adapted_cv || "";
}

async function copyActive() {
  await navigator.clipboard.writeText(currentResultText());
  toast("Copied to clipboard.");
}

async function exportFile(format) {
  if (!state.lastResult) return;
  const response = await api("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...state.lastResult,
      company: $("#companyInput").value.trim(),
      position: $("#positionInput").value.trim(),
      format,
    }),
  });
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const stamp = new Date().toISOString().slice(0, 10);
  a.href = url;
  a.download = `job_application_${stamp}.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

async function loadHistory() {
  try {
    const response = await api("/api/history");
    const data = await response.json();
    const list = $("#historyList");
    if (!data.items.length) {
      list.className = "history-list empty-state";
      list.textContent = "No generated applications yet.";
      return;
    }
    list.className = "history-list";
    list.innerHTML = data.items.map((item) => `
      <article class="history-item">
        <div>
          <strong>${escapeHtml(item.position || "Untitled role")}</strong>
          <small>${escapeHtml(item.company || "Company not specified")} · ${escapeHtml(item.created_at)}</small>
          <p>${escapeHtml(item.job_excerpt)}</p>
        </div>
        <span>${item.ats_score ?? "--"}</span>
      </article>
    `).join("");
  } catch (error) {
    toast(error.message, "bad");
  }
}

async function openExportsFolder(button) {
  setBusy(button, true, "Opening...");
  try {
    await api("/api/open-exports");
    toast("Exports folder opened.");
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    setBusy(button, false);
  }
}

function wireEvents() {
  setCvExportEnabled(false);
  $("#chooseCvBtn").addEventListener("click", chooseCvFromPc);
  $("#loadSavedBtn").addEventListener("click", (event) => loadSavedCv(event.currentTarget));
  $("#providerSelect").addEventListener("change", (event) => fillProviderFields(event.target.value));
  $("#refreshProviderBtn").addEventListener("click", (event) => refreshProviderStatus(event.currentTarget));
  $("#clearProviderKeyBtn").addEventListener("click", (event) => saveProvider(event.currentTarget, { clear: true }));
  $("#saveProviderBtn").addEventListener("click", (event) => saveProvider(event.currentTarget));
  $("#testProviderBtn").addEventListener("click", (event) => testProvider(event.currentTarget));
  $("#fetchBtn").addEventListener("click", (event) => fetchJobUrl(event.currentTarget));
  $("#cvFile").addEventListener("change", (event) => {
    if (event.target.files?.[0]) uploadCv(event.target.files[0]);
  });
  $("#selectRelevantBtn").addEventListener("click", suggestByRole);
  $("#matchBtn").addEventListener("click", (event) => runMatch(event.currentTarget));
  $("#copyBtn").addEventListener("click", copyActive);
  $("#mdBtn").addEventListener("click", () => exportFile("md"));
  $("#docxBtn").addEventListener("click", () => exportFile("docx"));
  $("#pdfBtn").addEventListener("click", () => exportFile("pdf"));
  $("#exportFullCvBtn").addEventListener("click", (event) => exportParsedCvBatch(false, event.currentTarget));
  $("#exportFilteredCvBtn").addEventListener("click", (event) => exportParsedCvBatch(true, event.currentTarget));
  $("#exportWebCvBtn").addEventListener("click", (event) => exportProfessionalWebCv(event.currentTarget));
  $("#refreshHistoryBtn").addEventListener("click", loadHistory);
  $("#openExportsBtn").addEventListener("click", (event) => openExportsFolder(event.currentTarget));
  $("#toggleEditorBtn").addEventListener("click", () => $("#cvEditor").classList.toggle("is-collapsed"));
  $$(".tab").forEach((tab) => tab.addEventListener("click", () => setTab(tab.dataset.tab)));
  $$(".step").forEach((step) => {
    step.addEventListener("click", () => document.getElementById(step.dataset.jump).scrollIntoView({ behavior: "smooth" }));
  });
  document.addEventListener("change", (event) => {
    if (event.target.matches("[data-toggle-section]")) {
      const section = event.target.dataset.toggleSection;
      const index = Number(event.target.dataset.toggleIndex);
      state.selected[section][index] = event.target.checked;
      renderSelectionSummary();
    }
  });
}

wireEvents();
checkHealth();
loadProviders();
loadHistory();
