import React from 'react';
import './App.css';
import { content } from '../../content';

type WaterStatus = {
  liters: number;
  displayLiters: number;
  overflow: boolean;
  activeRows: number;
  pool: PoolStatus;
  displayMode: 'water' | 'rainbow' | 'standby' | 'off';
};

type PoolLevel = 'ok' | 'warning' | 'critical' | null;

type PoolMetric = {
  status: PoolLevel;
  value: number | null;
  updatedAt: string | null;
};

type PoolStatus = {
  ph: PoolMetric;
  orp: PoolMetric;
};

const colors = {
  off: 'rgb(23, 36, 43)',
  outline: 'rgb(190, 235, 255)',
  text: 'rgb(52, 178, 255)',
  overflow: 'rgb(255, 45, 64)',
  poolOk: 'rgb(38, 102, 255)',
  poolWarning: 'rgb(255, 191, 0)',
  poolCritical: 'rgb(255, 45, 64)',
  low: 'rgb(0, 72, 145)',
  mid: 'rgb(0, 132, 220)',
  high: 'rgb(38, 186, 255)',
  foam: 'rgb(182, 244, 255)',
};

const bucket = {
  left: 12,
  right: 16,
  innerLeft: 13,
  innerRight: 15,
};

const poolPixels = {
  ph: { x: 0, y: 6 },
  orp: { x: 1, y: 6 },
};

const digits: Record<string, string[]> = {
  '0': ['111', '101', '101', '101', '111'],
  '1': ['010', '110', '010', '010', '111'],
  '2': ['111', '001', '111', '100', '111'],
  '3': ['111', '001', '111', '001', '111'],
  '4': ['101', '101', '111', '001', '001'],
  '5': ['111', '100', '111', '001', '111'],
  '6': ['111', '100', '111', '101', '111'],
  '7': ['111', '001', '010', '010', '010'],
  '8': ['111', '101', '111', '101', '111'],
  '9': ['111', '101', '111', '001', '111'],
};

function activeRowsForLiters(liters: number) {
  if (liters <= 0) return 0;
  return Math.min(5, Math.floor((liters - 1) / 200) + 1);
}

function displayLitersFor(liters: number) {
  return Math.min(999, Math.max(0, Math.floor(liters)));
}

function poolColor(status: PoolLevel) {
  if (status === 'ok') return colors.poolOk;
  if (status === 'warning') return colors.poolWarning;
  if (status === 'critical') return colors.poolCritical;
  return null;
}

function previewPixels(liters: number, wavePhase: number, pool: PoolStatus) {
  const activeRows = activeRowsForLiters(liters);
  const displayLiters = displayLitersFor(liters);
  const textColor = liters > 999 ? colors.overflow : colors.text;
  const pixels = Array.from({ length: 17 * 7 }, () => null as string | null);
  const setPixel = (x: number, y: number, color: string) => { pixels[y * 17 + x] = color; };

  String(displayLiters).padStart(3, ' ').split('').forEach((digit, digitIndex) => {
    if (digit === ' ') return;
    const xOffset = digitIndex * 4;
    digits[digit].forEach((row, y) => {
      row.split('').forEach((cell, x) => {
        if (cell === '1') setPixel(xOffset + x, y + 1, textColor);
      });
    });
  });

  for (let x = bucket.left; x <= bucket.right; x += 1) setPixel(x, 6, colors.outline);
  for (let y = 1; y <= 6; y += 1) {
    setPixel(bucket.left, y, colors.outline);
    setPixel(bucket.right, y, colors.outline);
  }

  if (activeRows === 0) return pixels;

  const surfaceY = 6 - activeRows;
  for (let x = bucket.innerLeft; x <= bucket.innerRight; x += 1) {
    for (let y = 5; y >= surfaceY; y -= 1) {
      const shimmer = (x + wavePhase) % 4 === 0;
      if (y === surfaceY) setPixel(x, y, shimmer ? colors.foam : colors.high);
      else if (y >= 4) setPixel(x, y, colors.low);
      else setPixel(x, y, colors.mid);
    }
  }

  const phColor = poolColor(pool.ph.status);
  const orpColor = poolColor(pool.orp.status);
  if (phColor) setPixel(poolPixels.ph.x, poolPixels.ph.y, phColor);
  if (orpColor) setPixel(poolPixels.orp.x, poolPixels.orp.y, orpColor);

  return pixels;
}

