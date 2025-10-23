const form = document.getElementById('analyze-form');
const topicInput = document.getElementById('topic');
const statusEl = document.getElementById('status');
const results = document.getElementById('results');
const summaryEl = document.getElementById('summary');
const analysisEl = document.getElementById('analysis');
const sourcesEl = document.getElementById('sources');



// Resets the UI to a loading state, clearing old results.

function resetUI() {
  statusEl.hidden = false;
  results.hidden = true;
  summaryEl.textContent = '';
  analysisEl.textContent = '';
  sourcesEl.innerHTML = '';
}

/**
 * Sends the topic to the backend API for analysis.
 * @param {string} topic The topic to analyze.
 * @returns {Promise<object>} The analysis data from the API.
 */
async function analyzeTopic(topic) {
  const response = await fetch('/api/analyze', 
    {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ topic })
    }
  );

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Unknown error during analysis');
  }
  return data;
}

function renderAnalysis(analysis){
    if (analysis) {
      // Replace markdown bold with HTML strong tags
      let formattedAnalysis = analysis.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Split by newlines and wrap each part in a paragraph tag
      analysisEl.innerHTML = formattedAnalysis.split('\n').filter(p => p.trim() !== '').map(p => `<p class="para_analysis">${p}</p>`).join('');
    } else {
      analysisEl.textContent = '(no analysis)';
    }
}


form.addEventListener('submit', async (e) => {
  e.preventDefault();  // stops the browser's default behavior for a form submission, which is to reload the page.
  const topic = topicInput.value.trim();
  if (!topic) return;

  resetUI();

  try {
    const data = await analyzeTopic(topic);

    summaryEl.textContent = data.summary || '(no summary)';

    renderAnalysis(data.analysis);

    if (data.sources) {
      const sourceItem = document.createElement('li');
      sourceItem.textContent = data.sources;
      sourcesEl.appendChild(sourceItem);
    }
   
    results.hidden = false;
  }
  catch (err) {
    alert(`Failed to analyze: ${err.message}`);
  }
  finally {
    statusEl.hidden = true;
  }
});
