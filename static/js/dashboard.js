// Dashboard JavaScript

let currentPage = 1;
let currentTab = 'all-emails';
let currentStatus = null;
let selectedEmails = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    initializeEventListeners();
    loadStats();
    loadEmails();
    updateTimestamp();
    setInterval(loadStats, 5000); // Refresh stats every 5 seconds
    setInterval(updateTimestamp, 1000); // Update timestamp every second
});

// Event Listeners
function initializeEventListeners() {
    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => handleTabClick(btn));
    });

    // Bind controls for the default tab
    bindTabControls('all-emails');
    
    // Initialize user menu
    initializeUserMenu();
}

function getTabDomIds(tabName) {
    if (tabName === 'all-emails') {
        return {
            searchInputId: 'searchInput',
            refreshBtnId: 'refreshBtn',
            selectAllId: 'selectAllCheckbox',
            tbodyId: 'emailsTableBody',
            paginationId: 'pagination',
            bulkSentId: 'bulkMarkSentBtn',
            bulkDeleteId: 'bulkDeleteBtn'
        };
    }

    return {
        searchInputId: `searchInput-${tabName}`,
        refreshBtnId: `refreshBtn-${tabName}`,
        selectAllId: `selectAllCheckbox-${tabName}`,
        tbodyId: `emailsTableBody-${tabName}`,
        paginationId: `pagination-${tabName}`,
        bulkSentId: `bulkMarkSentBtn-${tabName}`,
        bulkDeleteId: `bulkDeleteBtn-${tabName}`
    };
}

function bindTabControls(tabName) {
    const ids = getTabDomIds(tabName);
    const searchInput = document.getElementById(ids.searchInputId);
    const refreshBtn = document.getElementById(ids.refreshBtnId);
    const selectAll = document.getElementById(ids.selectAllId);
    const bulkSent = document.getElementById(ids.bulkSentId);
    const bulkDelete = document.getElementById(ids.bulkDeleteId);

    if (searchInput && !searchInput.dataset.bound) {
        searchInput.addEventListener('keyup', () => {
            currentPage = 1;
            loadEmails();
        });
        searchInput.dataset.bound = 'true';
    }

    if (refreshBtn && !refreshBtn.dataset.bound) {
        refreshBtn.addEventListener('click', () => {
            currentPage = 1;
            loadEmails();
        });
        refreshBtn.dataset.bound = 'true';
    }

    if (selectAll && !selectAll.dataset.bound) {
        selectAll.addEventListener('change', (e) => {
            const tabContainer = document.getElementById(`tab-${tabName}`);
            if (tabContainer) {
                tabContainer.querySelectorAll('tbody input[type="checkbox"]').forEach(cb => {
                    cb.checked = e.target.checked;
                });
            }
            updateSelectedEmails();
        });
        selectAll.dataset.bound = 'true';
    }

    if (bulkSent && !bulkSent.dataset.bound) {
        bulkSent.addEventListener('click', () => {
            if (selectedEmails.length > 0) {
                bulkUpdateStatus('sent');
            }
        });
        bulkSent.dataset.bound = 'true';
    }

    if (bulkDelete && !bulkDelete.dataset.bound) {
        bulkDelete.addEventListener('click', () => {
            if (selectedEmails.length > 0 && confirm(`Delete ${selectedEmails.length} emails?`)) {
                bulkDeleteEmails();
            }
        });
        bulkDelete.dataset.bound = 'true';
    }
}

// Tab Handling
function baseHandleTabClick(btn) {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Update active tab content
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
    
    const tabName = btn.getAttribute('data-tab');
    currentTab = tabName;
    
    if (tabName === 'all-emails') {
        currentStatus = null;
    } else {
        currentStatus = tabName;
    }
    
    currentPage = 1;
    
    // Show tab content
    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
        if (tabContent.innerHTML === '') {
            renderEmailsTable(tabContent);
        }
        bindTabControls(tabName);
    }

    loadEmails();
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success && data.overall) {
            const overall = data.overall || {};
            const today = data.today || {};

            // Update stat cards with safe defaults
            document.getElementById('totalEmails').textContent = overall.total || 0;
            document.getElementById('pendingEmails').textContent = overall.pending || 0;
            document.getElementById('sentEmails').textContent = today.sent || 0;
            document.getElementById('failedEmails').textContent = (parseInt(overall.failed) || 0) + (parseInt(overall.bounced) || 0);
            document.getElementById('bouncedEmails').textContent = overall.bounced || 0;

            // Update status indicator
            updateStatusIndicator(true);
        } else {
            // Set defaults if no data
            document.getElementById('totalEmails').textContent = 0;
            document.getElementById('pendingEmails').textContent = 0;
            document.getElementById('sentEmails').textContent = 0;
            document.getElementById('failedEmails').textContent = 0;
            document.getElementById('bouncedEmails').textContent = 0;
            updateStatusIndicator(false);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        updateStatusIndicator(false);
    }
}

// Load Emails
async function loadEmails() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            limit: 50
        });

        if (currentStatus) {
            params.append('status', currentStatus);
        }

        const response = await fetch(`/api/emails?${params}`);
        const data = await response.json();

        if (data.success) {
            renderEmails(data.emails, currentTab);
            renderPagination(data.pages, currentPage, currentTab);
        }
    } catch (error) {
        console.error('Error loading emails:', error);
    }
}

