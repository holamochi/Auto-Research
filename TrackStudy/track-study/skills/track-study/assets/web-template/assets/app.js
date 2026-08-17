(() => {
  'use strict';

  const data = window.TRACKSTUDY_DATA;
  const summary = document.querySelector('#summary');
  const status = document.querySelector('#graph-status');
  const dialog = document.querySelector('#detail-dialog');
  const dialogTitle = document.querySelector('#dialog-title');
  const dialogContent = document.querySelector('#dialog-content');
  const captionLayer = document.querySelector('#node-captions');

  if (!data || !Array.isArray(data.experiments) || typeof window.cytoscape !== 'function') {
    summary.textContent = 'TrackStudy data is missing. Run build_atlas.py before opening the atlas.';
    status.textContent = 'Build required';
    return;
  }

  const experiments = new Map(data.experiments.map((experiment) => [experiment.id, experiment]));
  const tracks = new Map(data.tracks.map((track) => [track.id, track]));
  const relations = data.relations || [];
  const captions = new Map();
  let activeTrack = 'all';
  let lastTap = { id: null, time: 0 };
  let captionFrame = 0;

  const create = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };

  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const graphColors = () => ({
    background: css('--bg'),
    panel: css('--panel'),
    text: css('--text'),
    muted: css('--muted'),
    border: css('--border-strong'),
    brand: css('--brand'),
    active: css('--active'),
    danger: css('--danger'),
  });

  const elements = [
    ...data.experiments.map((experiment) => ({
      group: 'nodes',
      data: {
        id: experiment.id,
        number: experiment.number,
        title: experiment.title,
        track: experiment.track,
        status: experiment.status,
        color: tracks.get(experiment.track)?.color || '#58a487',
      },
    })),
    ...relations.map((relation) => ({
      group: 'edges',
      data: {
        id: relation.id,
        source: relation.from,
        target: relation.to,
        label: relation.label,
        type: relation.type,
        kind: relation.kind,
        primary: relation.primary ? 1 : 0,
      },
      classes: relation.primary ? 'primary' : 'secondary',
    })),
  ];

  const cy = cytoscape({
    container: document.querySelector('#cy'),
    elements,
    minZoom: 0.18,
    maxZoom: 2.2,
    wheelSensitivity: 0.18,
    boxSelectionEnabled: false,
    autoungrabify: false,
    style: [],
  });

  function applyGraphTheme() {
    const colors = graphColors();
    cy.style()
      .selector('node')
      .style({
        width: 52,
        height: 34,
        shape: 'round-rectangle',
        'background-color': colors.panel,
        'border-color': colors.border,
        'border-width': 1.6,
        'border-style': 'dashed',
        label: 'data(number)',
        color: colors.text,
        'font-family': 'ui-monospace, SFMono-Regular, Menlo, monospace',
        'font-size': 12,
        'font-weight': 700,
        'text-valign': 'center',
        'text-halign': 'center',
        'overlay-opacity': 0,
      })
      .selector('node[status = "in-progress"]')
      .style({ 'border-color': colors.active, 'border-style': 'solid' })
      .selector('node[status = "blocked"]')
      .style({ 'border-color': colors.danger })
      .selector('node:selected')
      .style({
        'border-color': 'data(color)',
        'border-style': 'solid',
        'border-width': 3,
        'background-color': colors.panel,
      })
      .selector('node.search-match')
      .style({ 'border-color': colors.active, 'border-style': 'solid', 'border-width': 3 })
      .selector('edge')
      .style({
        width: 1.8,
        'line-color': colors.border,
        'target-arrow-color': colors.border,
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.75,
        'curve-style': 'bezier',
        label: 'data(label)',
        color: colors.muted,
        'font-size': 9,
        'font-weight': 600,
        'text-background-color': colors.background,
        'text-background-opacity': 0.9,
        'text-background-padding': 2,
        'text-rotation': 'none',
        'overlay-opacity': 0,
      })
      .selector('edge.secondary')
      .style({
        width: 1.2,
        'line-style': 'dashed',
        opacity: 0.72,
        'target-arrow-shape': 'none',
      })
      .selector('edge:selected')
      .style({
        width: 3,
        'line-color': colors.brand,
        'target-arrow-color': colors.brand,
        color: colors.text,
      })
      .update();
  }

  applyGraphTheme();

  function rootsFor(nodes) {
    const visibleIds = new Set(nodes.map((node) => node.id()));
    const incoming = new Set(
      cy.edges('.primary:visible')
        .filter((edge) => visibleIds.has(edge.source().id()) && visibleIds.has(edge.target().id()))
        .map((edge) => edge.target().id()),
    );
    return nodes.filter((node) => !incoming.has(node.id()));
  }

  function runLayout({ fit = true } = {}) {
    const visibleNodes = cy.nodes(':visible');
    if (!visibleNodes.length) return;
    const spacingFactor = window.innerWidth <= 520 ? 1.75 : window.innerWidth <= 900 ? 1.4 : 1.15;
    cy.layout({
      name: 'breadthfirst',
      directed: true,
      roots: rootsFor(visibleNodes),
      fit,
      padding: 56,
      spacingFactor,
      circle: false,
      grid: false,
      animate: false,
      maximal: true,
    }).run();
    scheduleCaptions();
  }

  function updateStatus() {
    status.textContent = `${cy.nodes(':visible').length} experiments · ${cy.edges(':visible').length} relations`;
  }

  function applyTrackFilter() {
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const visible = activeTrack === 'all' || node.data('track') === activeTrack;
        node.style('display', visible ? 'element' : 'none');
      });
      cy.edges().forEach((edge) => {
        const visible = edge.source().visible() && edge.target().visible();
        edge.style('display', visible ? 'element' : 'none');
      });
    });
    runLayout();
    updateStatus();
  }

  function buildCaptions() {
    data.experiments.forEach((experiment) => {
      const caption = create('div', 'node-caption', experiment.id);
      caption.dataset.nodeId = experiment.id;
      captionLayer.append(caption);
      captions.set(experiment.id, caption);
    });
  }

  function updateCaptions() {
    captionFrame = 0;
    cy.nodes().forEach((node) => {
      const caption = captions.get(node.id());
      if (!caption) return;
      const hidden = !node.visible();
      caption.classList.toggle('is-hidden', hidden);
      if (hidden) return;
      const position = node.renderedPosition();
      caption.style.left = `${position.x}px`;
      caption.style.top = `${position.y + node.renderedHeight() / 2}px`;
      caption.style.opacity = String(Math.min(1, Math.max(0.58, cy.zoom())));
    });
  }

  function scheduleCaptions() {
    if (captionFrame) return;
    captionFrame = requestAnimationFrame(updateCaptions);
  }

  buildCaptions();
  cy.on('render position pan zoom resize', scheduleCaptions);

  function badge(text) {
    return create('span', 'badge', text);
  }

  function showSummary(experiment) {
    summary.replaceChildren();
    summary.append(create('span', 'eyebrow', 'Experiment summary'));
    summary.append(create('h1', '', `${experiment.number} · ${experiment.title}`));
    summary.append(create('div', 'summary-id', experiment.id));
    const badges = create('div', 'badges');
    badges.append(badge(experiment.status), badge(tracks.get(experiment.track)?.label || experiment.track));
    summary.append(badges);
    [
      ['Current experiment', experiment.brief.experiment],
      ['What changed', experiment.brief.change],
      ['Conclusion', experiment.brief.conclusion],
    ].forEach(([title, text]) => {
      const card = create('section', 'summary-card');
      card.append(create('h3', '', title), create('p', '', text));
      summary.append(card);
    });
    const action = create('button', 'detail-action', 'Open full details');
    action.type = 'button';
    action.addEventListener('click', () => openDetails(experiment));
    summary.append(action);
  }

  function evidenceLink(evidence) {
    const anchor = create('a', 'evidence-link');
    if (evidence.type === 'local' || evidence.type === 'manifest') {
      anchor.href = new URL(`../${evidence.path}`, window.location.href).href;
      anchor.textContent = `${evidence.path}:${evidence.lineStart}-${evidence.lineEnd}`;
    } else if (evidence.url) {
      anchor.href = evidence.url;
      anchor.textContent = evidence.url;
    } else {
      anchor.removeAttribute('href');
      anchor.textContent = evidence.note || `${evidence.type} evidence unavailable locally`;
    }
    if (anchor.href) {
      anchor.target = '_blank';
      anchor.rel = 'noreferrer';
    }
    anchor.title = `${evidence.type} · ${evidence.claimPolicy}`;
    return anchor;
  }

  function detailSection(title, content) {
    const section = create('section', 'detail-section');
    section.append(create('h3', '', title), content);
    return section;
  }

  function openDetails(experiment) {
    dialogTitle.textContent = `${experiment.number} · ${experiment.title}`;
    dialogContent.replaceChildren();
    dialogContent.append(detailSection('Experiment', create('p', '', experiment.detail.experiment)));

    const changes = create('ul', 'detail-list');
    experiment.detail.changes.forEach((change) => {
      const predecessor = change.from ? `${change.from} · ` : '';
      changes.append(create('li', '', `${predecessor}${change.summary}`));
    });
    dialogContent.append(detailSection('Changes', changes));
    dialogContent.append(detailSection('Conclusion', create('p', '', experiment.detail.conclusion)));

    const caveats = create('ul', 'detail-list');
    experiment.detail.caveats.forEach((value) => caveats.append(create('li', '', value)));
    dialogContent.append(detailSection('Caveats', caveats));

    const related = relations.filter((relation) => relation.from === experiment.id || relation.to === experiment.id);
    if (related.length) {
      const relationList = create('ul', 'detail-list');
      related.forEach((relation) => {
        const direction = relation.from === experiment.id ? `→ ${relation.to}` : `${relation.from} →`;
        relationList.append(create('li', '', `${direction} · ${relation.label} [${relation.kind}]`));
      });
      dialogContent.append(detailSection('Relations', relationList));
    }

    const evidence = create('div', 'detail-list');
    experiment.evidence.forEach((item) => evidence.append(evidenceLink(item)));
    dialogContent.append(detailSection('Evidence', evidence));
    dialog.showModal();
  }

  cy.on('tap', 'node', (event) => {
    const experiment = experiments.get(event.target.id());
    if (!experiment) return;
    showSummary(experiment);
    const now = performance.now();
    if (lastTap.id === experiment.id && now - lastTap.time < 360) openDetails(experiment);
    lastTap = { id: experiment.id, time: now };
  });

  cy.on('tap', 'edge', (event) => {
    const relation = relations.find((item) => item.id === event.target.id());
    if (!relation) return;
    const from = experiments.get(relation.from);
    const to = experiments.get(relation.to);
    summary.replaceChildren();
    summary.append(create('span', 'eyebrow', 'Relationship'));
    summary.append(create('h1', '', relation.label));
    summary.append(create('p', 'summary-id', `${from?.id || relation.from} → ${to?.id || relation.to}`));
    const card = create('section', 'summary-card');
    card.append(create('h3', '', `${relation.kind} · ${relation.type}`));
    card.append(create('p', '', relation.primary ? 'Primary evolution edge' : 'Secondary or contextual relationship'));
    summary.append(card);
  });

  const trackFilter = document.querySelector('#track-filter');
  data.tracks.forEach((track) => {
    const option = document.createElement('option');
    option.value = track.id;
    option.textContent = track.label;
    trackFilter.append(option);
  });
  trackFilter.addEventListener('change', () => {
    activeTrack = trackFilter.value;
    applyTrackFilter();
  });

  document.querySelector('#fit').addEventListener('click', () => {
    cy.fit(cy.elements(':visible'), 56);
    scheduleCaptions();
  });

  const search = document.querySelector('#search');
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    cy.nodes().removeClass('search-match');
    if (query.length < 2) return;
    const matches = cy.nodes(':visible').filter((node) => {
      const experiment = experiments.get(node.id());
      const haystack = [
        experiment.id,
        experiment.title,
        experiment.brief.experiment,
        experiment.brief.change,
        experiment.brief.conclusion,
      ].join(' ').toLowerCase();
      return haystack.includes(query);
    });
    matches.addClass('search-match');
    if (matches.length === 1) {
      cy.animate({ center: { eles: matches }, zoom: Math.max(cy.zoom(), 1) }, { duration: 220 });
      showSummary(experiments.get(matches[0].id()));
    }
  });

  const themeButton = document.querySelector('#theme');
  const themeLabels = { system: 'Theme · Auto', light: 'Theme · Light', dark: 'Theme · Dark' };
  const applyTheme = (mode) => {
    const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
    const effective = mode === 'system' ? (prefersDark ? 'dark' : 'light') : mode;
    document.documentElement.dataset.themeMode = mode;
    document.documentElement.dataset.theme = effective;
    themeButton.textContent = themeLabels[mode];
    themeButton.setAttribute('aria-label', `Theme: ${mode}`);
    try { localStorage.setItem('trackstudy-theme', mode); } catch (_) {}
    applyGraphTheme();
  };
  themeButton.addEventListener('click', () => {
    const current = document.documentElement.dataset.themeMode || 'system';
    applyTheme(current === 'system' ? 'light' : current === 'light' ? 'dark' : 'system');
  });
  applyTheme(document.documentElement.dataset.themeMode || 'system');

  document.querySelector('#project-title').textContent = data.project.title;
  document.querySelector('#project-meta').textContent = `${data.project.description} · ${data.project.snapshotDate}`;
  document.title = `${data.project.title} · TrackStudy`;

  document.querySelector('#cy').addEventListener('keydown', (event) => {
    const selected = cy.nodes(':selected').first();
    if (event.key === 'Enter' && selected.nonempty()) {
      event.preventDefault();
      openDetails(experiments.get(selected.id()));
    }
  });
  window.addEventListener('resize', scheduleCaptions);
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if ((document.documentElement.dataset.themeMode || 'system') === 'system') applyTheme('system');
  });

  applyTrackFilter();
})();