function WaterPreview({ liters, pool }: { liters: number; pool: PoolStatus }) {
  const [wavePhase, setWavePhase] = React.useState(0);

  React.useEffect(() => {
    const interval = window.setInterval(() => setWavePhase((phase) => (phase + 1) % 4), 320);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="matrix-preview" aria-label={content.panel.waterAriaLabel(liters)}>
      {previewPixels(liters, wavePhase, pool).map((color, index) => (
        <span
          className={`matrix-dot${color ? ' lit' : ''}`}
          key={index}
          style={color ? { backgroundColor: color, color } : undefined}
        />
      ))}
    </div>
  );
}

const Navigation: React.FunctionComponent<{ view: 'home' | 'docs'; setView: (view: 'home' | 'docs') => void }> = ({ view, setView }) => (
  <nav className="app-nav" aria-label={content.navigation.ariaLabel}>
    <a className={view === 'home' ? 'active' : ''} href="#" onClick={() => setView('home')}>{content.navigation.home}</a>
    <a className={view === 'docs' ? 'active' : ''} href="#api-docs" onClick={() => setView('docs')}>{content.navigation.apiDocs}</a>
  </nav>
);

const ApiDocs: React.FunctionComponent = () => (
  <section className="docs-panel">
    <header className="docs-header">
      <span className="status-kicker">{content.appName}</span>
      <h1>{content.docs.title}</h1>
      <p>{content.docs.description}</p>
    </header>
    <div className="docs-table" role="table" aria-label={content.docs.title}>
      <div className="docs-row docs-row-header" role="row">
        <span role="columnheader">{content.docs.methodLabel}</span>
        <span role="columnheader">{content.docs.endpointLabel}</span>
        <span role="columnheader">{content.docs.requestLabel}</span>
        <span role="columnheader">{content.docs.descriptionLabel}</span>
      </div>
      {content.docs.endpoints.map((endpoint) => (
        <div className="docs-row" role="row" key={endpoint.endpoint}>
          <span className="method-list" role="cell">
            {endpoint.methods.map((method) => <code key={method}>{method}</code>)}
          </span>
          <code className="endpoint" role="cell">{endpoint.endpoint}</code>
          <code className="request-body" role="cell">{endpoint.request}</code>
          <span role="cell">{endpoint.description}</span>
        </div>
      ))}
    </div>
  </section>
);

export function App() {
  const [status, setStatus] = React.useState<WaterStatus>({
    liters: 0,
    displayLiters: 0,
    overflow: false,
    activeRows: 0,
    pool: {
      ph: { status: null, value: null, updatedAt: null },
      orp: { status: null, value: null, updatedAt: null },
    },
    displayMode: 'water',
  });
  const [liters, setLiters] = React.useState(0);
  const [message, setMessage] = React.useState('');
  const [error, setError] = React.useState(false);
  const [view, setView] = React.useState<'home' | 'docs'>(() => window.location.hash === '#api-docs' ? 'docs' : 'home');

  const applyStatus = React.useCallback((nextStatus: WaterStatus) => {
    setStatus(nextStatus);
    setLiters(nextStatus.liters);
  }, []);

  const refresh = React.useCallback(async () => {
    const response = await fetch('/api/status');
    if (response.ok) applyStatus(await response.json());
  }, [applyStatus]);

  React.useEffect(() => { refresh(); }, [refresh]);
  React.useEffect(() => {
    const handleHashChange = () => setView(window.location.hash === '#api-docs' ? 'docs' : 'home');
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const post = async (endpoint: string, body: object) => {
    setMessage('');
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const result = await response.json();
    if (!response.ok) {
      setError(true);
      setMessage(content.panel.apiError(result.error ?? response.statusText));
      return;
    }
    setError(false);
    applyStatus(result);
  };

  const submitWater = async () => {
    await post('/api/water', { liters });
  };

  if (view === 'docs') {
    return (
      <main className="app-shell">
        <Navigation view={view} setView={setView} />
        <ApiDocs />
      </main>
    );
  }

  return (
    <main className="app-shell">
      <Navigation view={view} setView={setView} />
      <section className="status-panel">
        <div className="status-led"><WaterPreview liters={status.liters} pool={status.pool} /></div>
        <div className="status-copy">
          <span className="status-kicker">{content.appName}</span>
          <h1>{status.liters}</h1>
          <p>{content.panel.statusSummary(status.activeRows, status.displayMode, status.overflow)}</p>
          <p className="pool-summary">
            {content.panel.poolSummary(status.pool.ph.status, status.pool.ph.value, status.pool.orp.status, status.pool.orp.value)}
          </p>
        </div>
      </section>

      <section className="control-panel">
        <h2>{content.panel.waterSection}</h2>
        <label htmlFor="liters">{content.panel.litersLabel(liters)}</label>
        <input
          id="liters"
          type="range"
          min="0"
          max="999"
          value={Math.min(liters, 999)}
          onChange={(event) => setLiters(Number(event.target.value))}
        />
        <div className="number-row">
          <input
            aria-label={content.panel.litersInputLabel}
            type="number"
            min="0"
            value={liters}
            onChange={(event) => setLiters(Math.max(0, Number(event.target.value)))}
          />
          <button onClick={submitWater}>{content.panel.waterSubmit}</button>
        </div>
        {message && (
          <p className={`form-message${error ? ' error' : ' success'}`} role="status">
            {message}
          </p>
        )}
      </section>

      <section className="control-panel">
        <h2>{content.panel.displaySection}</h2>
        <div className="button-row">
          <button onClick={() => post('/api/rainbow', {})}>{content.panel.rainbow}</button>
          <button onClick={() => post('/api/standby', {})}>{content.panel.standby}</button>
          <button onClick={() => post('/api/off', {})}>{content.panel.off}</button>
        </div>
      </section>
    </main>
  );
}
