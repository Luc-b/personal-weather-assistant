import { useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function Card({ title, subtitle, children }) {
  return (
    <section className="card">
      <header className="cardHeader">
        <div className="cardTitleRow">
          <h3 className="cardTitle">{title}</h3>
          {subtitle ? <span className="pill">{subtitle}</span> : null}
        </div>
      </header>
      <div className="cardBody">{children}</div>
    </section>
  );
}

function KV({ label, value }) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div className="kv">
      <div className="kvLabel">{label}</div>
      <div className="kvValue">{value}</div>
    </div>
  );
}

function ChipList({ items }) {
  if (!items || items.length === 0) return <div className="muted">—</div>;
  return (
    <div className="chips">
      {items.map((x, i) => (
        <span key={i} className="chip">
          {x}
        </span>
      ))}
    </div>
  );
}

function HostAvatar({ size = 44 }) {
  return (
    <div
      className="hostAvatar"
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 64 64" width={size} height={size}>
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#7c3aed" />
            <stop offset="1" stopColor="#22c55e" />
          </linearGradient>
        </defs>

        {/* soft background */}
        <circle cx="32" cy="32" r="30" fill="url(#g)" opacity="0.18" />
        <circle cx="32" cy="32" r="26" fill="#ffffff" opacity="0.85" />

        {/* head */}
        <circle cx="32" cy="30" r="12" fill="#fde7d0" />
        {/* hair */}
        <path
          d="M21 30c2-10 20-13 26-2 0-9-6-16-15-16-7 0-12 4-11 18z"
          fill="#111827"
          opacity="0.85"
        />
        {/* eyes */}
        <circle cx="28" cy="31" r="1.6" fill="#111827" />
        <circle cx="36" cy="31" r="1.6" fill="#111827" />
        {/* smile */}
        <path d="M28 36c2.5 2 5.5 2 8 0" stroke="#111827" strokeWidth="2" fill="none" strokeLinecap="round" />

        {/* suit */}
        <path
          d="M18 56c3-10 11-16 14-16h0c3 0 11 6 14 16"
          fill="#e5e7eb"
        />
        <path
          d="M26 41l6 5 6-5"
          fill="none"
          stroke="#2563eb"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}


export default function App() {
  const [city, setCity] = useState("Zagreb");
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [weather, setWeather] = useState(null);
  const [rec, setRec] = useState(null);

  const canSubmit = useMemo(() => {
    return city.trim().length > 0 && /^\d{4}-\d{2}-\d{2}$/.test(date);
  }, [city, date]);

  async function apiGet(path, params) {
    const url = new URL(API_BASE + path);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

    const res = await fetch(url.toString());
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body?.detail || `Request failed (${res.status})`);
    return body;
  }

  async function onRecommend() {
    if (!canSubmit) return;

    setLoading(true);
    setError("");

    try {
      const [w, r] = await Promise.all([
        apiGet("/forecast", { city: city.trim(), date }),
        apiGet("/recommend", { city: city.trim(), date }),
      ]);
      setWeather(w);
      setRec(r);
    } catch (e) {
      setError(e?.message || "Unknown error");
      setWeather(null);
      setRec(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <header className="topHeader">
          <div>
            <h1 className="title">Personal Weather Assistant</h1>
            <p className="subtitle">
              Clean forecast summary + friendly AI recommendations.
            </p>
          </div>
          <div className="badge">
            OpenWeatherMap <span className="dot">•</span> Groq
          </div>
        </header>

        <section className="panel">
          <div className="formRow">
            <div className="field">
              <label className="label">City</label>
              <input
                className="input"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="e.g. Zagreb"
              />
            </div>

            <div className="field">
              <label className="label">Date</label>
              <input
                className="input"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>

            <button className="button" onClick={onRecommend} disabled={!canSubmit || loading}>
              {loading ? "Working…" : "Recommend"}
            </button>
          </div>

          <div className="hint">
            Forecast is available up to ~5 days ahead (OpenWeather 5-day / 3-hour).
          </div>

          {error ? (
            <div className="alert">
              <div className="alertTitle">Couldn’t fetch results</div>
              <div className="alertBody">{error}</div>
            </div>
          ) : null}
        </section>

        {weather || rec ? (
          <div className="grid">
            <Card
              title="Weather"
              subtitle={weather ? `${weather.city} (${weather.country})` : ""}
            >
              {weather ? (
                <div className="kvGrid">
                  <KV label="Date" value={String(weather.date)} />
                  <KV label="Condition" value={weather.description} />
                  <KV label="Temp" value={`${weather.temperature_c} °C`} />
                  <KV
                    label="Feels like"
                    value={weather.feels_like_c != null ? `${weather.feels_like_c} °C` : null}
                  />
                  <KV
                    label="Humidity"
                    value={weather.humidity_percent != null ? `${weather.humidity_percent}%` : null}
                  />
                  <KV
                    label="Wind"
                    value={weather.wind_speed_mps != null ? `${weather.wind_speed_mps} m/s` : null}
                  />
                  <KV
                    label="Precip chance"
                    value={
                      weather.precipitation_probability != null
                        ? `${Math.round(weather.precipitation_probability * 100)}%`
                        : null
                    }
                  />
                </div>
              ) : (
                <div className="muted">No forecast loaded.</div>
              )}
            </Card>

            <Card
            title={
              <div className="hostTitle">
                <HostAvatar />
                <div>
                  <div className="hostTitleText">Skye</div>
                  <div className="hostTitleSub">Your friendly forecast guide</div>
                </div>
              </div>
            }
          >
              {rec ? (
                <div className="host">
                  <div className="hostLead">
                    <b>
                      {weather
                        ? `${weather.city} — ${String(weather.date)}:`
                        : "Today:"}
                    </b>{" "}
                    {rec.summary}
                  </div>

                  <div className="hostSection">
                    <div className="hostLabel">How to dress</div>
                    <div className="hostRow">
                      <div className="hostCol">
                        <div className="miniLabel">Top</div>
                        <ChipList items={rec.outfit?.top} />
                      </div>
                      <div className="hostCol">
                        <div className="miniLabel">Bottom</div>
                        <ChipList items={rec.outfit?.bottom} />
                      </div>
                    </div>

                    <div className="hostRow">
                      <div className="hostCol">
                        <div className="miniLabel">Shoes</div>
                        <ChipList items={rec.outfit?.shoes} />
                      </div>
                      <div className="hostCol">
                        <div className="miniLabel">Outerwear</div>
                        <ChipList items={rec.outfit?.outerwear} />
                      </div>
                    </div>

                    <div className="hostRow">
                      <div className="hostCol">
                        <div className="miniLabel">Accessories / bring</div>
                        <ChipList items={rec.outfit?.accessories} />
                      </div>
                    </div>
                  </div>

                  <div className="hostSection">
                    <div className="hostLabel">Best activities</div>
                    <div className="hostRow">
                      <div className="hostCol">
                        <div className="miniLabel">Outdoor</div>
                        <ChipList items={rec.activities?.outdoor} />
                      </div>
                      <div className="hostCol">
                        <div className="miniLabel">Indoor</div>
                        <ChipList items={rec.activities?.indoor} />
                      </div>
                    </div>
                  </div>

                  <div className="hostSection">
                    <div className="hostLabel">Warnings & tips</div>
                    <div className="hostRow">
                      <div className="hostCol">
                        <div className="miniLabel">Warnings</div>
                        <ChipList items={rec.warnings} />
                      </div>
                      <div className="hostCol">
                        <div className="miniLabel">Tips</div>
                        <ChipList items={rec.tips} />
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="muted">—</div>
              )}
            </Card>
          </div>
        ) : (
          <div className="empty">
            Enter a city and date, then click <b>Recommend</b>.
          </div>
        )}

        <footer className="footer">
          Tip: try a date within the next 1–5 days for the selected city.
        </footer>
      </div>
    </div>
  );
}
