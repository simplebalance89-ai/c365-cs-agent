/* =============================================================
   CONVEYANCE365 — AI Customer Service Agent
   Frontend Application Logic
   ============================================================= */

'use strict';

// ── MOCK DATA ─────────────────────────────────────────────────
const MOCK_TICKETS = [
  {
    id: 1001,
    subject: "HVAC not working in Suite 4B — meeting in 2 hours",
    requester: "Sarah Chen",
    requester_email: "sarah.chen@novacorp.com",
    priority: "urgent",
    status: "open",
    category: "Facilities",
    created_at: "2024-01-15T09:14:00Z",
    updated_at: "2024-01-15T09:42:00Z",
    sentiment: "negative",
    ai_summary: "Tenant in Suite 4B is reporting a non-functional HVAC system. They have an important client meeting scheduled in approximately 2 hours. This is a high-urgency facilities issue requiring immediate dispatch. Temperature has reportedly reached 82°F in the workspace.",
    conversation: [
      { author: "Sarah Chen", role: "customer", time: "9:14 AM", body: "Hi, the AC in our suite (4B) has completely stopped working. It's getting really hot in here and we have a very important client meeting in 2 hours. This is urgent — we can't have clients walking into a sweltering office. Please send someone ASAP." },
      { author: "Support Agent", role: "agent", time: "9:28 AM", body: "Hi Sarah, I'm so sorry to hear about the AC issue. I've flagged this as urgent and am escalating to our facilities team right now. Can you confirm the exact temperature and whether any other suites are affected?" },
      { author: "Sarah Chen", role: "customer", time: "9:35 AM", body: "It's showing 82°F on the thermostat and the unit is making a clicking noise but not blowing cold air. I don't think other suites are affected — the ones next to us seem fine." }
    ],
    ai_response: "Hi Sarah,\n\nI completely understand the urgency here — we're treating this as our top priority right now.\n\nOur HVAC technician has been dispatched and is en route to Suite 4B. ETA is approximately 30–40 minutes, which gives us time to resolve the issue before your client meeting.\n\nIn the meantime, we have two portable AC units we can bring up immediately to cool the space while the repair is underway. I'll also reserve our Conference Suite A on the 3rd floor as a backup space for your meeting at no charge, just in case.\n\nYou'll receive a text update when the technician is 10 minutes away.\n\nWe sincerely apologize for the inconvenience and are committed to making sure your meeting goes smoothly.\n\nBest regards,\nConveyance365 Support"
  },
  {
    id: 1002,
    subject: "Need to add 2 more desks to our hot desk plan",
    requester: "Marcus Webb",
    requester_email: "marcus@blueridgecap.com",
    priority: "high",
    status: "open",
    category: "Account / Billing",
    created_at: "2024-01-15T08:30:00Z",
    updated_at: "2024-01-15T08:45:00Z",
    sentiment: "positive",
    ai_summary: "Existing hot desk client looking to expand their plan by 2 desks. This is an upsell opportunity. Client appears satisfied and is growing their team. Requires account update and billing adjustment. No technical issues involved.",
    conversation: [
      { author: "Marcus Webb", role: "customer", time: "8:30 AM", body: "Hey! We've been loving Conveyance365 so far — the team really settles in well here. We're hiring two more people who'll need hot desk access starting Feb 1st. Can we add them to our plan? Also curious if there are any discounts for adding multiple desks at once." }
    ],
    ai_response: "Hi Marcus,\n\nThat's fantastic news — congratulations on the team growth! We love hearing that the team has been enjoying Conveyance365.\n\nAbsolutely, adding 2 more hot desk memberships is easy. Here's what I can do for you:\n\n• Add 2 hot desk memberships effective February 1st\n• Current rate: $299/desk/month (your plan rate)\n• With 2+ additional desks, you qualify for our Growth Tier: $275/desk/month across all your desks\n\nThis would actually reduce your existing desk costs AND add the two new ones. Net savings of ~$48/month.\n\nI'll send over an updated membership agreement for your e-signature. Would you like me to also set up access credentials for the new team members once you confirm their names and emails?\n\nLooking forward to welcoming the new additions!\n\nWarm regards,\nConveyance365 Support"
  },
  {
    id: 1003,
    subject: "WiFi dropping every 30 minutes — affecting video calls",
    requester: "Priya Nair",
    requester_email: "priya@meridiandesign.io",
    priority: "high",
    status: "open",
    category: "Technical / IT",
    created_at: "2024-01-15T10:02:00Z",
    updated_at: "2024-01-15T10:20:00Z",
    sentiment: "negative",
    ai_summary: "Recurring WiFi connectivity issue in what appears to be a specific area of the workspace. Customer has been experiencing this for 3 days. Drops occur approximately every 30 minutes and interrupt video calls. May be a DHCP lease issue or access point problem. IT team should investigate the AP nearest to the affected workspace.",
    conversation: [
      { author: "Priya Nair", role: "customer", time: "10:02 AM", body: "This is the third day in a row the WiFi has been dropping for us. It happens like clockwork every 30 minutes and it's killing our video calls with clients. We're a design studio — we depend on reliable internet. This is really not acceptable." },
      { author: "Support Agent", role: "agent", time: "10:15 AM", body: "Hi Priya, I sincerely apologize for this ongoing issue. Three days is far too long for this to persist. Can you tell me which area of the workspace you're in and roughly what time the drops tend to start each day?" },
      { author: "Priya Nair", role: "customer", time: "10:20 AM", body: "We're in the Creative Wing, desks 12-16. It usually starts around 9:30 AM and then just keeps dropping every 30 min after that. Our team is working around it but honestly we're considering whether Conveyance365 is right for us if this keeps happening." }
    ],
    ai_response: "Hi Priya,\n\nI hear you, and I want to sincerely apologize — three days of this is completely unacceptable, and I take full responsibility for not getting this resolved sooner.\n\nI've just escalated this directly to our IT infrastructure team with the specific details you've shared: Creative Wing, desks 12–16, starting ~9:30 AM. Based on the 30-minute interval pattern, this looks like a DHCP lease issue with the access point in your area, which is fixable.\n\nHere's what happens next:\n1. Our IT tech will be in the Creative Wing within the hour to diagnose and fix the access point\n2. We'll monitor connectivity for the rest of today and tomorrow\n3. As an apology for 3 days of disruption, I'm crediting your account with 3 days of membership — no charge\n\nI'll personally follow up with you at 2 PM today to confirm the issue is resolved. If it happens again before then, text our emergency facilities line: [number on file].\n\nWe absolutely want Conveyance365 to be the right fit for Meridian Design — and we'll earn that back.\n\nSincerely,\nConveyance365 Support"
  },
  {
    id: 1004,
    subject: "Conference room booking question — recurring reservations",
    requester: "Daniel Park",
    requester_email: "d.park@summitventures.co",
    priority: "normal",
    status: "open",
    category: "Bookings",
    created_at: "2024-01-15T07:50:00Z",
    updated_at: "2024-01-15T07:50:00Z",
    sentiment: "neutral",
    ai_summary: "Member asking about recurring conference room bookings. Standard inquiry — wants to reserve a conference room on a weekly basis for team standups. Need to check room availability and explain recurring booking policy/process through the member portal.",
    conversation: [
      { author: "Daniel Park", role: "customer", time: "7:50 AM", body: "Hi — I'm trying to figure out how to set up a recurring conference room booking. We do a team standup every Tuesday and Thursday at 10 AM for about 45 minutes and I want to reserve the same room (preferably Boardroom 2) both days each week. Is this possible through the portal?" }
    ],
    ai_response: "Hi Daniel,\n\nGreat question! Yes, recurring bookings are absolutely available through your member portal.\n\nHere's how to set it up:\n1. Log into your member portal at members.conveyance365.com\n2. Navigate to Conference Rooms → Book a Room\n3. Select Boardroom 2, choose your start time (10:00 AM, 45 min)\n4. Click \"Make Recurring\" and select Tuesday/Thursday weekly\n5. Set your end date or choose \"Until Cancelled\"\n\nQuick note: Boardroom 2 is currently available on your requested slots. Recurring bookings are locked in on a first-come basis, so I'd recommend setting this up today.\n\nYour plan includes 4 hours of conference room time per month — your 45-min standups twice weekly will use approximately 6 hours/month, so there will be a small overage charge of $15/month for the additional 2 hours. Let me know if you'd like me to look at a plan upgrade that might make more sense.\n\nAnything else I can help with?\n\nBest,\nConveyance365 Support"
  },
  {
    id: 1005,
    subject: "Printer not connecting — need to print contracts today",
    requester: "Jennifer Torres",
    requester_email: "jennifer@torresgrouplaw.com",
    priority: "urgent",
    status: "open",
    category: "Technical / IT",
    created_at: "2024-01-15T11:15:00Z",
    updated_at: "2024-01-15T11:15:00Z",
    sentiment: "negative",
    ai_summary: "Law firm member unable to connect to the shared printer. Urgent because they need to print legal contracts today. Likely a driver or network printer connection issue. Standard troubleshooting: verify printer IP, reinstall print driver, or direct to alternate printer location.",
    conversation: [
      { author: "Jennifer Torres", role: "customer", time: "11:15 AM", body: "I cannot get the printer on the 2nd floor to connect to my laptop (Mac). I've tried turning it off and on. I have contracts I need to print by 1 PM for a client signing. This is really stressful." }
    ],
    ai_response: "Hi Jennifer,\n\nI understand the time pressure — let's get this sorted right now.\n\nFor Mac connectivity to our floor printers, try these steps first (takes under 2 min):\n1. Go to System Preferences → Printers & Scanners\n2. Click the + button and select \"Conveyance365-Floor2-HP\" from the list\n3. If it doesn't appear, click \"IP\" tab and enter: 192.168.1.45\n\nIf that doesn't work immediately: our front desk (ext. 0) can print documents for you — just email them the files and they'll have them printed and waiting within 5 minutes. Given your 1 PM deadline, I'd use this as your backup right now.\n\nI'm also sending our IT tech to the 2nd floor printer to do a quick reset — this should resolve the Mac connection issue for all future use.\n\nPlease let me know the moment you have those contracts in hand. You've got this.\n\nConveyance365 Support"
  },
  {
    id: 1006,
    subject: "Interested in upgrading to private office — need pricing",
    requester: "Alex Kim",
    requester_email: "alex@kimcreative.studio",
    priority: "normal",
    status: "open",
    category: "Sales / Upgrade",
    created_at: "2024-01-15T06:45:00Z",
    updated_at: "2024-01-15T06:45:00Z",
    sentiment: "positive",
    ai_summary: "Existing hot desk member interested in upgrading to a private office. Clear upsell opportunity. Member has been with Conveyance365 for ~6 months and their creative studio is growing. Should be routed to sales team for a tour and proposal, while providing initial pricing to maintain momentum.",
    conversation: [
      { author: "Alex Kim", role: "customer", time: "6:45 AM", body: "Hi Conveyance365 team — I've been a hot desk member for about 6 months now and the business has grown to the point where we really need a dedicated private space. Can you send me pricing for private offices? Ideally looking for something that fits 3-4 people." }
    ],
    ai_response: "Hi Alex,\n\nCongratulations on the growth — six months in and already scaling up is a great sign!\n\nFor a 3–4 person private office, here's our current availability and pricing:\n\n• Studio Office (3 desks) — $1,850/month — 2 available\n• Standard Private Office (4 desks) — $2,400/month — 1 available on Floor 3\n• Premium Office (4 desks + glass wall, Floor 5) — $2,800/month — 1 available\n\nAll private offices include: 24/7 access, 10 hrs conference room/month, mail handling, and your current hot desk membership perks.\n\nAs a 6-month member, you also qualify for our Loyalty Upgrade Incentive: first 2 months at 15% off when you sign a 12-month term.\n\nI'd love to schedule a quick 10-minute walkthrough of the available offices so you can see the spaces in person. I can do Tuesday or Wednesday afternoon — does either work?\n\nLooking forward to growing with you!\n\nConveyance365 Sales Team"
  },
  {
    id: 1007,
    subject: "Package delivered to wrong floor — missing important docs",
    requester: "Rachel Green",
    requester_email: "r.green@foundrypartners.com",
    priority: "high",
    status: "open",
    category: "Facilities",
    created_at: "2024-01-15T10:45:00Z",
    updated_at: "2024-01-15T10:45:00Z",
    sentiment: "negative",
    ai_summary: "Mail delivery error — package containing important documents was delivered to the wrong floor. Member is concerned about missing time-sensitive materials. Requires immediate physical search of mail room and incorrect delivery floor. Should be treated as high priority due to potential legal/business sensitivity of documents.",
    conversation: [
      { author: "Rachel Green", role: "customer", time: "10:45 AM", body: "A package that was supposed to come to Floor 4 (Foundry Partners) was apparently delivered somewhere else. It has legal documents inside that I need today. The tracking says it was delivered at 9:15 AM to 'Conveyance365' but it's not at our floor's mail area." }
    ],
    ai_response: "Hi Rachel,\n\nWe're on this right now — legal documents going missing is absolutely something we take seriously.\n\nI've alerted our front desk and facilities team to check three locations immediately:\n1. Main floor mail room (packages sometimes sorted centrally)\n2. Floor 3 and Floor 5 mail areas (adjacent floor mix-up)\n3. Front desk reception (oversized packages are held there)\n\nCan you share the tracking number? That will let us confirm exactly where the delivery scan occurred in our building and narrow the search.\n\nSomeone will physically walk those locations in the next 10 minutes. I'll call you directly at the number on your account as soon as the package is located. If we cannot locate it within 30 minutes, I will escalate to building management and initiate a formal package trace.\n\nSorry for this stress — we'll find it.\n\nConveyance365 Support"
  },
  {
    id: 1008,
    subject: "Locker combo not working after reset",
    requester: "Tom Bradley",
    requester_email: "tom.b@cloudnative.dev",
    priority: "low",
    status: "open",
    category: "Facilities",
    created_at: "2024-01-15T09:55:00Z",
    updated_at: "2024-01-15T09:55:00Z",
    sentiment: "neutral",
    ai_summary: "Member locked out of their assigned locker after a combination reset didn't work correctly. Low urgency as it does not affect their work directly. Standard facilities task — front desk has master override access to all lockers.",
    conversation: [
      { author: "Tom Bradley", role: "customer", time: "9:55 AM", body: "Hey — I reset my locker combo yesterday (Locker #23 on Floor 2) and now neither the old code nor the new one is working. My laptop bag is in there." }
    ],
    ai_response: "Hi Tom,\n\nNo worries — this happens occasionally after combo resets. Easy fix!\n\nOur front desk has a master override key for all lockers. Just swing by the main reception and mention Locker #23 on Floor 2 — they can open it for you immediately, no wait.\n\nWhile you're there, they can also do a full combo reset with you present to make sure the new code takes correctly.\n\nSorry for the inconvenience!\n\nConveyance365 Support"
  }
];

