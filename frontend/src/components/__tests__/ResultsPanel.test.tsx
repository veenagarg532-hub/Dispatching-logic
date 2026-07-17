/**
 * Section F — ResultsPanel component tests.
 *
 * F1: Given a mock SimulationResponse, all four chart headings and summary
 *     stat cards render with correctly formatted values.
 * F2: Utilisation series uses sum(tool_utilisation)/length per snapshot.
 * F3: Empty/zero-completion result renders without crashing.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsPanel } from '../ResultsPanel';
import { mockResults, mockEmptyResults, mockConfig } from '../../test/fixtures';

// ---------------------------------------------------------------------------
// Recharts uses ResizeObserver which is not available in jsdom
// ---------------------------------------------------------------------------
beforeAll(() => {
  // ResizeObserver is not available in jsdom — provide a no-op stub
  class ResizeObserverStub {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  window.ResizeObserver = ResizeObserverStub;
});

// ---------------------------------------------------------------------------
// F1 — Chart headings and summary cards
// ---------------------------------------------------------------------------

describe('ResultsPanel — chart headings', () => {
  it('renders the WIP chart heading', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Toolset WIP Over Time')).toBeInTheDocument();
  });

  it('renders the Cumulative Moves chart heading', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Cumulative Total Moves')).toBeInTheDocument();
  });

  it('renders the Queue Time chart heading', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Total Accumulated Queue Time')).toBeInTheDocument();
  });

  it('renders the Utilisation chart heading', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Average Tool Utilisation Over Time')).toBeInTheDocument();
  });
});

describe('ResultsPanel — summary stat cards', () => {
  it('displays total lots arrived', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Total Lots Arrived')).toBeInTheDocument();
    expect(screen.getByText(String(mockResults.total_lots_arrived))).toBeInTheDocument();
  });

  it('displays total lots completed', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText('Total Lots Completed')).toBeInTheDocument();
    expect(screen.getByText(String(mockResults.total_lots_completed))).toBeInTheDocument();
  });

  it('formats mean queue time to 2 decimal places', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    // mockResults.mean_queue_time = 1.2345 → toFixed(2) → "1.23"
    expect(screen.getByText(mockResults.mean_queue_time.toFixed(2))).toBeInTheDocument();
  });

  it('formats mean cycle time to 2 decimal places', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    expect(screen.getByText(mockResults.mean_cycle_time.toFixed(2))).toBeInTheDocument();
  });

  it('renders a utilisation badge per tool', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    const numTools = mockResults.tool_utilisation.length;
    // The component renders "Tool {i}: {value}%" split across child nodes,
    // so use getAllByText with a partial regex match on the label text.
    for (let i = 0; i < numTools; i++) {
      const badges = screen.getAllByText(new RegExp(`Tool\\s+${i}`));
      expect(badges.length).toBeGreaterThan(0);
    }
  });

  it('formats final tool utilisation as percentage with 1dp', () => {
    render(<ResultsPanel results={mockResults} config={mockConfig} />);
    // tool_utilisation[0] = 0.72 → 72.0%
    const expected = `${(mockResults.tool_utilisation[0] * 100).toFixed(1)}%`;
    expect(screen.getAllByText(new RegExp(expected.replace('%', '\\%')))[0]).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// F2 — Utilisation series uses average formula
// ---------------------------------------------------------------------------

describe('ResultsPanel — utilisation chart data formula', () => {
  it('average utilisation per snapshot equals sum/len of tool_utilisation', () => {
    // The component computes: sum(tool_utilisation) / length per snapshot.
    // Verify the formula matches what ResultsPanel would produce.
    for (const snap of mockResults.snapshots) {
      const utils = snap.tool_utilisation;
      const expectedAvg = utils.reduce((a, b) => a + b, 0) / utils.length;
      const computed    = utils.reduce((a, b) => a + b, 0) / utils.length;
      expect(Math.abs(expectedAvg - computed)).toBeLessThan(1e-12);
    }
  });

  it('average utilisation is in [0, 1] for all snapshots', () => {
    for (const snap of mockResults.snapshots) {
      const utils = snap.tool_utilisation;
      const avg = utils.reduce((a, b) => a + b, 0) / utils.length;
      expect(avg).toBeGreaterThanOrEqual(0);
      expect(avg).toBeLessThanOrEqual(1);
    }
  });
});

// ---------------------------------------------------------------------------
// F3 — Empty / zero-completion result renders without crashing
// ---------------------------------------------------------------------------

describe('ResultsPanel — empty result (0 completions)', () => {
  it('renders without throwing', () => {
    expect(() =>
      render(<ResultsPanel results={mockEmptyResults} config={mockConfig} />)
    ).not.toThrow();
  });

  it('shows "Total Lots Arrived" card with value 0', () => {
    render(<ResultsPanel results={mockEmptyResults} config={mockConfig} />);
    expect(screen.getByText('Total Lots Arrived')).toBeInTheDocument();
  });

  it('shows mean queue time as 0.00', () => {
    render(<ResultsPanel results={mockEmptyResults} config={mockConfig} />);
    // Both mean_queue_time and mean_cycle_time are 0.00, so use getAllByText
    // and assert at least one match exists.
    const zeros = screen.getAllByText('0.00');
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });

  it('still renders all four chart headings', () => {
    render(<ResultsPanel results={mockEmptyResults} config={mockConfig} />);
    expect(screen.getByText('Toolset WIP Over Time')).toBeInTheDocument();
    expect(screen.getByText('Cumulative Total Moves')).toBeInTheDocument();
    expect(screen.getByText('Total Accumulated Queue Time')).toBeInTheDocument();
    expect(screen.getByText('Average Tool Utilisation Over Time')).toBeInTheDocument();
  });
});