// Render Emails Table
function renderEmails(emails, tabName) {
    const ids = getTabDomIds(tabName);
    const tbody = document.getElementById(ids.tbodyId);
    if (!tbody) return;
    
    if (emails.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No emails found</td></tr>';
        return;
    }

    tbody.innerHTML = emails.map(email => `
        <tr>
            <td>
                <input type="checkbox" class="email-checkbox" value="${email.id}" onchange="updateSelectedEmails()">
            </td>
            <td>${email.id}</td>
            <td>${truncate(email.recipient, 30)}</td>
            <td>${truncate(email.subject, 40)}</td>
            <td>
                <span class="status-badge status-${email.status}">
                    ${email.status}
                </span>
            </td>
            <td>${formatDate(email.sent_at)}</td>
            <td>${formatDate(email.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewEmailDetails(${email.id})">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');

    // Update selected emails visibility
    updateBulkActionButtons();
}

// Render Emails Table Structure
function renderEmailsTable(container) {
    container.innerHTML = `
        <div class="emails-header">
            <div class="filter-group">
                <input type="text" id="searchInput-${currentTab}" placeholder="Search emails..." class="search-box">
                <button class="btn btn-secondary" id="refreshBtn-${currentTab}">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
            <div class="action-group">
                <button class="btn btn-success" id="bulkMarkSentBtn-${currentTab}" style="display:none;">
                    <i class="fas fa-check"></i> Mark Selected as Sent
                </button>
                <button class="btn btn-danger" id="bulkDeleteBtn-${currentTab}" style="display:none;">
                    <i class="fas fa-trash"></i> Delete Selected
                </button>
            </div>
        </div>

        <div class="emails-table-wrapper">
            <table class="emails-table">
                <thead>
                    <tr>
                        <th><input type="checkbox" id="selectAllCheckbox-${currentTab}"></th>
                        <th>ID</th>
                        <th>Recipient</th>
                        <th>Subject</th>
                        <th>Status</th>
                        <th>Sent</th>
                        <th>Created</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="emailsTableBody-${currentTab}">
                    <tr><td colspan="8" class="text-center">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div class="pagination" id="pagination-${currentTab}"></div>
    `;

    bindTabControls(currentTab);
}

// Render Pagination
function renderPagination(pages, current, tabName) {
    const ids = getTabDomIds(tabName);
    const pagination = document.getElementById(ids.paginationId);
    if (!pagination) return;

    let html = '';

    if (current > 1) {
        html += `<button onclick="goToPage(1)">First</button>`;
        html += `<button onclick="goToPage(${current - 1})">Previous</button>`;
    }

    for (let i = Math.max(1, current - 2); i <= Math.min(pages, current + 2); i++) {
        html += `<button onclick="goToPage(${i})" class="${i === current ? 'active' : ''}">${i}</button>`;
    }

    if (current < pages) {
        html += `<button onclick="goToPage(${current + 1})">Next</button>`;
        html += `<button onclick="goToPage(${pages})">Last</button>`;
    }

    pagination.innerHTML = html;
}

// Go to Page
function goToPage(page) {
    currentPage = page;
    loadEmails();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// View Email Details
async function viewEmailDetails(emailId) {
    try {
        const response = await fetch(`/api/email/${emailId}`);
        const data = await response.json();

        if (data.success) {
            const email = data.email;
            const modalBody = document.getElementById('emailModalBody');

            modalBody.innerHTML = `
                <div class="detail-row">
                    <span class="detail-label">ID:</span>
                    <span class="detail-value">${email.id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Recipient:</span>
                    <span class="detail-value">${email.recipient}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Subject:</span>
                    <span class="detail-value">${email.subject}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">
                        <span class="status-badge status-${email.status}">${email.status}</span>
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Body:</span>
                    <span class="detail-value" style="max-height: 200px; overflow-y: auto;">${escapeHtml(email.body)}</span>
                </div>
                ${email.error_message ? `
                <div class="detail-row">
                    <span class="detail-label">Error:</span>
                    <span class="detail-value error">${escapeHtml(email.error_message)}</span>
                </div>
                ` : ''}
                <div class="detail-row">
                    <span class="detail-label">Created:</span>
                    <span class="detail-value">${formatDate(email.created_at)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Sent:</span>
                    <span class="detail-value">${formatDate(email.sent_at) || 'Not sent'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Updated:</span>
                    <span class="detail-value">${formatDate(email.updated_at)}</span>
                </div>
                <div style="margin-top: 1.5rem; display: flex; gap: 0.75rem;">
                    <button class="btn btn-success" onclick="updateEmailStatus(${email.id}, 'sent')">
                        <i class="fas fa-check"></i> Mark as Sent
                    </button>
                    <button class="btn btn-danger" onclick="updateEmailStatus(${email.id}, 'failed')">
                        <i class="fas fa-times"></i> Mark as Failed
                    </button>
                    <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                </div>
            `;

            document.getElementById('emailModal').classList.add('active');
        }
    } catch (error) {
        console.error('Error loading email details:', error);
        alert('Failed to load email details');
    }
}

// Update Email Status
async function updateEmailStatus(emailId, status) {
    try {
        const response = await fetch(`/api/email/${emailId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });

        const data = await response.json();

        if (data.success) {
            alert('Email status updated');
            closeModal();
            loadEmails();
            loadStats();
        } else {
            alert('Failed to update status');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Error updating status');
    }
}

// Update Selected Emails
function updateSelectedEmails() {
    const tabContainer = document.getElementById(`tab-${currentTab}`);
    if (!tabContainer) {
        selectedEmails = [];
        updateBulkActionButtons();
        return;
    }
    selectedEmails = Array.from(tabContainer.querySelectorAll('.email-checkbox:checked')).map(cb => parseInt(cb.value));
    updateBulkActionButtons();
}

// Update Bulk Action Buttons
function updateBulkActionButtons() {
    const ids = getTabDomIds(currentTab);
    const markSentBtn = document.getElementById(ids.bulkSentId);
    const deleteBtn = document.getElementById(ids.bulkDeleteId);

    if (!markSentBtn || !deleteBtn) return;

    if (selectedEmails.length > 0) {
        markSentBtn.style.display = 'inline-flex';
        deleteBtn.style.display = 'inline-flex';
    } else {
        markSentBtn.style.display = 'none';
        deleteBtn.style.display = 'none';
    }
}

// Bulk Update Status
async function bulkUpdateStatus(status) {
    if (selectedEmails.length === 0) return;

    try {
        const response = await fetch('/api/emails/bulk-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email_ids: selectedEmails, status })
        });

        const data = await response.json();

        if (data.success) {
            alert(`${selectedEmails.length} emails marked as ${status}`);
            loadEmails();
            loadStats();
            selectedEmails = [];
            updateBulkActionButtons();
        } else {
            alert('Failed to update emails');
        }
    } catch (error) {
        console.error('Error bulk updating:', error);
        alert('Error updating emails');
    }
}

// Bulk Delete Emails
async function bulkDeleteEmails() {
    if (selectedEmails.length === 0) return;

    try {
        for (const emailId of selectedEmails) {
            await fetch(`/api/email/${emailId}`, { method: 'DELETE' });
        }

        alert(`${selectedEmails.length} emails deleted`);
        loadEmails();
        loadStats();
        selectedEmails = [];
        updateBulkActionButtons();
    } catch (error) {
        console.error('Error deleting emails:', error);
        alert('Error deleting emails');
    }
}

// Close Modal
function closeModal() {
    document.getElementById('emailModal').classList.remove('active');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('emailModal');
    if (e.target === modal) {
        closeModal();
    }
});

// Update Status Indicator
function updateStatusIndicator(connected) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.dot');

    if (connected) {
        dot.style.backgroundColor = '#10b981';
        indicator.querySelector('span:last-child').textContent = 'Connected';
    } else {
        dot.style.backgroundColor = '#ef4444';
        indicator.querySelector('span:last-child').textContent = 'Disconnected';
    }
}

