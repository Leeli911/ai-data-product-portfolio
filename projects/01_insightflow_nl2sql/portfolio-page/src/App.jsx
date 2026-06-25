import { useRef, useState } from 'react'
import './styles.css'

const DEMO_QUESTION = 'Why did GMV drop in Chaoyang this week?'

const DEMO_RESULT = {
  intent: [
    ['Analysis type', 'Drop reason analysis'],
    ['Metric', 'GMV'],
    ['Scope', 'Chaoyang District'],
    ['Comparison', 'Current week vs previous week'],
  ],
  plan: [
    'Validate the GMV decline across comparable seven-day windows.',
    'Decompose GMV into order volume and average order value.',
    'Inspect active users, peak-hour orders, and coupon cost as supporting signals.',
  ],
  sql: `WITH weekly_metrics AS (
  SELECT
    CASE
      WHEN order_date >= DATE '2026-06-17' THEN 'current_week'
      ELSE 'previous_week'
    END AS period,
    SUM(gmv) AS gmv,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT user_id) AS active_users
  FROM fact_orders
  JOIN dim_district USING (district_id)
  WHERE district_name = 'Chaoyang'
    AND order_date BETWEEN DATE '2026-06-10' AND DATE '2026-06-23'
  GROUP BY 1
)
SELECT * FROM weekly_metrics ORDER BY period;`,
  queryResult: [
    { metric: 'GMV', current: '¥680,309', previous: '¥751,318', change: '−9.5%' },
    { metric: 'Orders', current: '6,776', previous: '7,481', change: '−9.4%' },
    { metric: 'Active users', current: '6,174', previous: '6,133', change: '+0.7%' },
    { metric: 'Avg. order value', current: '¥100.40', previous: '¥100.43', change: '0.0%' },
  ],
  facts: [
    'GMV decreased 9.5%, from ¥751,318 to ¥680,309.',
    'Order volume decreased 9.4%, while average order value remained nearly flat.',
    'Active users increased 0.7%, so the decline is not explained by user reach alone.',
  ],
  interpretations: [
    'Order volume moved in the same direction and at nearly the same rate as GMV, making it the strongest observed associated factor.',
    'Stable average order value suggests basket size was not a material contributor in this comparison window.',
  ],
  limitations: [
    'The observed relationships are correlational and do not establish causality.',
    'Inventory, weather, competitor activity, and marketing exposure are not available in the current dataset.',
    'The result is valid only for this controlled scenario and its fixed schema.',
  ],
  structuralCompleteness: '0.90',
}

const TECHNOLOGIES = [
  'Python',
  'DuckDB',
  'Pydantic',
  'Streamlit',
  'SQL Guardrails',
]

const VALIDATION_GATES = [
  'schema validation passed',
  'SQL execution validated',
  'comparison window verified',
]

const PIPELINE = [
  { label: 'Business Question', tag: 'constrained' },
  { label: 'Intent', tag: 'inspectable' },
  { label: 'Plan', tag: 'inspectable' },
  { label: 'SQL', tag: 'validated' },
  { label: 'Execution', tag: 'validated' },
  { label: 'Insight', tag: 'constrained' },
  { label: 'Structural Completeness', tag: 'inspectable' },
]

const CONTRIBUTIONS = [
  {
    number: '01',
    title: 'The system enforces evidence decomposition.',
    text: 'Every analytical response must separate observed facts, bounded interpretations, and explicit limitations with traceable evidence links.',
  },
  {
    number: '02',
    title: 'The system represents uncertainty explicitly.',
    text: 'Missing variables and causal limits remain visible, while structural completeness measures coverage rather than answer probability.',
  },
  {
    number: '03',
    title: 'The pipeline requires stage-level verification.',
    text: 'Intent, plan, SQL, execution, and evidence linkage must pass inspectable gates before an interpretation is presented.',
  },
  {
    number: '04',
    title: 'The execution layer permits only schema-grounded SQL.',
    text: 'Read-only queries are constrained to known tables and columns, independently validated, and executed against the controlled schema.',
  },
]

