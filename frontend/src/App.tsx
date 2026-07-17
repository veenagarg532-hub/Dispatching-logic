import { useState, useEffect } from 'react';
import { api } from './api';
import type { SimulationRequest, SimulationResponse, ScenarioInfo } from './types';
import { InputPanel } from './components/InputPanel';
import { ResultsPanel } from './components/ResultsPanel';
import { ComparisonPanel } from './components/ComparisonPanel';
import { ConceptExplainer } from './components/ConceptExplainer';
import './App.css';

function App() {
  const [scenarioInfo, setScenarioInfo] = useState<ScenarioInfo | null>(null);
  const [config, setConfig] = useState<SimulationRequest | null>(null);
  const [results, setResults] = useState<SimulationResponse | null>(null);
  const [comparisonResults, setComparisonResults] = useState<SimulationResponse[] | null>(null);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load scenario info on mount
  useEffect(() => {
    api
      .getScenarioInfo()
      .then((info) => {
        setScenarioInfo(info);
        setConfig(info.default_config);
        // Initialize with first strategy selected
        setSelectedStrategies([info.dispatching_rules[0]]);
      })
      .catch((err) => {
        setError(`Failed to load scenario: ${err.message}`);
      });
  }, []);

  const handleRun = async () => {
    if (!config) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setComparisonResults(null);

    try {
      if (comparisonMode && selectedStrategies.length > 1) {
        // Comparison mode: run multiple strategies
        const configWithStrategies = {
          ...config,
          dispatching_rules_to_compare: selectedStrategies,
        };
        const comparisonData = await api.runComparison(configWithStrategies);
        setComparisonResults(comparisonData.results);
      } else {
        // Single mode: run one strategy
        const singleConfig = {
          ...config,
          dispatching_rule: selectedStrategies[0] || config.dispatching_rule,
        };
        const result = await api.runSimulation(singleConfig);
        setResults(result);
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(error.response?.data?.detail || error.message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (scenarioInfo) {
      setConfig(scenarioInfo.default_config);
      setSelectedStrategies([scenarioInfo.dispatching_rules[0]]);
      setResults(null);
      setComparisonResults(null);
      setError(null);
      setComparisonMode(false);
    }
  };

  if (!scenarioInfo || !config) {
    return (
      <div className="app">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading scenario...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>{scenarioInfo.concept_title}</h1>
        <p className="subtitle">
          Interactive Discrete-Event Simulation — Factory Dynamics MVP
        </p>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="main-content">
        <InputPanel
          config={config}
          onChange={setConfig}
          onRun={handleRun}
          onReset={handleReset}
          loading={loading}
          dispatchingRules={scenarioInfo.dispatching_rules}
          arrivalDistributions={scenarioInfo.arrival_distributions}
          comparisonMode={comparisonMode}
          onComparisonModeChange={setComparisonMode}
          selectedStrategies={selectedStrategies}
          onSelectedStrategiesChange={setSelectedStrategies}
        />

        <div>
          <ConceptExplainer text={scenarioInfo.concept_explainer} />
          {loading && (
            <div className="panel loading">
              <div className="spinner"></div>
              <p>Running simulation{comparisonMode && selectedStrategies.length > 1 ? 's' : ''}...</p>
            </div>
          )}
          {comparisonResults && !loading && (
            <ComparisonPanel results={comparisonResults} config={config} />
          )}
          {results && !loading && !comparisonResults && (
            <ResultsPanel results={results} config={config} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