// Update Timestamp
function updateTimestamp() {
    const now = new Date();
    const timestamp = now.toLocaleTimeString();
    document.getElementById('timestamp').textContent = timestamp;
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Settings Management
async function loadSettings() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();

        if (data.success) {
            const config = data.config;
            document.getElementById('batchSize').value = config.batch_size;
            document.getElementById('dailyLimit').value = config.daily_limit;
            document.getElementById('batchDelay').value = config.batch_delay;
            document.getElementById('smtpHost').textContent = config.smtp_host;
            document.getElementById('smtpPort').textContent = config.smtp_port;
            document.getElementById('fromEmail').textContent = config.from_email;
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    try {
        const saveBtn = document.getElementById('saveSettingsBtn');
        const resultBox = document.getElementById('settingsResult');
        
        saveBtn.classList.add('loading');
        saveBtn.disabled = true;

        const config = {
            batch_size: parseInt(document.getElementById('batchSize').value),
            daily_limit: parseInt(document.getElementById('dailyLimit').value),
            batch_delay: parseInt(document.getElementById('batchDelay').value)
        };

        const response = await fetch('/api/config', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        resultBox.style.display = 'block';
        if (data.success) {
            resultBox.className = 'result-box success';
            resultBox.textContent = '✓ ' + data.message;
        } else {
            resultBox.className = 'result-box error';
            resultBox.textContent = '✗ Error: ' + data.error;
        }

        saveBtn.classList.remove('loading');
        saveBtn.disabled = false;

    } catch (error) {
        console.error('Error saving settings:', error);
        const resultBox = document.getElementById('settingsResult');
        resultBox.style.display = 'block';
        resultBox.className = 'result-box error';
        resultBox.textContent = '✗ Error: ' + error.message;
        
        document.getElementById('saveSettingsBtn').classList.remove('loading');
        document.getElementById('saveSettingsBtn').disabled = false;
    }
}

// Send Now Functionality
async function sendEmailsNow() {
    try {
        const sendBtn = document.getElementById('sendNowBtn');
        const resultBox = document.getElementById('sendNowResult');
        const limit = parseInt(document.getElementById('sendNowLimit').value);

        if (!limit || limit < 1) {
            alert('Please enter a valid number of emails to send');
            return;
        }

        if (!confirm(`Send ${limit} pending emails now?`)) {
            return;
        }

        sendBtn.classList.add('loading');
        sendBtn.disabled = true;
        resultBox.style.display = 'none';

        const response = await fetch('/api/send-now', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limit })
        });

        const data = await response.json();

        resultBox.style.display = 'block';
        if (data.success) {
            resultBox.className = 'result-box success';
            resultBox.textContent = '✓ ' + data.message + '\n\n' + (data.output || '');
            
            // Refresh stats after sending
            setTimeout(() => {
                loadStats();
                loadEmails();
            }, 1000);
        } else {
            resultBox.className = 'result-box error';
            resultBox.textContent = '✗ Error: ' + (data.error || 'Failed to send emails');
        }

        sendBtn.classList.remove('loading');
        sendBtn.disabled = false;

    } catch (error) {
        console.error('Error sending emails:', error);
        const resultBox = document.getElementById('sendNowResult');
        resultBox.style.display = 'block';
        resultBox.className = 'result-box error';
        resultBox.textContent = '✗ Error: ' + error.message;
        
        document.getElementById('sendNowBtn').classList.remove('loading');
        document.getElementById('sendNowBtn').disabled = false;
    }
}

