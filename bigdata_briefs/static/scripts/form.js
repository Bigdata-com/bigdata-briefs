document.getElementById('briefForm').onsubmit = async function (e) {
    e.preventDefault();
    const output = document.getElementById('output');
    const spinner = document.getElementById('spinner');
    const showJsonBtn = document.getElementById('showJsonBtn');
    const submitBtn = document.querySelector('button[type="submit"]');
    output.innerHTML = '';
    output.classList.remove('error');
    showJsonBtn.style.display = 'none';
    lastReport = null;

    // Disable the submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Waiting for response...';

    // Get companies and check if its available in the watchlists
    let companies = document.getElementById('companies_text').value.trim();
    const foundWatchlist = watchlists.find(w => w.name === companies);
    if (foundWatchlist) {
        companies = foundWatchlist.id;
    }
    else if (!companies) {
        output.innerHTML = `<span class="error">❌ Error: Company Universe is required.</span>`;
        output.classList.add('error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generrate Brief';
        return;
    }
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;

    const llm_model = document.getElementById('llm_model').value.trim();

    // Build request payload
    let payload = {
    };
    let topics = document.getElementById('topics').value.trim();
    if (topics) {
        let topicsArray;
        if (topics.includes('\n')) {
            topicsArray = topics.split('\n').map(t => t.trim()).filter(Boolean);
        } else {
            topicsArray = [topics];
        }

        // Validate that ALL topics contain the {company} placeholder
        const topicsWithoutPlaceholder = topicsArray.filter(topic => !topic.includes('{company}'));
        if (topicsWithoutPlaceholder.length > 0) {
            const failingTopicsList = topicsWithoutPlaceholder.map(topic => `• ${escapeHtml(topic)}`).join('<br>');
            output.innerHTML = `<span class="error">❌ Error: The following topics are missing the {company} placeholder:<br>${failingTopicsList}</span>`;
            output.classList.add('error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generrate Brief';
            return;
        }

        payload.topics = topicsArray;
    }
    const novelty = document.getElementById('novelty').value === 'true';
    let sources = document.getElementById('sources').value.trim();
    if (sources) {
        if (sources.includes(',')) {
            payload.sources = sources.split(',').map(s => s.trim()).filter(Boolean);
            // A single RP Entity ID
        }
        else {
            payload.sources = [sources];
        }
    }

    // A list of companies
    if (companies.includes(',')) {
        payload.companies = companies.split(',').map(s => s.trim()).filter(Boolean);
        // A single RP Entity ID
    } else if (companies.length === 6) {
        payload.companies = [companies];
        // A watchlist ID
    } else if (companies.length > 6) {
        payload.companies = companies;
    }

    if (start_date) payload.report_start_date = start_date;
    if (end_date) payload.report_end_date = end_date;
    if (novelty) payload.novelty = novelty;

    // Add token from URL param if present
    const params = new URLSearchParams();
    const token = getUrlParam('token');
    if (token) {
        params.append("token", token);
    }

    try {
        const response = await fetch(`/briefs/create?${params}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const data = await response.json();
        // Start polling status endpoint every 5 seconds using request_id
        if (data && data.request_id) {
            const requestId = data.request_id;
            let polling = true;
            const logViewer = document.getElementById('logViewer');
            async function pollStatus() {

                try {
                    const statusResp = await fetch(`/briefs/status/${requestId}?${params}`);
                    if (!statusResp.ok) {
                        throw new Error(`Status HTTP error ${statusResp.status}`);
                    }
                    const statusData = await statusResp.json();
                    spinner.style.display = 'block';
                    // Render logs if available
                    if (statusData.logs && Array.isArray(statusData.logs)) {
                        logViewer.innerHTML = statusData.logs.map(line => {
                            let base = 'mb-1';
                            let color = '';
                            if (line.toLowerCase().includes('error')) color = 'text-red-400';
                            else if (line.toLowerCase().includes('success')) color = 'text-green-400';
                            else if (line.toLowerCase().includes('info')) color = 'text-sky-400';
                            return `<div class='${base} ${color}'>${line}</div>`;
                        }).join('');
                        logViewer.scrollTop = logViewer.scrollHeight;
                    } else if (statusData.log) {
                        logViewer.textContent = statusData.log;
                    } else {
                        logViewer.textContent = 'No logs yet.';
                    }
                    // Stop polling if status is 'completed' or 'failed'
                    if (statusData.status === 'completed' || statusData.status === 'failed') {
                        polling = false;
                        if (statusData.status === 'completed') {
                            output.innerHTML = renderBriefReport(statusData.report)
                            showJsonBtn.style.display = 'inline-block';
                            lastReport = statusData.report;
                        }
                        spinner.style.display = 'none';
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Generrate Brief';
                        return;
                    }
                } catch (err) {
                    logViewer.innerHTML = `<div class=\"log-line log-error\">❌ Status Error: ${err.message}</div>`;
                }
                if (polling) {
                    setTimeout(pollStatus, 5000);
                }
            }
            pollStatus();
        }
    } catch (err) {
        output.innerHTML = `<span class="error">❌ Error: ${err.message}</span>`;
        output.classList.add('error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generrate Brief';
        spinner.style.display = 'none';
    }
};

document.getElementById('showJsonBtn').onclick = function () {
    if (lastReport) {
        document.getElementById('jsonContent').textContent = JSON.stringify(lastReport, null, 2);
        document.getElementById('jsonModal').style.display = 'block';
    }
};