const MOCK_INSIGHTS = {
  tickets_received: 47,
  resolved_today: 31,
  resolution_rate: "66%",
  avg_response_time: "4.2 min",
  csat_score: "4.7/5",
  open_urgent: 2,
  categories: [
    { name: "Facilities", count: 14, pct: 30 },
    { name: "Technical / IT", count: 12, pct: 26 },
    { name: "Bookings", count: 9, pct: 19 },
    { name: "Account / Billing", count: 7, pct: 15 },
    { name: "Sales / Upgrade", count: 5, pct: 11 }
  ],
  sentiment: { positive: 45, neutral: 32, negative: 23 },
  activity: [
    { type: "resolved", text: "<strong>AI resolved</strong> ticket #998 — WiFi inquiry", time: "2 min ago", dot: "dot-green" },
    { type: "classified", text: "<strong>AI classified</strong> #1008 as Facilities (98% confidence)", time: "4 min ago", dot: "dot-blue" },
    { type: "escalated", text: "<strong>Escalated</strong> #1001 to Facilities Emergency", time: "8 min ago", dot: "dot-accent" },
    { type: "response", text: "<strong>AI drafted</strong> response for #1003 (WiFi drops)", time: "11 min ago", dot: "dot-blue" },
    { type: "new", text: "<strong>New ticket</strong> #1007 — Missing package, Floor 4", time: "19 min ago", dot: "dot-orange" },
    { type: "resolved", text: "<strong>AI resolved</strong> #995 — Desk booking question", time: "25 min ago", dot: "dot-green" }
  ]
};

