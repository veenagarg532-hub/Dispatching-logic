import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { SimulationResponse, SimulationRequest } from '../types';

interface ResultsPanelProps {
  results: SimulationResponse;
  config: SimulationRequest;
}

export function ResultsPanel({ results, config }: ResultsPanelProps) {
  const wipData = results.snapshots.map((s) => ({
    time: s.time,
    WIP: s.wip,
  }));

  const movesData = results.snapshots.map((s) => ({
    time: s.time,
    'Cumulative Moves': s.cumulative_moves,
  }));

  const queueTimeData = results.snapshots.map((s) => ({
    time: s.time,
    'Total Queue Time': s.cumulative_queue_time,
  }));

  // Tool utilisation over time (average across all tools)
  const utilisationData = results.snapshots.map((s) => ({
    time: s.time,
    'Avg Utilisation': (
      s.tool_utilisation.reduce((a, b) => a + b, 0) / s.tool_utilisation.length
    ).toFixed(3),
  }));

  return (
    <div className="panel results-panel">
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Simulation Results</h2>

      <div className="chart-container">
        <h3>Toolset WIP Over Time</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={wipData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'WIP (lots)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="WIP" stroke="#4299e1" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>Cumulative Total Moves</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={movesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Moves', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Cumulative Moves"
              stroke="#48bb78"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>Total Accumulated Queue Time</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={queueTimeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Queue Time', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Total Queue Time"
              stroke="#ed8936"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>Average Tool Utilisation Over Time</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={utilisationData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis
              label={{ value: 'Utilisation', angle: -90, position: 'insideLeft' }}
              domain={[0, 1]}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Avg Utilisation"
              stroke="#9f7aea"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="summary-stats">
        <div className="stat-card">
          <div className="stat-label">Total Lots Arrived</div>
          <div className="stat-value">{results.total_lots_arrived}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Lots Completed</div>
          <div className="stat-value">{results.total_lots_completed}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Mean Queue Time</div>
          <div className="stat-value">{results.mean_queue_time.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Mean Cycle Time</div>
          <div className="stat-value">{results.mean_cycle_time.toFixed(2)}</div>
        </div>
      </div>

      <div className="stat-card" style={{ marginTop: '1rem' }}>
        <div className="stat-label">Final Tool Utilisation</div>
        <div className="tool-utilisation">
          {results.tool_utilisation.map((util, i) => (
            <div key={i} className="tool-util-badge">
              Tool {i}: {(util * 100).toFixed(1)}%
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
