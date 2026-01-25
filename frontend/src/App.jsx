import './App.css'
import { useEffect, useMemo, useState } from 'react'
import { api } from './api'

function App() {
  const payload = useMemo(
    () => ({
      schema_version: '1.0',
      user_context: {
        user_id: 'alex_demo',
        currency: 'USD',
        timezone: 'America/Los_Angeles',
      },
      period: {
        start_date: '2025-01-01',
        end_date: '2025-01-31',
      },
      income: { monthly_income: 2200.0, confidence: 0.7 },
      spending_summary: {
        total_spend: 1874.32,
        transaction_count: 126,
        category_totals: [
          { category: 'Food & Drink', amount: 510.25, transaction_count: 34 },
          { category: 'Coffee', amount: 142.1, transaction_count: 22 },
          { category: 'Subscriptions', amount: 89.0, transaction_count: 6 },
        ],
        top_merchants: [
          {
            merchant: 'Starbucks',
            amount: 96.4,
            transaction_count: 14,
            category_hint: 'Coffee',
          },
          {
            merchant: 'DoorDash',
            amount: 310.0,
            transaction_count: 8,
            category_hint: 'Food & Drink',
          },
        ],
        silent_spenders: [
          {
            label: 'Coffee runs',
            category: 'Coffee',
            avg_amount: 6.46,
            transaction_count: 22,
            amount: 142.1,
          },
        ],
        recurring_merchants: [
          {
            merchant: 'Spotify',
            category_hint: 'Subscriptions',
            amount_per_period: 11.99,
            cadence: 'monthly',
            last_charge_date: '2025-01-18',
            confidence: 0.85,
          },
        ],
      },
      constraints: { tip_count: 3, flashcard_count: 5 },
    }),
    [],
  )

  const [tips, setTips] = useState(null)
  const [cards, setCards] = useState(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [bypassPrecomputed, setBypassPrecomputed] = useState(false)

  async function loadAll({ bypass } = { bypass: false }) {
    setLoading(true)
    setErr(null)
    try {
      const headers = bypass ? { 'X-AI-Bypass-Precomputed': '1' } : {}
      const [tipsRes, cardsRes] = await Promise.all([
        api.post('/ai/savings-tips', payload, { headers }),
        api.post('/ai/flashcards', payload, { headers }),
      ])
      setTips(tipsRes.data)
      setCards(cardsRes.data)
    } catch (e) {
      setErr(e?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll({ bypass: false })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="app">
      <header className="hero">
        <div className="brand">
          <div className="mark" aria-hidden="true">
            FS
          </div>
          <div className="titleblock">
            <h1>FinWise</h1>
            <p className="subtitle">
              AI spending coach + gamified flashcards + micro-savings (demo mode ready)
            </p>
          </div>
        </div>

        <div className="controls">
          <div className="meta">
            <div className="pill">User: {payload.user_context.user_id}</div>
            <div className="pill">
              Period: {payload.period.start_date} → {payload.period.end_date}
            </div>
          </div>

          <div className="actions">
            <label className="toggle">
              <input
                type="checkbox"
                checked={bypassPrecomputed}
                onChange={(e) => setBypassPrecomputed(e.target.checked)}
              />
              <span>Try live Gemini (bypass precomputed)</span>
            </label>
            <button
              className="btn primary"
              onClick={() => loadAll({ bypass: bypassPrecomputed })}
              disabled={loading}
            >
              {loading ? 'Loading…' : 'Refresh'}
            </button>
          </div>
        </div>
      </header>

      {err ? <div className="banner error">Error: {err}</div> : null}

      <main className="grid">
        <section className="panel">
          <div className="panelHead">
            <h2>Spending Snapshot</h2>
            <div className="muted">
              Total: ${payload.spending_summary.total_spend.toFixed(2)} • Txns:{' '}
              {payload.spending_summary.transaction_count}
            </div>
          </div>

          <div className="list">
            {payload.spending_summary.category_totals.map((c) => (
              <div className="row" key={c.category}>
                <div className="rowLeft">
                  <div className="rowTitle">{c.category}</div>
                  <div className="rowSub">{c.transaction_count} txns</div>
                </div>
                <div className="rowRight">${c.amount.toFixed(2)}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panelHead">
            <h2>AI Savings Tips</h2>
            <div className="muted">
              {tips ? (
                <>
                  Source: <b>{tips.meta.generated_by}</b> • fallback_used:{' '}
                  <b>{String(tips.meta.fallback_used)}</b>
                </>
              ) : (
                '—'
              )}
            </div>
          </div>

          {!tips ? (
            <div className="skeleton">Waiting for response…</div>
          ) : (
            <div className="cards">
              {tips.tips.map((t) => (
                <article className="tip" key={t.id}>
                  <div className="tipTop">
                    <div className="tipTitle">{t.title}</div>
                    <div className="tipAmt">${Number(t.estimated_monthly_savings).toFixed(0)}/mo</div>
                  </div>
                  <div className="tipBody">{t.recommendation}</div>
                  <div className="tipFoot">
                    <div className="chip">confidence: {Math.round(t.confidence * 100)}%</div>
                    {t.category_targets?.length ? (
                      <div className="chip">{t.category_targets.join(', ')}</div>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="panel span2">
          <div className="panelHead">
            <h2>Flashcards</h2>
            <div className="muted">
              {cards ? (
                <>
                  Source: <b>{cards.meta.generated_by}</b> • fallback_used:{' '}
                  <b>{String(cards.meta.fallback_used)}</b>
                </>
              ) : (
                '—'
              )}
            </div>
          </div>

          {!cards ? (
            <div className="skeleton">Waiting for response…</div>
          ) : (
            <div className="flashGrid">
              {cards.flashcards.map((c) => (
                <article className="flash" key={c.id}>
                  <div className="flashMeta">
                    <span className="chip">{c.type}</span>
                    <span className="chip">{c.skill}</span>
                    <span className="chip">{c.difficulty}</span>
                  </div>
                  <div className="flashQ">{c.question}</div>
                  <div className="flashOpts">
                    {c.options.map((o) => (
                      <div className="opt" key={o}>
                        {o}
                      </div>
                    ))}
                  </div>
                  <div className="flashAns">
                    <div className="muted">Answer</div>
                    <div className="ans">{c.answer}</div>
                    <div className="exp">{c.explanation}</div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <span className="muted">
          Tip: run backend on port 5050 and start frontend dev server; Vite proxies `/api` → backend.
        </span>
      </footer>
    </div>
  )
}

export default App
