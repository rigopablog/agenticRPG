(function () {
  'use strict';

  // Resolve API base from this script's own URL so the widget always points
  // to wherever it is served from (works locally and in production).
  const SCRIPT_SRC = document.currentScript && document.currentScript.src;
  const API_BASE = SCRIPT_SRC
    ? new URL(SCRIPT_SRC).origin
    : 'http://localhost:8000';

  // Prevent double-init
  if (window.__agentsHubLoaded) return;
  window.__agentsHubLoaded = true;

  /* ── Styles ─────────────────────────────────────────────────────────── */
  const css = `
    #ah-fab {
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 999998;
      background: #6366f1;
      color: #fff;
      border: none;
      border-radius: 50px;
      padding: 13px 20px;
      font-size: 14px;
      font-weight: 700;
      font-family: system-ui, sans-serif;
      cursor: pointer;
      box-shadow: 0 4px 24px rgba(99,102,241,.55);
      display: flex;
      align-items: center;
      gap: 8px;
      transition: transform .2s, box-shadow .2s;
      letter-spacing: .3px;
    }
    #ah-fab:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 32px rgba(99,102,241,.7);
    }
    #ah-fab .ah-fab-icon { font-size: 18px; line-height: 1; }

    #ah-overlay {
      position: fixed;
      inset: 0;
      z-index: 999999;
      background: rgba(0,0,0,.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity .25s;
    }
    #ah-overlay.ah-open {
      opacity: 1;
      pointer-events: all;
    }

    #ah-panel {
      background: #0f1117;
      border-radius: 16px;
      border: 1px solid #2d3148;
      box-shadow: 0 24px 80px rgba(0,0,0,.8);
      width: min(960px, 95vw);
      height: min(680px, 92vh);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transform: scale(.95) translateY(16px);
      transition: transform .25s;
    }
    #ah-overlay.ah-open #ah-panel {
      transform: scale(1) translateY(0);
    }

    #ah-panel-header {
      background: #131620;
      border-bottom: 1px solid #1e2235;
      padding: 14px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }
    #ah-panel-header .ah-logo {
      width: 32px; height: 32px;
      background: #6366f1;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 17px;
    }
    #ah-panel-header .ah-title {
      font-family: system-ui, sans-serif;
      font-weight: 700;
      font-size: 15px;
      color: #e2e8f0;
    }
    #ah-panel-header .ah-subtitle {
      font-family: system-ui, sans-serif;
      font-size: 11px;
      color: #64748b;
      margin-left: 4px;
    }
    #ah-close {
      margin-left: auto;
      background: #1e2235;
      border: none;
      color: #94a3b8;
      width: 28px; height: 28px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      display: flex; align-items: center; justify-content: center;
      transition: background .15s, color .15s;
    }
    #ah-close:hover { background: #dc2626; color: #fff; }

    #ah-iframe {
      flex: 1;
      border: none;
      width: 100%;
    }

    #ah-powered {
      background: #131620;
      border-top: 1px solid #1e2235;
      padding: 6px 16px;
      font-family: system-ui, sans-serif;
      font-size: 10px;
      color: #374151;
      text-align: right;
      flex-shrink: 0;
    }
    #ah-powered a { color: #6366f1; text-decoration: none; }
  `;

  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  /* ── FAB button ──────────────────────────────────────────────────────── */
  const fab = document.createElement('button');
  fab.id = 'ah-fab';
  fab.innerHTML = '<span class="ah-fab-icon">🤖</span> AI Agents';
  document.body.appendChild(fab);

  /* ── Overlay + Panel ─────────────────────────────────────────────────── */
  const overlay = document.createElement('div');
  overlay.id = 'ah-overlay';

  const panel = document.createElement('div');
  panel.id = 'ah-panel';

  const header = document.createElement('div');
  header.id = 'ah-panel-header';
  header.innerHTML = `
    <div class="ah-logo">🤖</div>
    <span class="ah-title">Agents Hub</span>
    <span class="ah-subtitle">23 agentes · Llama 3.3 70B</span>
    <button id="ah-close" title="Cerrar">✕</button>
  `;

  const iframe = document.createElement('iframe');
  iframe.id = 'ah-iframe';
  iframe.title = 'Agents Hub';
  // Load lazily — only set src when first opened
  iframe.dataset.src = API_BASE + '/';

  const powered = document.createElement('div');
  powered.id = 'ah-powered';
  powered.innerHTML = 'Powered by <a href="https://rpgdevelopment.com" target="_blank">RPG Development</a>';

  panel.appendChild(header);
  panel.appendChild(iframe);
  panel.appendChild(powered);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);

  /* ── Logic ───────────────────────────────────────────────────────────── */
  let loaded = false;

  function openPanel() {
    if (!loaded) {
      iframe.src = iframe.dataset.src;
      loaded = true;
    }
    overlay.classList.add('ah-open');
    document.body.style.overflow = 'hidden';
  }

  function closePanel() {
    overlay.classList.remove('ah-open');
    document.body.style.overflow = '';
  }

  fab.addEventListener('click', openPanel);
  document.getElementById('ah-close').addEventListener('click', closePanel);

  // Close on backdrop click
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePanel();
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePanel();
  });
})();