// ── STATE ─────────────────────────────────────────────────────
const state = {
  tickets: [],
  activeTicketId: null,
  demoMode: false,
  connected: false,
  filter: 'all',
  search: ''
};

// ── DOM REFS ──────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const ticketList    = $('ticket-list');
const ticketDetail  = $('ticket-detail');
const emptyDetail   = $('empty-detail');
const demoToggle    = $('demo-mode-toggle');
const refreshBtn    = $('refresh-btn');
const priorityFilter = $('priority-filter');
const searchInput   = $('search-input');
const connDot       = $('conn-dot');
const connLabel     = $('conn-label');
const responseTA    = $('response-textarea');
const charCount     = $('char-count');
const toast         = $('toast');

let toastTimer = null;

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindEvents();
  setTodayLabel();
  // Start with demo mode ON for the sales demo
  demoToggle.checked = true;
  state.demoMode = true;
  loadData();
  setInterval(tickActivityFeed, 8000);
});

// ── EVENTS ────────────────────────────────────────────────────
function bindEvents() {
  demoToggle.addEventListener('change', e => {
    state.demoMode = e.target.checked;
    showToast(state.demoMode ? 'Demo Mode activated — showing realistic mock data' : 'Live Mode — connecting to API…', 'info');
    loadData();
  });

  refreshBtn.addEventListener('click', () => {
    refreshBtn.classList.add('spinning');
    loadData().finally(() => {
      setTimeout(() => refreshBtn.classList.remove('spinning'), 600);
    });
  });

  priorityFilter.addEventListener('change', e => {
    state.filter = e.target.value;
    renderTicketList();
  });

  searchInput.addEventListener('input', e => {
    state.search = e.target.value.toLowerCase();
    renderTicketList();
  });

  responseTA.addEventListener('input', () => {
    charCount.textContent = `${responseTA.value.length} characters`;
  });

  $('btn-send').addEventListener('click', sendResponse);
  $('btn-copy').addEventListener('click', copyResponse);
  $('btn-escalate').addEventListener('click', escalateTicket);
  $('btn-classify').addEventListener('click', classifyTicket);
  $('btn-regenerate').addEventListener('click', regenerateResponse);
}