function DemoSection({ question, setQuestion, status, runAnalysis, demoRef }) {
  const isRunning = status === 'running'
  const hasResult = status === 'success'

  return (
    <section className="section demo-section" id="demo" ref={demoRef}>
      <div className="section-heading demo-heading">
        <div>
          <p className="eyebrow">System demo</p>
          <h2 className="display">Inspect the analysis trail</h2>
        </div>
        <p className="section-intro">
          An auditable, deterministic walkthrough of one controlled GMV analysis scenario.
        </p>
      </div>

      <div className="demo-shell">
        <form className="question-form" onSubmit={runAnalysis}>
          <label htmlFor="business-question">Business Question</label>
          <div className="question-row">
            <input
              id="business-question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a structured business question"
              aria-describedby={status === 'empty' ? 'question-error' : undefined}
            />
            <button className="button button-primary" type="submit" disabled={isRunning}>
              {isRunning ? 'Analyzing…' : 'Run Analysis'}
            </button>
          </div>
          {status === 'empty' && (
            <p className="form-error" id="question-error" role="alert">
              Enter a business question to run the controlled demonstration.
            </p>
          )}
          <p className="form-note">
            Controlled demonstration. Every non-empty input returns the same fixed result.
          </p>
        </form>

        {!hasResult && (
          <div className={`demo-idle ${isRunning ? 'is-running' : ''}`} aria-live="polite">
            <div>
              <span className="idle-index">01</span>
              <span>Intent</span>
            </div>
            <div>
              <span className="idle-index">02</span>
              <span>Plan</span>
            </div>
            <div>
              <span className="idle-index">03</span>
              <span>Validated SQL</span>
            </div>
            <div>
              <span className="idle-index">04</span>
              <span>Evidence</span>
            </div>
          </div>
        )}

        {hasResult && (
          <div className="analysis-output" aria-live="polite">
            <div className="output-meta">
              <span>Controlled demonstration</span>
              <span>Completed deterministically</span>
            </div>

            <div className="output-grid">
              <div className="trace-column">
                <article className="output-card">
                  <h3>Intent</h3>
                  <dl className="intent-grid">
                    {DEMO_RESULT.intent.map(([term, value]) => (
                      <div key={term}>
                        <dt>{term}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                </article>

                <article className="output-card">
                  <h3>Analysis Plan</h3>
                  <ol className="plan-list">
                    {DEMO_RESULT.plan.map((step, index) => (
                      <li key={step}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <p>{step}</p>
                      </li>
                    ))}
                  </ol>
                </article>

                <article className="output-card code-card">
                  <div className="card-title-row">
                    <h3>SQL Query</h3>
                    <span className="status-badge">Validated read-only</span>
                  </div>
                  <pre>
                    <code>{DEMO_RESULT.sql}</code>
                  </pre>
                </article>

                <article className="output-card result-card">
                  <h3>Query Result</h3>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th>Current week</th>
                          <th>Previous week</th>
                          <th>Change</th>
                        </tr>
                      </thead>
                      <tbody>
                        {DEMO_RESULT.queryResult.map((row) => (
                          <tr key={row.metric}>
                            <th>{row.metric}</th>
                            <td>{row.current}</td>
                            <td>{row.previous}</td>
                            <td className={row.change.startsWith('−') ? 'negative' : ''}>
                              {row.change}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </article>

                <article className="output-card validation-card">
                  <div className="card-title-row">
                    <h3>Validation Gates</h3>
                    <span className="status-badge">All gates passed</span>
                  </div>
                  <ol className="validation-list">
                    {VALIDATION_GATES.map((gate, index) => (
                      <li key={gate}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <strong>{gate}</strong>
                      </li>
                    ))}
                  </ol>
                </article>
              </div>

              <aside className="evidence-column">
                <article className="confidence-card">
                  <div>
                    <p className="eyebrow">Schema and evidence coverage</p>
                    <h3>Structural Completeness Score</h3>
                  </div>
                  <strong>{DEMO_RESULT.structuralCompleteness}</strong>
                  <div className="confidence-bar" aria-hidden="true">
                    <span />
                  </div>
                  <p>
                    Measures verified schema coverage, execution validity, comparison-window integrity, and evidence linkage. It is not a probability of correctness.
                  </p>
                </article>

                <article className="evidence-card facts-card">
                  <p className="evidence-type">Observed evidence</p>
                  <h3>Facts</h3>
                  <ul>
                    {DEMO_RESULT.facts.map((fact) => (
                      <li key={fact}>{fact}</li>
                    ))}
                  </ul>
                </article>

                <article className="evidence-card">
                  <p className="evidence-type">Reasoned from facts</p>
                  <h3>Interpretations</h3>
                  <div className="inference-boundary">
                    <span>bounded inference space</span>
                    <p>
                      Interpretations are bounded by observed metrics available in the controlled schema.
                    </p>
                  </div>
                  <ul>
                    {DEMO_RESULT.interpretations.map((interpretation) => (
                      <li key={interpretation}>{interpretation}</li>
                    ))}
                  </ul>
                </article>

                <article className="evidence-card limitation-card">
                  <p className="evidence-type">Uncertainty boundary</p>
                  <h3>Limitations</h3>
                  <ul>
                    {DEMO_RESULT.limitations.map((limitation) => (
                      <li key={limitation}>{limitation}</li>
                    ))}
                  </ul>
                </article>
              </aside>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

function Architecture() {
  return (
    <section className="section architecture-section" id="architecture">
      <div className="section-heading architecture-heading">
        <div>
          <p className="eyebrow">Architecture</p>
          <h2 className="display">System architecture</h2>
        </div>
        <p className="section-intro">
          Each transition leaves an auditable artifact. Validated, constrained, and inspectable stages stop unsupported claims before insight generation.
        </p>
      </div>
      <div className="pipeline" aria-label="Text2Analytics system pipeline">
        {PIPELINE.map((stage, index) => (
          <div className="pipeline-item" key={stage.label}>
            <span className="pipeline-index">{String(index + 1).padStart(2, '0')}</span>
            <span className="pipeline-node">
              <span>{stage.label}</span>
              <span className="pipeline-tag">{stage.tag}</span>
            </span>
            {index < PIPELINE.length - 1 && <span className="pipeline-arrow">→</span>}
          </div>
        ))}
      </div>
      <div className="architecture-note">
        <span>Typed intermediate states</span>
        <span>Independent SQL validation</span>
        <span>Failure-aware orchestration</span>
      </div>
    </section>
  )
}

function Contributions() {
  return (
    <section className="section contributions-section" id="contributions">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Research contribution</p>
          <h2 className="display">Key contributions</h2>
        </div>
        <p className="section-intro">
          System-level claims encoded as enforceable constraints, not aspirational interface principles.
        </p>
      </div>
      <div className="contribution-grid">
        {CONTRIBUTIONS.map((contribution) => (
          <article className="contribution-card" key={contribution.number}>
            <span>{contribution.number}</span>
            <h3>{contribution.title}</h3>
            <p>{contribution.text}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default function App() {
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState('idle')
  const demoRef = useRef(null)

  const updateQuestion = (value) => {
    setQuestion(value)
    if (status === 'empty') setStatus('idle')
  }

  const runAnalysis = (event) => {
    event.preventDefault()
    if (!question.trim()) {
      setStatus('empty')
      return
    }

    setStatus('running')
    window.setTimeout(() => setStatus('success'), 450)
  }

  const tryDemoQuestion = () => {
    setQuestion(DEMO_QUESTION)
    setStatus('idle')
    demoRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  }

  return (
    <>
      <header className="site-header">
        <div className="container nav-inner">
          <a className="wordmark" href="#top">Text2Analytics</a>
          <nav aria-label="Project sections">
            <a href="#problem">Problem</a>
            <a href="#demo">Demo</a>
            <a href="#architecture">Architecture</a>
            <a href="#contributions">Contributions</a>
          </nav>
          <span className="header-meta">Research prototype / 2026</span>
        </div>
      </header>

      <main id="top">
        <section className="hero container">
          <div className="hero-main">
            <p className="eyebrow">Evidence-grounded analytics</p>
            <h1>Text2Analytics</h1>
            <h2 className="display">From business questions to inspectable evidence.</h2>
            <p className="hero-subtitle">
              An Evidence-based Analytics System for Structured Decision Support
            </p>
            <div className="technology-list" aria-label="Technology stack">
              {TECHNOLOGIES.map((technology) => (
                <span key={technology}>{technology}</span>
              ))}
            </div>
          </div>
          <aside className="hero-aside">
            <span className="aside-label">Research question</span>
            <p>
              How can analytical reasoning become visible, verifiable, and appropriately uncertain?
            </p>
            <dl>
              <div>
                <dt>Mode</dt>
                <dd>Controlled</dd>
              </div>
              <div>
                <dt>Execution</dt>
                <dd>Deterministic</dd>
              </div>
              <div>
                <dt>Focus</dt>
                <dd>Human-centered AI</dd>
              </div>
            </dl>
          </aside>
        </section>

        <section className="section problem-section container" id="problem">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Problem</p>
              <h2 className="display">Why Text2SQL is not enough</h2>
            </div>
            <p className="section-intro">
              A syntactically valid query can still sit inside an invalid analytical path.
            </p>
          </div>

          <div className="problem-grid">
            <article className="problem-card">
              <span className="problem-number">01</span>
              <h3>Text2SQL retrieves data</h3>
              <p>
                It translates a question into a query, but often hides intent assumptions, skips analysis planning, and moves directly from rows to narrative.
              </p>
              <ul>
                <li>Unstated metric and time definitions</li>
                <li>No explicit evidence-to-claim mapping</li>
                <li>Weak representation of missing variables</li>
              </ul>
            </article>

            <article className="problem-card problem-card-accent">
              <span className="problem-number">02</span>
              <h3>Structured analytics supports decisions</h3>
              <p>
                Text2Analytics exposes the intermediate reasoning states that must be inspected before an analytical answer is safe to use.
              </p>
              <ul>
                <li>Intent and plan before query generation</li>
                <li>Schema grounding and independent validation</li>
                <li>Facts, interpretations, and limitations separated</li>
              </ul>
            </article>
          </div>
        </section>

        <div className="container">
          <DemoSection
            question={question}
            setQuestion={updateQuestion}
            status={status}
            runAnalysis={runAnalysis}
            demoRef={demoRef}
          />
          <Architecture />
          <Contributions />
        </div>

        <section className="live-demo-section" aria-labelledby="live-demo-title">
          <div className="container live-demo-inner">
            <div>
              <p className="eyebrow">Controlled interaction</p>
              <h2 className="display" id="live-demo-title">Follow one question through the pipeline.</h2>
            </div>
            <button className="button button-light" type="button" onClick={tryDemoQuestion}>
              Try Demo Question
            </button>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-grid">
          <div>
            <strong>Text2Analytics</strong>
            <p>Research prototype for human-centered AI</p>
          </div>
          <div>
            <span>Controlled deterministic system</span>
            <span>Not a production system</span>
          </div>
          <p className="footer-note">
            Designed to study structured, evidence-grounded analytical reasoning under constrained conditions.
          </p>
        </div>
      </footer>
    </>
  )
}
