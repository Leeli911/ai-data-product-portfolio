import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('Text2Analytics portfolio page', () => {
  it('presents the project framing and required sections', () => {
    render(<App />)

    expect(
      screen.getByRole('heading', { name: 'Text2Analytics', level: 1 }),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'An Evidence-based Analytics System for Structured Decision Support',
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Why Text2SQL is not enough' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'System architecture' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Key contributions' }),
    ).toBeInTheDocument()

    for (const technology of [
      'Python',
      'DuckDB',
      'Pydantic',
      'Streamlit',
      'SQL Guardrails',
    ]) {
      expect(screen.getByText(technology)).toBeInTheDocument()
    }
  })

  it('fills the controlled demo question', () => {
    render(<App />)

    fireEvent.click(screen.getByRole('button', { name: 'Try Demo Question' }))

    expect(screen.getByLabelText('Business Question')).toHaveValue(
      'Why did GMV drop in Chaoyang this week?',
    )
  })

  it('requires a non-empty business question', () => {
    render(<App />)

    fireEvent.click(screen.getByRole('button', { name: 'Run Analysis' }))

    expect(
      screen.getByText(
        'Enter a business question to run the controlled demonstration.',
      ),
    ).toBeInTheDocument()
  })

  it('reveals every required deterministic output', async () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Try Demo Question' }))
    fireEvent.click(screen.getByRole('button', { name: 'Run Analysis' }))

    await waitFor(() =>
      expect(
        screen.getByText('Structural Completeness Score'),
      ).toBeInTheDocument(),
    )
    expect(screen.queryByText('Confidence Score')).not.toBeInTheDocument()

    for (const label of [
      'Intent',
      'Analysis Plan',
      'SQL Query',
      'Query Result',
      'Validation Gates',
      'Facts',
      'Interpretations',
      'Limitations',
    ]) {
      expect(
        screen.getByRole('heading', { name: label }),
      ).toBeInTheDocument()
    }
    expect(screen.getByText('0.90')).toBeInTheDocument()
    expect(screen.getByText('schema validation passed')).toBeInTheDocument()
    expect(screen.getByText('SQL execution validated')).toBeInTheDocument()
    expect(screen.getByText('comparison window verified')).toBeInTheDocument()
    expect(screen.getByText('bounded inference space')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Interpretations are bounded by observed metrics available in the controlled schema.',
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Measures verified schema coverage, execution validity, comparison-window integrity, and evidence linkage. It is not a probability of correctness.',
      ),
    ).toBeInTheDocument()
  })

  it('presents enforceable research claims and stage constraints', () => {
    render(<App />)

    for (const claim of [
      'The system enforces evidence decomposition.',
      'The system represents uncertainty explicitly.',
      'The pipeline requires stage-level verification.',
      'The execution layer permits only schema-grounded SQL.',
    ]) {
      expect(screen.getByRole('heading', { name: claim })).toBeInTheDocument()
    }

    expect(screen.getAllByText('validated').length).toBeGreaterThan(0)
    expect(screen.getAllByText('constrained').length).toBeGreaterThan(0)
    expect(screen.getAllByText('inspectable').length).toBeGreaterThan(0)
  })
})