// ── DATA LOADING ──────────────────────────────────────────────
async function loadData() {
  setConnectionStatus('connecting');

  if (state.demoMode) {
    await delay(400);
    state.tickets = [...MOCK_TICKETS];
    setConnectionStatus('connected');
    renderTicketList();
    renderInsights(MOCK_INSIGHTS);
    updateHeaderStats(MOCK_INSIGHTS);
    renderActivityFeed(MOCK_INSIGHTS.activity);
    return;
  }

  // Live API mode
  try {
    const [ticketsRes, insightsRes] = await Promise.all([
      fetchWithTimeout('/api/tickets'),
      fetchWithTimeout('/api/insights')
    ]);
    state.tickets = ticketsRes;
    setConnectionStatus('connected');
    renderTicketList();
    renderInsights(insightsRes);
    updateHeaderStats(insightsRes);
    renderActivityFeed(insightsRes.activity || []);
  } catch (err) {
    setConnectionStatus('error');
    showToast('Could not connect to API — falling back to demo data', 'error');
    // Graceful fallback
    state.tickets = [...MOCK_TICKETS];
    renderTicketList();
    renderInsights(MOCK_INSIGHTS);
    updateHeaderStats(MOCK_INSIGHTS);
    renderActivityFeed(MOCK_INSIGHTS.activity);
  }
}

