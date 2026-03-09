const sampleText = `Title: Outcomes of early corticosteroid therapy in hospitalized patients with severe pneumonia

Abstract
Objective
This study evaluated whether early corticosteroid therapy improved respiratory outcomes and reduced mortality in adults hospitalized with severe pneumonia.

Methods
We conducted a retrospective cohort study including 312 patients admitted between January 2022 and December 2023. Patients receiving dexamethasone within 24 hours of admission were compared with matched controls. Primary outcomes included oxygen requirement at day 7, ICU transfer, and in-hospital mortality.

Results
Early corticosteroid therapy was associated with lower ICU transfer rates and shorter median duration of oxygen support. In-hospital mortality was 11.2% in the treatment group versus 16.8% in controls. Adverse hyperglycemia occurred more frequently in patients with diabetes. Multivariable analysis showed a significant association between early treatment and improved respiratory recovery.

Conclusion
Early corticosteroid therapy may improve short-term respiratory outcomes in selected patients with severe pneumonia, although careful glucose monitoring is required.`;

const textInput = document.getElementById('textInput');
const summarizeBtn = document.getElementById('summarizeBtn');
const sampleBtn = document.getElementById('sampleBtn');
const statusEl = document.getElementById('status');

function renderStructured(data) {
  const target = document.getElementById('structuredSummary');
  const entries = Object.entries(data || {});
  if (!entries.length) {
    target.textContent = 'No structured output yet.';
    target.classList.add('muted');
    return;
  }
  target.classList.remove('muted');
  target.innerHTML = entries.map(([k, v]) => `<div><strong>${k.replace(/_/g, ' ')}:</strong><br>${v}</div><br>`).join('');
}

function renderEvidence(items) {
  const target = document.getElementById('evidenceList');
  if (!items?.length) {
    target.textContent = 'No evidence yet.';
    target.classList.add('muted');
    return;
  }
  target.classList.remove('muted');
  target.innerHTML = items.map(item => `
    <div class="evidence-item">
      <div>${item.sentence}</div>
      <div class="small">Section: ${item.section} · Score: ${item.score}</div>
    </div>
  `).join('');
}

function renderEntities(items) {
  const target = document.getElementById('entityList');
  if (!items?.length) {
    target.textContent = 'No entities yet.';
    target.classList.add('muted');
    return;
  }
  target.classList.remove('muted');
  target.innerHTML = items.map(item => `<span class="pill">${item.text} · ${item.label}</span>`).join('');
}

async function summarize() {
  const text = textInput.value.trim();
  if (text.length < 50) {
    statusEl.textContent = 'Please paste at least 50 characters of biomedical text.';
    return;
  }
  statusEl.textContent = 'Summarizing...';
  summarizeBtn.disabled = true;
  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        target_sentences: Number(document.getElementById('targetSentences').value || 6),
        abstractive: document.getElementById('abstractive').checked
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    const finalSummary = document.getElementById('finalSummary');
    finalSummary.textContent = data.final_summary || 'No summary.';
    finalSummary.classList.remove('muted');
    renderStructured(data.structured_summary);
    renderEvidence(data.evidence);
    renderEntities(data.key_entities);
    statusEl.textContent = `Done. ${data.stats.summary_sentences} summary sentences generated.`;
  } catch (err) {
    statusEl.textContent = err.message;
  } finally {
    summarizeBtn.disabled = false;
  }
}

summarizeBtn.addEventListener('click', summarize);
sampleBtn.addEventListener('click', () => { textInput.value = sampleText; statusEl.textContent = 'Sample loaded.'; });
