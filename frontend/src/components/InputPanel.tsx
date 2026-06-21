import type { SimulationRequest } from '../types';

interface InputPanelProps {
  config: SimulationRequest;
  onChange: (config: SimulationRequest) => void;
  onRun: () => void;
  onReset: () => void;
  loading: boolean;
  dispatchingRules: string[];
  arrivalDistributions: string[];
  comparisonMode: boolean;
  onComparisonModeChange: (mode: boolean) => void;
  selectedStrategies: string[];
  onSelectedStrategiesChange: (strategies: string[]) => void;
}

export function InputPanel({
  config,
  onChange,
  onRun,
  onReset,
  loading,
  dispatchingRules,
  arrivalDistributions,
  comparisonMode,
  onComparisonModeChange,
  selectedStrategies,
  onSelectedStrategiesChange,
}: InputPanelProps) {
  const updateConfig = (updates: Partial<SimulationRequest>) => {
    onChange({ ...config, ...updates });
  };

  const updateProcessingTime = (index: number, value: number) => {
    const newTimes = [...config.processing_times];
    newTimes[index] = value;
    updateConfig({ processing_times: newTimes });
  };

  const updateQualification = (tool: number, product: number, value: boolean) => {
    const newMatrix = config.qualification_matrix.map((row) => [...row]);
    newMatrix[tool][product] = value;
    updateConfig({ qualification_matrix: newMatrix });
  };

  const handleNumToolsChange = (n: number) => {
    const current = config.qualification_matrix.length;
    let newMatrix = [...config.qualification_matrix];
    if (n > current) {
      // Add rows (all qualified by default)
      for (let i = current; i < n; i++) {
        newMatrix.push(Array(config.num_products).fill(true));
      }
    } else if (n < current) {
      // Remove rows
      newMatrix = newMatrix.slice(0, n);
    }
    updateConfig({ num_tools: n, qualification_matrix: newMatrix });
  };

  const handleNumProductsChange = (n: number) => {
    const current = config.num_products;
    let newMatrix = config.qualification_matrix.map((row) => [...row]);
    let newTimes = [...config.processing_times];

    if (n > current) {
      // Add columns and processing times
      newMatrix = newMatrix.map((row) => [...row, ...Array(n - current).fill(true)]);
      newTimes = [...newTimes, ...Array(n - current).fill(3.0)];
    } else if (n < current) {
      // Remove columns and processing times
      newMatrix = newMatrix.map((row) => row.slice(0, n));
      newTimes = newTimes.slice(0, n);
    }

    updateConfig({
      num_products: n,
      qualification_matrix: newMatrix,
      processing_times: newTimes,
    });
  };

  return (
    <div className="panel input-panel">
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Configuration</h2>

      <div className="form-group">
        <label>Number of Tools</label>
        <input
          type="number"
          min={1}
          max={10}
          value={config.num_tools}
          onChange={(e) => handleNumToolsChange(Number(e.target.value))}
        />
      </div>

      <div className="form-group">
        <label>Number of Products</label>
        <input
          type="number"
          min={1}
          max={8}
          value={config.num_products}
          onChange={(e) => handleNumProductsChange(Number(e.target.value))}
        />
      </div>

      <div className="form-group">
        <label>Arrival Rate (lots/time unit)</label>
        <input
          type="number"
          min={0.01}
          max={10}
          step={0.1}
          value={config.arrival_rate}
          onChange={(e) => updateConfig({ arrival_rate: Number(e.target.value) })}
        />
      </div>

      <div className="form-group">
        <label>Arrival Distribution</label>
        <select
          value={config.arrival_distribution}
          onChange={(e) =>
            updateConfig({
              arrival_distribution: e.target.value as 'exponential' | 'fixed',
            })
          }
        >
          {arrivalDistributions.map((dist) => (
            <option key={dist} value={dist}>
              {dist}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Processing Times (time units)</label>
        <div className="processing-times">
          {config.processing_times.map((time, i) => (
            <div key={i} className="processing-time-row">
              <label>Product {i}:</label>
              <input
                type="number"
                min={0.1}
                max={100}
                step={0.5}
                value={time}
                onChange={(e) => updateProcessingTime(i, Number(e.target.value))}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Cross-Qualification Matrix</label>
        <div className="matrix-editor">
          {config.qualification_matrix.map((row, toolIdx) => (
            <div key={toolIdx} className="matrix-row">
              <label>Tool {toolIdx}:</label>
              <div className="checkbox-group">
                {row.map((qualified, prodIdx) => (
                  <label key={prodIdx}>
                    <input
                      type="checkbox"
                      checked={qualified}
                      onChange={(e) =>
                        updateQualification(toolIdx, prodIdx, e.target.checked)
                      }
                    />
                    P{prodIdx}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={comparisonMode}
            onChange={(e) => onComparisonModeChange(e.target.checked)}
            style={{ marginRight: '0.5rem' }}
          />
          <strong>Comparison Mode</strong> (Select multiple strategies)
        </label>
      </div>

      {comparisonMode ? (
        <div className="form-group">
          <label>Select Dispatching Rules to Compare</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {dispatchingRules.map((rule) => (
              <label key={rule} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={selectedStrategies.includes(rule)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onSelectedStrategiesChange([...selectedStrategies, rule]);
                    } else {
                      onSelectedStrategiesChange(selectedStrategies.filter((s) => s !== rule));
                    }
                  }}
                />
                {rule.replace(/_/g, ' ').toUpperCase()}
              </label>
            ))}
          </div>
          {selectedStrategies.length === 0 && (
            <p style={{ color: '#e53e3e', fontSize: '0.85rem', marginTop: '0.5rem' }}>
              Please select at least one strategy
            </p>
          )}
        </div>
      ) : (
        <div className="form-group">
          <label>Dispatching Rule</label>
          <select
            value={selectedStrategies[0] || config.dispatching_rule}
            onChange={(e) => {
              onSelectedStrategiesChange([e.target.value]);
              updateConfig({ dispatching_rule: e.target.value });
            }}
          >
            {dispatchingRules.map((rule) => (
              <option key={rule} value={rule}>
                {rule.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="form-group">
        <label>Simulation Duration (time units)</label>
        <input
          type="number"
          min={10}
          max={2000}
          step={10}
          value={config.sim_duration}
          onChange={(e) => updateConfig({ sim_duration: Number(e.target.value) })}
        />
      </div>

      <div className="form-group">
        <label>Snapshot Interval (time units)</label>
        <input
          type="number"
          min={0.5}
          max={10}
          step={0.5}
          value={config.snapshot_interval}
          onChange={(e) => updateConfig({ snapshot_interval: Number(e.target.value) })}
        />
      </div>

      <div className="form-group">
        <label>Random Seed (null for random)</label>
        <input
          type="number"
          value={config.random_seed ?? ''}
          onChange={(e) =>
            updateConfig({
              random_seed: e.target.value === '' ? null : Number(e.target.value),
            })
          }
          placeholder="null"
        />
      </div>

      <div className="button-group">
        <button 
          className="btn-primary" 
          onClick={onRun} 
          disabled={loading || (comparisonMode && selectedStrategies.length === 0)}
        >
          {loading ? 'Running...' : comparisonMode && selectedStrategies.length > 1 ? 'Run Comparison' : 'Run Simulation'}
        </button>
        <button className="btn-secondary" onClick={onReset} disabled={loading}>
          Reset
        </button>
      </div>
    </div>
  );
}