// Enhanced Tab Handling
function handleTabClick(btn) {
    const tabName = btn.getAttribute('data-tab');
    
    // Handle special tabs
    if (tabName === 'settings') {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-settings').classList.add('active');
        
        // Load settings
        loadSettings();
        return;
    }
    
    if (tabName === 'send-now') {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-send-now').classList.add('active');
        return;
    }
    
    if (tabName === 'validation') {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-validation').classList.add('active');
        
        // Load validation stats
        loadValidationStats();
        return;
    }
    
    if (tabName === 'templates') {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-templates').classList.add('active');
        
        // Load templates
        loadTemplates();
        return;
    }
    
    if (tabName === 'scheduler') {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-scheduler').classList.add('active');
        
        // Load schedules and templates for dropdown
        loadSchedules();
        loadScheduleTemplates();
        return;
    }
    
    // Use original handler for email list tabs
    baseHandleTabClick(btn);
}

// Test SMTP Functionality
async function testSMTP() {
    try {
        const testBtn = document.getElementById('testSmtpBtn');
        const resultBox = document.getElementById('smtpTestResult');
        const testEmail = document.getElementById('testEmail').value.trim();

        testBtn.classList.add('loading');
        testBtn.disabled = true;
        resultBox.style.display = 'none';

        const requestBody = testEmail ? { test_email: testEmail } : {};

        const response = await fetch('/api/test-smtp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        resultBox.style.display = 'block';
        if (data.success) {
            resultBox.className = 'result-box success';
            let message = data.message;
            
            if (data.details) {
                message += '\n\nConnection Test: ' + (data.details.connection ? '✓ Passed' : '✗ Failed');
                if (testEmail) {
                    message += '\nEmail Send Test: ' + (data.details.send ? '✓ Passed' : '✗ Failed');
                }
                message += '\n\nSMTP Configuration:';
                message += '\n  Host: ' + data.details.smtp_host;
                message += '\n  Port: ' + data.details.smtp_port;
                message += '\n  From: ' + data.details.from_email;
            }
            
            resultBox.textContent = message;
        } else {
            resultBox.className = 'result-box error';
            let message = data.error;
            
            if (data.details) {
                message += '\n\nConnection Test: ' + (data.details.connection ? '✓ Passed' : '✗ Failed');
                if (testEmail && data.details.connection) {
                    message += '\nEmail Send Test: ' + (data.details.send ? '✓ Passed' : '✗ Failed');
                }
            }
            
            resultBox.textContent = message;
        }

        testBtn.classList.remove('loading');
        testBtn.disabled = false;

    } catch (error) {
        console.error('Error testing SMTP:', error);
        const resultBox = document.getElementById('smtpTestResult');
        resultBox.style.display = 'block';
        resultBox.className = 'result-box error';
        resultBox.textContent = '✗ Error: ' + error.message;
        
        document.getElementById('testSmtpBtn').classList.remove('loading');
        document.getElementById('testSmtpBtn').disabled = false;
    }
}

// Enhanced initialization
document.addEventListener('DOMContentLoaded', function() {
    // Settings button listeners
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
    
    const reloadSettingsBtn = document.getElementById('reloadSettingsBtn');
    if (reloadSettingsBtn) {
        reloadSettingsBtn.addEventListener('click', loadSettings);
    }
    
    // Send now button listener
    const sendNowBtn = document.getElementById('sendNowBtn');
    if (sendNowBtn) {
        sendNowBtn.addEventListener('click', sendEmailsNow);
    }
    
    // Test SMTP button listener
    const testSmtpBtn = document.getElementById('testSmtpBtn');
    if (testSmtpBtn) {
        testSmtpBtn.addEventListener('click', testSMTP);
    }
    
    // Validation button listeners
    const startValidationBtn = document.getElementById('startValidationBtn');
    if (startValidationBtn) {
        startValidationBtn.addEventListener('click', startValidation);
    }
    
    const refreshValidationStatsBtn = document.getElementById('refreshValidationStatsBtn');
    if (refreshValidationStatsBtn) {
        refreshValidationStatsBtn.addEventListener('click', loadValidationStats);
    }
    
    // Load validation stats when validation tab is opened
    loadValidationStats();
});

// VALIDATION FUNCTIONS
async function loadValidationStats() {
    try {
        const response = await fetch('/api/validation/stats');
        const data = await response.json();
        
        if (data.success && data.stats) {
            const stats = data.stats;
            document.getElementById('valTotalEmails').textContent = stats.total || 0;
            document.getElementById('valUnchecked').textContent = stats.unchecked || 0;
            document.getElementById('valValid').textContent = stats.valid || 0;
            document.getElementById('valInvalid').textContent = stats.invalid || 0;
            document.getElementById('valNeedsReview').textContent = stats.needs_review || 0;
        }
        
        // Load validation results table
        loadValidationResults('unchecked', 1);
    } catch (error) {
        console.error('Error loading validation stats:', error);
    }
}

async function loadValidationResults(status, page = 1) {
    try {
        const response = await fetch(`/api/validation/emails?status=${status}&page=${page}&limit=50`);
        const data = await response.json();
        
        if (data.success && data.emails) {
            const tbody = document.getElementById('validationResultsTableBody');
            tbody.innerHTML = '';
            
            if (data.emails.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No results found</td></tr>';
                return;
            }
            
            data.emails.forEach(email => {
                const notes = email.validation_notes || {};
                const warnings = (notes.warnings || []).join(', ');
                const statusBadge = getStatusBadge(email.validation_status);
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${email.recipient}</td>
                    <td>${statusBadge}</td>
                    <td title="${warnings}">${warnings ? warnings.substring(0, 50) + '...' : '-'}</td>
                    <td title="${notes.overall_message}">${(notes.overall_message || '-').substring(0, 50)}...</td>
                    <td>${email.validated_at ? new Date(email.validated_at).toLocaleString() : '-'}</td>
                `;
                tbody.appendChild(row);
            });
            
            // Update pagination
            renderValidationPagination(data.pages, page);
        }
    } catch (error) {
        console.error('Error loading validation results:', error);
    }
}

function getStatusBadge(status) {
    const badges = {
        'unchecked': '<span class="badge badge-secondary">Unchecked</span>',
        'valid': '<span class="badge badge-success">Valid</span>',
        'invalid': '<span class="badge badge-danger">Invalid</span>',
        'needs_review': '<span class="badge badge-warning">Needs Review</span>'
    };
    return badges[status] || `<span class="badge">${status}</span>`;
}

function renderValidationPagination(totalPages, currentPage) {
    const paginationContainer = document.getElementById('validationPagination');
    if (!paginationContainer) return;
    
    paginationContainer.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.className = `pagination-btn ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.onclick = () => {
            const status = document.getElementById('validationStatus').value;
            loadValidationResults(status, i);
        };
        paginationContainer.appendChild(btn);
    }
}

async function startValidation() {
    const level = document.getElementById('validationLevel').value;
    const status = document.getElementById('validationStatus').value;
    const limit = parseInt(document.getElementById('validationBatchSize').value);
    
    const btn = document.getElementById('startValidationBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
    
    try {
        const response = await fetch('/api/validation/validate-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                validation_status: status,
                limit: limit,
                level: level
            })
        });
        
        const data = await response.json();
        
        const resultBox = document.getElementById('validationResult');
        resultBox.style.display = 'block';
        
        if (data.success) {
            resultBox.className = 'result-box alert alert-success';
            resultBox.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <div>
                    <strong>Validation Complete!</strong>
                    <ul>
                        <li>Validated: ${data.validated} emails</li>
                        <li>Errors: ${data.errors} emails</li>
                        <li>Total Processed: ${data.total} emails</li>
                    </ul>
                    ${data.results && data.results.length > 0 ? `
                        <h4>Summary:</h4>
                        <ul>
                            ${data.results.slice(0, 5).map(r => `
                                <li>
                                    ${r.recipient}: 
                                    <strong>${r.status}</strong>
                                    ${r.warnings && r.warnings.length > 0 ? `<br><small>${r.warnings.join(', ')}</small>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                        ${data.results.length > 5 ? `<p><small>... and ${data.results.length - 5} more</small></p>` : ''}
                    ` : ''}
                </div>
            `;
        } else {
            resultBox.className = 'result-box alert alert-error';
            resultBox.innerHTML = `<i class="fas fa-times-circle"></i> <strong>Error:</strong> ${data.error}`;
        }
        
        // Refresh stats
        setTimeout(loadValidationStats, 1000);
        
    } catch (error) {
        console.error('Error during validation:', error);
        const resultBox = document.getElementById('validationResult');
        resultBox.style.display = 'block';
        resultBox.className = 'result-box alert alert-error';
        resultBox.innerHTML = `<i class="fas fa-times-circle"></i> <strong>Error:</strong> ${error.message}`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// ===================== TEMPLATE MANAGEMENT =====================

async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();
        
        if (data.success && data.templates) {
            const container = document.getElementById('templatesList');
            container.innerHTML = '';
            
            if (data.templates.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No templates created yet. Create your first template to get started!</p></div>';
                return;
            }
            
            data.templates.forEach(template => {
                const card = document.createElement('div');
                card.className = 'template-card';
                card.innerHTML = `
                    <div class="card-header">
                        <h4>${template.name}</h4>
                        <div class="card-actions">
                            <button class="btn-icon" onclick="editTemplate(${template.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-icon" onclick="deleteTemplate(${template.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <p><strong>Subject:</strong> ${template.subject}</p>
                        <p><strong>Created:</strong> ${new Date(template.created_at).toLocaleString()}</p>
                        <p><strong>Updated:</strong> ${new Date(template.updated_at).toLocaleString()}</p>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

async function saveTemplate() {
    const templateId = document.getElementById('templateName').dataset.templateId;
    const name = document.getElementById('templateName').value;
    const subject = document.getElementById('templateSubject').value;
    const body = document.getElementById('templateBody').value;
    const html = document.getElementById('templateHtml').value;
    const tags = document.getElementById('templateTags').value.split(',').filter(t => t.trim());
    
    if (!name || !subject || !body) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const method = templateId ? 'PUT' : 'POST';
        const url = templateId ? `/api/templates/${templateId}` : '/api/templates';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                subject: subject,
                body: body,
                html_body: html || null,
                tags: tags.length > 0 ? tags : null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            document.getElementById('templateForm').style.display = 'none';
            resetTemplateForm();
            loadTemplates();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving template:', error);
        alert('Error saving template: ' + error.message);
    }
}

async function editTemplate(templateId) {
    try {
        const response = await fetch(`/api/templates/${templateId}`);
        const data = await response.json();
        
        if (data.success && data.template) {
            const template = data.template;
            document.getElementById('formTitle').textContent = `Edit Template: ${template.name}`;
            document.getElementById('templateName').value = template.name;
            document.getElementById('templateName').dataset.templateId = templateId;
            document.getElementById('templateSubject').value = template.subject;
            document.getElementById('templateBody').value = template.body;
            document.getElementById('templateHtml').value = template.html_body || '';
            document.getElementById('templateTags').value = template.tags ? template.tags.join(', ') : '';
            
            document.getElementById('templateForm').style.display = 'block';
            document.getElementById('templateForm').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error editing template:', error);
        alert('Error loading template');
    }
}

async function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
        const response = await fetch(`/api/templates/${templateId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Template deleted successfully');
            loadTemplates();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting template:', error);
        alert('Error deleting template');
    }
}

function resetTemplateForm() {
    document.getElementById('formTitle').textContent = 'Create New Template';
    document.getElementById('templateName').value = '';
    document.getElementById('templateName').dataset.templateId = '';
    document.getElementById('templateSubject').value = '';
    document.getElementById('templateBody').value = '';
    document.getElementById('templateHtml').value = '';
    document.getElementById('templateTags').value = '';
}

// ===================== SCHEDULER MANAGEMENT =====================

async function loadSchedules() {
    try {
        const response = await fetch('/api/schedules');
        const data = await response.json();
        
        if (data.success && data.schedules) {
            const container = document.getElementById('schedulesList');
            container.innerHTML = '';
            
            if (data.schedules.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No schedules created yet. Create your first schedule!</p></div>';
                return;
            }
            
            data.schedules.forEach(schedule => {
                const statusBadgeClass = {
                    'draft': 'badge-secondary',
                    'scheduled': 'badge-info',
                    'running': 'badge-warning',
                    'completed': 'badge-success',
                    'failed': 'badge-danger',
                    'paused': 'badge-secondary'
                }[schedule.status] || 'badge-secondary';
                
                const card = document.createElement('div');
                card.className = 'schedule-card';
                card.innerHTML = `
                    <div class="card-header">
                        <h4>${schedule.name}</h4>
                        <div class="card-status">
                            <span class="badge ${statusBadgeClass}">${schedule.status}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <p><strong>Type:</strong> ${schedule.schedule_type}</p>
                        <p><strong>Recipients:</strong> ${schedule.total_recipients}</p>
                        <p><strong>Sent:</strong> ${schedule.sent_count} / Failed: ${schedule.failed_count}</p>
                        <p><strong>Next Run:</strong> ${schedule.next_run ? new Date(schedule.next_run).toLocaleString() : 'Not scheduled'}</p>
                    </div>
                    <div class="card-actions">
                        <button class="btn-icon" onclick="editSchedule(${schedule.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        ${schedule.is_active ? 
                            `<button class="btn-icon" onclick="deactivateSchedule(${schedule.id})" title="Pause">
                                <i class="fas fa-pause"></i>
                            </button>` :
                            `<button class="btn-icon" onclick="activateSchedule(${schedule.id})" title="Resume">
                                <i class="fas fa-play"></i>
                            </button>`
                        }
                        <button class="btn-icon" onclick="deleteSchedule(${schedule.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading schedules:', error);
    }
}

async function loadScheduleTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();
        
        if (data.success && data.templates) {
            const select = document.getElementById('scheduleTemplate');
            select.innerHTML = '<option value="">-- Select Template --</option>';
            
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = template.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading templates for scheduler:', error);
    }
}

async function saveSchedule() {
    const scheduleId = document.getElementById('scheduleName').dataset.scheduleId;
    const name = document.getElementById('scheduleName').value;
    const templateId = document.getElementById('scheduleTemplate').value;
    const scheduleType = document.getElementById('scheduleType').value;
    const scheduleTime = document.getElementById('scheduleTime').value;
    const startDate = document.getElementById('scheduleStartDate').value;
    const endDate = document.getElementById('scheduleEndDate').value;
    const recipientsText = document.getElementById('scheduleRecipients').value;
    const notes = document.getElementById('scheduleNotes').value;
    
    if (!name || !scheduleType || !startDate || !recipientsText.trim()) {
        alert('Please fill in all required fields');
        return;
    }
    
    const recipients = recipientsText.split('\n').map(e => e.trim()).filter(e => e);
    
    try {
        const method = scheduleId ? 'PUT' : 'POST';
        const url = scheduleId ? `/api/schedules/${scheduleId}` : '/api/schedules';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                template_id: templateId || null,
                schedule_type: scheduleType,
                schedule_time: scheduleTime || null,
                start_date: startDate,
                end_date: endDate || null,
                recipient_list: recipients,
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            document.getElementById('scheduleForm').style.display = 'none';
            resetScheduleForm();
            loadSchedules();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving schedule:', error);
        alert('Error saving schedule: ' + error.message);
    }
}

async function editSchedule(scheduleId) {
    try {
        const response = await fetch(`/api/schedules/${scheduleId}`);
        const data = await response.json();
        
        if (data.success && data.schedule) {
            const schedule = data.schedule;
            document.getElementById('scheduleFormTitle').textContent = `Edit Schedule: ${schedule.name}`;
            document.getElementById('scheduleName').value = schedule.name;
            document.getElementById('scheduleName').dataset.scheduleId = scheduleId;
            document.getElementById('scheduleTemplate').value = schedule.template_id || '';
            document.getElementById('scheduleType').value = schedule.schedule_type || 'once';
            document.getElementById('scheduleTime').value = schedule.schedule_time || '';
            document.getElementById('scheduleStartDate').value = schedule.start_date || '';
            document.getElementById('scheduleEndDate').value = schedule.end_date || '';
            document.getElementById('scheduleNotes').value = schedule.notes || '';
            
            // Parse recipients from JSON
            try {
                const recipients = JSON.parse(schedule.recipient_list);
                document.getElementById('scheduleRecipients').value = recipients.join('\n');
            } catch (e) {
                document.getElementById('scheduleRecipients').value = schedule.recipient_list;
            }
            
            document.getElementById('scheduleForm').style.display = 'block';
            document.getElementById('scheduleForm').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error editing schedule:', error);
        alert('Error loading schedule');
    }
}

async function activateSchedule(scheduleId) {
    try {
        const response = await fetch(`/api/schedules/${scheduleId}/activate`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert('Schedule activated');
            loadSchedules();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error activating schedule:', error);
        alert('Error activating schedule');
    }
}

async function deactivateSchedule(scheduleId) {
    try {
        const response = await fetch(`/api/schedules/${scheduleId}/deactivate`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert('Schedule paused');
            loadSchedules();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error pausing schedule:', error);
        alert('Error pausing schedule');
    }
}

async function deleteSchedule(scheduleId) {
    if (!confirm('Are you sure you want to delete this schedule?')) return;
    
    try {
        const response = await fetch(`/api/schedules/${scheduleId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Schedule deleted successfully');
            loadSchedules();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting schedule:', error);
        alert('Error deleting schedule');
    }
}

function resetScheduleForm() {
    document.getElementById('scheduleFormTitle').textContent = 'Create New Schedule';
    document.getElementById('scheduleName').value = '';
    document.getElementById('scheduleName').dataset.scheduleId = '';
    document.getElementById('scheduleTemplate').value = '';
    document.getElementById('scheduleType').value = 'once';
    document.getElementById('scheduleTime').value = '';
    document.getElementById('scheduleStartDate').value = '';
    document.getElementById('scheduleEndDate').value = '';
    document.getElementById('scheduleRecipients').value = '';
    document.getElementById('scheduleNotes').value = '';
}

// ===================== EVENT LISTENERS FOR TEMPLATES & SCHEDULER =====================

document.getElementById('createTemplateBtn')?.addEventListener('click', () => {
    resetTemplateForm();
    document.getElementById('templateForm').style.display = 'block';
    document.getElementById('templateForm').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('cancelTemplateBtn')?.addEventListener('click', () => {
    document.getElementById('templateForm').style.display = 'none';
});

document.getElementById('saveTemplateBtn')?.addEventListener('click', saveTemplate);

document.getElementById('createScheduleBtn')?.addEventListener('click', () => {
    resetScheduleForm();
    document.getElementById('scheduleForm').style.display = 'block';
    document.getElementById('scheduleForm').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('cancelScheduleBtn')?.addEventListener('click', () => {
    document.getElementById('scheduleForm').style.display = 'none';
});

document.getElementById('saveScheduleBtn')?.addEventListener('click', saveSchedule);


// ===================== GRAPESJS VISUAL TEMPLATE BUILDER =====================

let grapesjsEditor = null;

// Builder Mode Switching
document.getElementById('codeEditorModeBtn')?.addEventListener('click', () => {
    switchEditorMode('code');
});

document.getElementById('visualBuilderModeBtn')?.addEventListener('click', () => {
    switchEditorMode('visual');
});

function switchEditorMode(mode) {
    const codeMode = document.getElementById('codeEditorMode');
    const visualMode = document.getElementById('visualBuilderMode');
    const codeBtn = document.getElementById('codeEditorModeBtn');
    const visualBtn = document.getElementById('visualBuilderModeBtn');

    if (mode === 'code') {
        codeMode.style.display = 'block';
        visualMode.style.display = 'none';
        codeBtn.classList.add('active');
        visualBtn.classList.remove('active');
    } else {
        codeMode.style.display = 'none';
        visualMode.style.display = 'block';
        visualBtn.classList.add('active');
        codeBtn.classList.remove('active');
        initializeGrapesJS();
    }
}

function initializeGrapesJS() {
    // If editor already exists, don't reinitialize
    if (grapesjsEditor) return;

    grapesjsEditor = grapesjs.init({
        container: '#gjs',
        fromElement: true,
        height: '650px',
        width: 'auto',
        storageManager: false,
        plugins: ['gjs-preset-newsletter'],
        pluginsOpts: {
            'gjs-preset-newsletter': {
                modalTitleImport: 'Import template',
                cmdOpenImport: 'gjs-open-import-template',
                cmdTglImages: 'gjs-toggle-images',
                cmdInlineHtml: 'gjs-get-inlined-html',
                tableStylePrefix: 'gjs-table-',
                cellStylePrefix: 'gjs-cell-',
                classPrefix: 'gjs-'
            }
        },
        canvas: {
            styles: [
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
            ]
        },
        assetManager: {
            embedAsBase64: false,
            upload: false,
            uploadText: 'Drop files here or click to upload',
            multiUpload: false,
        },
        styleManager: {
            sectors: [{
                name: 'General',
                properties: [
                    'float', 'display', 'position', 'top', 'right', 'left', 'bottom'
                ]
            }, {
                name: 'Dimension',
                open: false,
                properties: [
                    'width', 'height', 'max-width', 'min-height', 'margin', 'padding'
                ]
            }, {
                name: 'Typography',
                open: false,
                properties: [
                    'font-family', 'font-size', 'font-weight', 'letter-spacing',
                    'color', 'line-height', 'text-align', 'text-decoration', 'text-shadow'
                ]
            }, {
                name: 'Decorations',
                open: false,
                properties: [
                    'background-color', 'border-radius', 'border', 'box-shadow', 'background'
                ]
            }]
        },
        blockManager: {
            blocks: [
                {
                    id: 'section',
                    label: '<i class="fa fa-square-o"></i><div>Section</div>',
                    content: '<table style="width: 100%;"><tr><td style="padding: 20px;">Section Content</td></tr></table>',
                    category: 'Basic'
                },
                {
                    id: 'text',
                    label: '<i class="fa fa-text-width"></i><div>Text</div>',
                    content: '<div style="padding: 10px;">Insert your text here. You can use {{name}}, {{email}} for variables.</div>',
                    category: 'Basic'
                },
                {
                    id: 'button',
                    label: '<i class="fa fa-square"></i><div>Button</div>',
                    content: '<a href="#" style="display: inline-block; padding: 12px 24px; background: #4f46e5; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Click Me</a>',
                    category: 'Basic'
                },
                {
                    id: 'image',
                    label: '<i class="fa fa-image"></i><div>Image</div>',
                    content: '<img src="https://via.placeholder.com/600x200" alt="Image" style="max-width: 100%; height: auto;">',
                    category: 'Basic'
                },
                {
                    id: 'divider',
                    label: '<i class="fa fa-minus"></i><div>Divider</div>',
                    content: '<hr style="border: none; border-top: 2px solid #e5e7eb; margin: 20px 0;">',
                    category: 'Basic'
                },
                {
                    id: 'spacer',
                    label: '<i class="fa fa-arrows-v"></i><div>Spacer</div>',
                    content: '<div style="height: 30px;"></div>',
                    category: 'Basic'
                }
            ]
        }
    });

    // Load existing content if editing a template
    const existingHtml = document.getElementById('templateHtml')?.value;
    if (existingHtml && existingHtml.trim()) {
        grapesjsEditor.setComponents(existingHtml);
    }
}

document.getElementById('saveBuilderTemplateBtn')?.addEventListener('click', () => {
    const name = document.getElementById('builderTemplateName').value;
    const subject = document.getElementById('builderTemplateSubject').value;

    if (!name || !subject) {
        alert('Please fill in template name and subject');
        return;
    }

    if (!grapesjsEditor) {
        alert('Visual builder not initialized');
        return;
    }

    // Get HTML from GrapesJS with inlined styles
    let htmlBody = '';
    try {
        htmlBody = grapesjsEditor.runCommand('gjs-get-inlined-html');
    } catch (e) {
        // Fallback if inline command not available
        htmlBody = grapesjsEditor.getHtml() + '<style>' + grapesjsEditor.getCss() + '</style>';
    }
    
    // Generate plain text version
    const plainText = grapesjsEditor.getWrapper().toHTML()
        .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
        .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

    // Populate code editor fields and save
    document.getElementById('templateName').value = name;
    document.getElementById('templateSubject').value = subject;
    document.getElementById('templateBody').value = plainText;
    document.getElementById('templateHtml').value = htmlBody;

    saveTemplate();
});

document.getElementById('cancelBuilderBtn')?.addEventListener('click', () => {
    document.getElementById('templateForm').style.display = 'none';
    if (grapesjsEditor) {
        grapesjsEditor.destroy();
        grapesjsEditor = null;
    }
});

// User Menu Functions
function initializeUserMenu() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    const logoutBtn = document.getElementById('logoutBtn');
    const userMenuUsername = document.getElementById('userMenuUsername');
    
    if (!userMenuBtn) return;
    
    // Load and display current username
    loadCurrentUsername(userMenuUsername);
    
    // Toggle dropdown on user button click
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
        userMenuBtn.classList.toggle('active');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.classList.remove('active');
            userMenuBtn.classList.remove('active');
        }
    });
    
    // Logout functionality
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await logoutUser();
        });
    }
    
    // Prevent dropdown items from closing on click (except logout)
    document.querySelectorAll('.dropdown-item').forEach(item => {
        if (!item.id.includes('logout')) {
            item.addEventListener('click', (e) => {
                userDropdown.classList.remove('active');
                userMenuBtn.classList.remove('active');
            });
        }
    });
}

function loadCurrentUsername(element) {
    // Get username from Flask session
    fetch('/api/current-user')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.username) {
                element.textContent = data.username;
            }
        })
        .catch(error => console.error('Error loading username:', error));
}

async function logoutUser() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear any session data and redirect to login
            window.location.href = '/login';
        } else {
            showAlert(data.error || 'Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showAlert('Logout failed: ' + error.message, 'error');
    }
}

function showAlert(message, type = 'info') {
    // Use existing notification system or create a simple alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem;
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        max-width: 300px;
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