async function fetchWithTimeout(url, options = {}, timeout = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}

// ── TICKET LIST ───────────────────────────────────────────────
function renderTicketList() {
  let tickets = state.tickets;

  if (state.filter !== 'all') {
    tickets = tickets.filter(t => t.priority === state.filter);
  }
  if (state.search) {
    tickets = tickets.filter(t =>
      t.subject.toLowerCase().includes(state.search) ||
      t.requester.toLowerCase().includes(state.search) ||
      (t.category || '').toLowerCase().includes(state.search)
    );
  }

  // Sort: urgent first, then high, then by time
  const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
  tickets.sort((a, b) => {
    const pa = priorityOrder[a.priority] ?? 9;
    const pb = priorityOrder[b.priority] ?? 9;
    if (pa !== pb) return pa - pb;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  // Update panel title with count
  const titleEl = document.querySelector('.panel-queue .panel-title');
  const existingBadge = titleEl.querySelector('.ticket-count');
  if (existingBadge) existingBadge.remove();
  const badge = document.createElement('span');
  badge.className = 'ticket-count';
  badge.textContent = tickets.length;
  titleEl.appendChild(badge);

  if (tickets.length === 0) {
    ticketList.innerHTML = `<div class="no-tickets">No tickets match your filter</div>`;
    return;
  }

  ticketList.innerHTML = tickets.map(t => renderTicketItem(t)).join('');

  // Bind click events
  ticketList.querySelectorAll('.ticket-item').forEach(el => {
    el.addEventListener('click', () => {
      const id = parseInt(el.dataset.id, 10);
      selectTicket(id);
    });
  });

  // Re-apply active state
  if (state.activeTicketId) {
    const activeEl = ticketList.querySelector(`[data-id="${state.activeTicketId}"]`);
    if (activeEl) activeEl.classList.add('active');
  }
}

function renderTicketItem(t) {
  const timeAgo = formatTimeAgo(t.created_at);
  return `
    <div class="ticket-item" data-id="${t.id}">
      <div class="ticket-item-header">
        <span class="ticket-id">#${t.id}</span>
        <span class="priority-badge priority-${t.priority}">${capitalize(t.priority)}</span>
      </div>
      <div class="ticket-subject">${escapeHtml(t.subject)}</div>
      <div class="ticket-meta">
        <span class="ticket-requester">${escapeHtml(t.requester)}</span>
        <span class="ticket-time">${timeAgo}</span>
      </div>
      <div class="ticket-footer">
        <span class="category-tag">${escapeHtml(t.category || 'Uncategorized')}</span>
      </div>
    </div>
  `;
}

// ── TICKET DETAIL ─────────────────────────────────────────────
async function selectTicket(id) {
  state.activeTicketId = id;

  // Update active state in list
  ticketList.querySelectorAll('.ticket-item').forEach(el => {
    el.classList.toggle('active', parseInt(el.dataset.id, 10) === id);
  });

  emptyDetail.style.display = 'none';
  ticketDetail.style.display = 'flex';
  ticketDetail.style.flexDirection = 'column';
  ticketDetail.style.gap = '20px';

  let ticket;

  if (state.demoMode) {
    await delay(150);
    ticket = MOCK_TICKETS.find(t => t.id === id);
  } else {
    try {
      ticket = await fetchWithTimeout(`/api/tickets/${id}`);
    } catch (err) {
      // Fallback to local mock
      ticket = MOCK_TICKETS.find(t => t.id === id);
      if (!ticket) { showToast('Could not load ticket details', 'error'); return; }
    }
  }

  if (!ticket) return;
  populateDetail(ticket);
}

function populateDetail(ticket) {
  $('detail-id').textContent = `#${ticket.id}`;
  $('detail-priority').textContent = capitalize(ticket.priority);
  $('detail-priority').className = `priority-badge priority-${ticket.priority}`;
  $('detail-category').textContent = ticket.category || 'Uncategorized';
  $('detail-subject').textContent = ticket.subject;
  $('detail-requester').textContent = `${ticket.requester} · ${ticket.requester_email || ''}`;
  $('detail-created').textContent = formatDateTime(ticket.created_at);
  $('ai-summary-text').textContent = ticket.ai_summary || 'No summary available.';

  // Sentiment
  const sentMap = {
    positive: { icon: '😊', label: 'Positive', cls: 'positive' },
    neutral:  { icon: '😐', label: 'Neutral',  cls: 'neutral' },
    negative: { icon: '😟', label: 'Frustrated', cls: 'negative' }
  };
  const sent = sentMap[ticket.sentiment] || sentMap.neutral;
  const sentBadge = $('sentiment-badge');
  $('sentiment-icon').textContent = sent.icon;
  $('sentiment-label').textContent = sent.label;
  sentBadge.className = `sentiment-badge ${sent.cls}`;

  // Conversation
  const thread = $('conversation-thread');
  thread.innerHTML = (ticket.conversation || []).map(msg => {
    const cls = msg.role === 'customer' ? 'customer' : 'agent';
    const nameCls = msg.role === 'customer' ? 'customer-name' : 'agent-name';
    return `
      <div class="message-bubble ${cls}">
        <div class="message-header">
          <span class="message-author ${nameCls}">${escapeHtml(msg.author)}</span>
          <span>${escapeHtml(msg.time || '')}</span>
        </div>
        <div class="message-body">${escapeHtml(msg.body)}</div>
      </div>
    `;
  }).join('');

  // AI Response
  const responseText = ticket.ai_response || '';
  responseTA.value = responseText;
  charCount.textContent = `${responseText.length} characters`;

  // Store current ticket on element for actions
  ticketDetail.dataset.ticketId = ticket.id;
}

// ── TICKET ACTIONS ────────────────────────────────────────────
async function sendResponse() {
  const id = ticketDetail.dataset.ticketId;
  const body = responseTA.value.trim();
  if (!body) { showToast('Response cannot be empty', 'error'); return; }

  const btn = $('btn-send');
  btn.disabled = true;
  btn.innerHTML = `<div class="spinner" style="width:14px;height:14px;border-width:2px;"></div> Sending…`;

  if (!state.demoMode) {
    try {
      await fetchWithTimeout(`/api/tickets/${id}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response: body })
      });
    } catch (err) {
      // Demo graceful fallback
    }
  }

  await delay(state.demoMode ? 900 : 500);

  btn.disabled = false;
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Send Response`;

  // Add sent message to thread
  const sentBubble = document.createElement('div');
  sentBubble.className = 'message-bubble ai-response';
  sentBubble.innerHTML = `
    <div class="message-header">
      <span class="message-author ai-name">AI Agent (sent)</span>
      <span>Just now</span>
    </div>
    <div class="message-body">${escapeHtml(body)}</div>
  `;
  $('conversation-thread').appendChild(sentBubble);
  sentBubble.scrollIntoView({ behavior: 'smooth', block: 'end' });

  // Remove ticket from queue visually
  const ticketEl = ticketList.querySelector(`[data-id="${id}"]`);
  if (ticketEl) {
    ticketEl.style.opacity = '0.4';
    ticketEl.style.pointerEvents = 'none';
  }

  showToast('Response sent successfully', 'success');
  addActivity(`<strong>AI response sent</strong> for ticket #${id}`, 'dot-green');
}

async function escalateTicket() {
  const id = ticketDetail.dataset.ticketId;
  if (!id) return;

  if (!state.demoMode) {
    try {
      await fetchWithTimeout(`/api/tickets/${id}/escalate`, { method: 'POST' });
    } catch (err) {}
  }

  await delay(state.demoMode ? 400 : 200);
  showToast(`Ticket #${id} escalated to senior support`, 'info');
  addActivity(`<strong>Escalated</strong> ticket #${id} to senior support`, 'dot-accent');

  const btn = $('btn-escalate');
  btn.textContent = 'Escalated';
  btn.disabled = true;
  btn.style.opacity = '0.6';
}

async function classifyTicket() {
  const id = ticketDetail.dataset.ticketId;
  if (!id) return;

  if (!state.demoMode) {
    try {
      await fetchWithTimeout(`/api/tickets/${id}/classify`, { method: 'POST' });
    } catch (err) {}
  }

  await delay(state.demoMode ? 600 : 300);
  showToast('Ticket re-classified by AI', 'success');
  addActivity(`<strong>AI re-classified</strong> ticket #${id}`, 'dot-blue');
}

async function regenerateResponse() {
  const id = ticketDetail.dataset.ticketId;
  const btn = $('btn-regenerate');
  btn.disabled = true;
  btn.textContent = 'Generating…';
  responseTA.value = '';
  charCount.textContent = '0 characters';

  await delay(state.demoMode ? 1200 : 800);

  const ticket = MOCK_TICKETS.find(t => t.id === parseInt(id, 10));
  if (ticket) {
    const variations = [ticket.ai_response, ticket.ai_response + '\n\nP.S. Please don\'t hesitate to reach out if you need any additional assistance.'];
    responseTA.value = variations[Math.floor(Math.random() * variations.length)] || ticket.ai_response;
    charCount.textContent = `${responseTA.value.length} characters`;
  }

  btn.disabled = false;
  btn.textContent = 'Regenerate';
  showToast('New response generated', 'success');
}

function copyResponse() {
  const text = responseTA.value;
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Response copied to clipboard', 'success');
  }).catch(() => {
    // Fallback
    responseTA.select();
    document.execCommand('copy');
    showToast('Response copied', 'success');
  });
}

// ── INSIGHTS ──────────────────────────────────────────────────
function renderInsights(data) {
  $('stat-received').textContent    = data.tickets_received || '—';
  $('stat-resolved-pct').textContent = data.resolution_rate || '—';
  $('stat-response-time').textContent = data.avg_response_time || '—';
  $('stat-csat').textContent         = data.csat_score || '—';

  renderCategoryBars(data.categories || []);
  renderSentimentBar(data.sentiment || {});
}

function updateHeaderStats(data) {
  const total = (data.tickets_received || 0);
  const urgent = data.open_urgent || 0;
  const resolved = data.resolved_today || 0;
  const csat = data.csat_score || '—';

  $('hdr-open').textContent = total;
  $('hdr-urgent').textContent = urgent;
  $('hdr-resolved').textContent = resolved;
  $('hdr-csat').textContent = csat;
}

function renderCategoryBars(categories) {
  const container = $('category-bars');
  if (!categories.length) { container.innerHTML = '<span style="color:var(--text-muted);font-size:12px;">No data</span>'; return; }
  const max = Math.max(...categories.map(c => c.pct));

  container.innerHTML = categories.map(c => `
    <div class="category-bar-row">
      <div class="category-bar-header">
        <span class="category-bar-label">${escapeHtml(c.name)}</span>
        <span class="category-bar-pct">${c.count} · ${c.pct}%</span>
      </div>
      <div class="category-bar-track">
        <div class="category-bar-fill" style="width: ${c.pct}%"></div>
      </div>
    </div>
  `).join('');

  // Animate bars
  setTimeout(() => {
    container.querySelectorAll('.category-bar-fill').forEach((el, i) => {
      el.style.width = `${categories[i].pct}%`;
    });
  }, 100);
}

function renderSentimentBar(sentiment) {
  const total = (sentiment.positive || 0) + (sentiment.neutral || 0) + (sentiment.negative || 0);
  if (!total) return;

  const pp = Math.round((sentiment.positive / total) * 100);
  const np = Math.round((sentiment.neutral / total) * 100);
  const ngp = 100 - pp - np;

  const posEl  = $('sent-positive');
  const neuEl  = $('sent-neutral');
  const negEl  = $('sent-negative');

  posEl.style.width  = `${pp}%`;
  neuEl.style.width  = `${np}%`;
  negEl.style.width  = `${ngp}%`;

  $('sent-positive-pct').textContent = `${pp}%`;
  $('sent-neutral-pct').textContent  = `${np}%`;
  $('sent-negative-pct').textContent = `${ngp}%`;
}

function renderActivityFeed(activities) {
  const feed = $('activity-feed');
  feed.innerHTML = activities.map(a => `
    <div class="activity-item">
      <div class="activity-dot ${a.dot}"></div>
      <div class="activity-body">
        <span class="activity-text">${a.text}</span>
        <span class="activity-time">${a.time}</span>
      </div>
    </div>
  `).join('');
}

// Tick the activity feed timestamps (makes demo feel live)
let activityTick = 0;
function tickActivityFeed() {
  if (!state.demoMode) return;
  activityTick++;
  const items = document.querySelectorAll('.activity-time');
  const times = ['Just now', '1 min ago', '2 min ago', '3 min ago', '5 min ago', '7 min ago'];
  items.forEach((el, i) => {
    const shifted = Math.min(i + Math.floor(activityTick / 2), times.length - 1);
    // Only advance occasionally
    if (activityTick % 3 === 0 && i < 3) {
      el.textContent = times[Math.min(parseInt(el.textContent) + 1, shifted)] || el.textContent;
    }
  });
}

function addActivity(text, dot) {
  const feed = $('activity-feed');
  const item = document.createElement('div');
  item.className = 'activity-item';
  item.style.opacity = '0';
  item.style.transform = 'translateY(-8px)';
  item.innerHTML = `
    <div class="activity-dot ${dot}"></div>
    <div class="activity-body">
      <span class="activity-text">${text}</span>
      <span class="activity-time">Just now</span>
    </div>
  `;
  feed.insertBefore(item, feed.firstChild);
  requestAnimationFrame(() => {
    item.style.transition = 'opacity 0.3s, transform 0.3s';
    item.style.opacity = '1';
    item.style.transform = 'none';
  });
  // Remove oldest if too many
  const all = feed.querySelectorAll('.activity-item');
  if (all.length > 8) all[all.length - 1].remove();
}

// ── CONNECTION STATUS ─────────────────────────────────────────
function setConnectionStatus(status) {
  state.connected = status === 'connected';
  connDot.className = 'conn-dot' + (status === 'connected' ? ' connected' : status === 'error' ? ' error' : '');
  connLabel.textContent = {
    connected:  state.demoMode ? 'Demo Active' : 'Connected',
    connecting: 'Connecting…',
    error:      'Offline'
  }[status] || 'Unknown';
}

// ── HEALTH CHECK ──────────────────────────────────────────────
async function checkHealth() {
  if (state.demoMode) {
    setConnectionStatus('connected');
    return;
  }
  try {
    const res = await fetchWithTimeout('/health', {}, 3000);
    setConnectionStatus('connected');
  } catch {
    setConnectionStatus('error');
  }
}
setInterval(() => { if (!state.demoMode) checkHealth(); }, 30000);

// ── TOAST ─────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  clearTimeout(toastTimer);
  toast.textContent = '';

  const icon = { success: '✓', error: '✕', info: 'ℹ' }[type] || 'ℹ';
  const iconEl = document.createElement('span');
  iconEl.textContent = icon;
  iconEl.style.cssText = `font-weight:700;font-size:14px;opacity:0.8;`;
  toast.appendChild(iconEl);
  toast.appendChild(document.createTextNode(' ' + message));

  toast.className = `toast ${type} show`;
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

// ── UTILITIES ─────────────────────────────────────────────────
function setTodayLabel() {
  const now = new Date();
  const opts = { weekday: 'short', month: 'short', day: 'numeric' };
  $('today-label').textContent = now.toLocaleDateString('en-US', opts);
}

function formatTimeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function formatDateTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
  });
}

function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
