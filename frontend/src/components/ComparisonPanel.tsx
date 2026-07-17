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

interface ComparisonPanelProps {
  results: SimulationResponse[];
  config: SimulationRequest;
}

const COLORS = ['#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#f56565', '#38b2ac'];

export function ComparisonPanel({ results }: ComparisonPanelProps) {
  // Merge all snapshots by time for overlay charts
  const mergeSnapshotsByMetric = (metric: 'wip' | 'cumulative_moves' | 'cumulative_queue_time') => {
    const timeMap = new Map<number, Record<string, number>>();
    
    results.forEach((result) => {
      result.snapshots.forEach((snapshot) => {
        if (!timeMap.has(snapshot.time)) {
          timeMap.set(snapshot.time, { time: snapshot.time });
        }
        const dataPoint = timeMap.get(snapshot.time);
        if (dataPoint) {
          dataPoint[`${result.dispatching_rule}`] = snapshot[metric];
        }
      });
    });
    
    return Array.from(timeMap.values()).sort((a, b) => a.time - b.time);
  };

  const wipComparisonData = mergeSnapshotsByMetric('wip');
  const movesComparisonData = mergeSnapshotsByMetric('cumulative_moves');
  const queueTimeComparisonData = mergeSnapshotsByMetric('cumulative_queue_time');

  return (
    <div className="panel results-panel">
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>
        Strategy Comparison Results
      </h2>

      {/* Comparison Summary Table */}
      <div style={{ marginBottom: '2rem', overflowX: 'auto' }}>
        <h3>Performance Summary</h3>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          marginTop: '1rem',
          fontSize: '0.9rem',
        }}>
          <thead>
            <tr style={{ background: '#f7fafc' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>
                Strategy
              </th>
              <th style={{ padding: '0.75rem', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>
                Completed Lots
              </th>
              <th style={{ padding: '0.75rem', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>
                Mean Queue Time
              </th>
              <th style={{ padding: '0.75rem', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>
                Mean Cycle Time
              </th>
              <th style={{ padding: '0.75rem', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>
                Avg Utilisation
              </th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => {
              const avgUtil = result.tool_utilisation.reduce((a, b) => a + b, 0) / result.tool_utilisation.length;
              // Find best values for highlighting
              const bestQueueTime = Math.min(...results.map(r => r.mean_queue_time));
              const bestCycleTime = Math.min(...results.map(r => r.mean_cycle_time));
              const mostCompleted = Math.max(...results.map(r => r.total_lots_completed));
              
              return (
                <tr key={result.dispatching_rule} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ 
                    padding: '0.75rem',
                    fontWeight: 500,
                    color: COLORS[index % COLORS.length],
                  }}>
                    {result.dispatching_rule.replace(/_/g, ' ').toUpperCase()}
                  </td>
                  <td style={{ 
                    padding: '0.75rem', 
                    textAlign: 'right',
                    fontWeight: result.total_lots_completed === mostCompleted ? 'bold' : 'normal',
                    background: result.total_lots_completed === mostCompleted ? '#e6fffa' : 'transparent',
                  }}>
                    {result.total_lots_completed}
                  </td>
                  <td style={{ 
                    padding: '0.75rem', 
                    textAlign: 'right',
                    fontWeight: result.mean_queue_time === bestQueueTime ? 'bold' : 'normal',
                    background: result.mean_queue_time === bestQueueTime ? '#e6fffa' : 'transparent',
                  }}>
                    {result.mean_queue_time.toFixed(2)}
                  </td>
                  <td style={{ 
                    padding: '0.75rem', 
                    textAlign: 'right',
                    fontWeight: result.mean_cycle_time === bestCycleTime ? 'bold' : 'normal',
                    background: result.mean_cycle_time === bestCycleTime ? '#e6fffa' : 'transparent',
                  }}>
                    {result.mean_cycle_time.toFixed(2)}
                  </td>
                  <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                    {(avgUtil * 100).toFixed(1)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <p style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.5rem', fontStyle: 'italic' }}>
          * Highlighted cells show the best performance for each metric
        </p>
      </div>

      {/* Comparison Charts */}
      <div className="chart-container">
        <h3>WIP Comparison Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={wipComparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'WIP (lots)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            {results.map((result, index) => (
              <Line
                key={result.dispatching_rule}
                type="monotone"
                dataKey={result.dispatching_rule}
                name={result.dispatching_rule.replace(/_/g, ' ').toUpperCase()}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>Cumulative Moves Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={movesComparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Moves', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            {results.map((result, index) => (
              <Line
                key={result.dispatching_rule}
                type="monotone"
                dataKey={result.dispatching_rule}
                name={result.dispatching_rule.replace(/_/g, ' ').toUpperCase()}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>Queue Time Accumulation Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={queueTimeComparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Queue Time', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            {results.map((result, index) => (
              <Line
                key={result.dispatching_rule}
                type="monotone"
                dataKey={result.dispatching_rule}
                name={result.dispatching_rule.replace(/_/g, ' ').toUpperCase()}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Key Insights */}
      <div style={{ 
        background: '#edf2f7', 
        padding: '1.5rem', 
        borderRadius: '4px', 
        marginTop: '2rem' 
      }}>
        <h3 style={{ marginBottom: '1rem' }}>Key Insights</h3>
        <ul style={{ listStyle: 'disc', marginLeft: '1.5rem', lineHeight: '1.8' }}>
          <li>
            <strong>Best Queue Time:</strong> {
              results.reduce((best, r) => 
                r.mean_queue_time < best.mean_queue_time ? r : best
              ).dispatching_rule.replace(/_/g, ' ').toUpperCase()
            } with {
              Math.min(...results.map(r => r.mean_queue_time)).toFixed(2)
            } time units
          </li>
          <li>
            <strong>Highest Throughput:</strong> {
              results.reduce((best, r) => 
                r.total_lots_completed > best.total_lots_completed ? r : best
              ).dispatching_rule.replace(/_/g, ' ').toUpperCase()
            } with {
              Math.max(...results.map(r => r.total_lots_completed))
            } lots completed
          </li>
          <li>
            <strong>Most Efficient:</strong> {
              results.reduce((best, r) => {
                const avgUtil = r.tool_utilisation.reduce((a, b) => a + b, 0) / r.tool_utilisation.length;
                const bestAvgUtil = best.tool_utilisation.reduce((a, b) => a + b, 0) / best.tool_utilisation.length;
                return avgUtil > bestAvgUtil ? r : best;
              }).dispatching_rule.replace(/_/g, ' ').toUpperCase()
            } with highest average utilisation
          </li>
        </ul>
      </div>
    </div>
  );
}
