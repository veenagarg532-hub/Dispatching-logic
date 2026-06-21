/**
 * TypeScript type definitions matching the backend API schemas.
 */

export interface SimulationRequest {
  num_tools: number;
  num_products: number;
  arrival_rate: number;
  arrival_distribution: 'exponential' | 'fixed';
  processing_times: number[];
  qualification_matrix: boolean[][];
  dispatching_rule: string;
  dispatching_rules_to_compare?: string[];  // NEW: for comparison mode
  sim_duration: number;
  snapshot_interval: number;
  random_seed: number | null;
}

export interface MetricSnapshot {
  time: number;
  wip: number;
  cumulative_moves: number;
  cumulative_queue_time: number;
  tool_utilisation: number[];
}

export interface SimulationResponse {
  dispatching_rule: string;  // NEW: which rule was used
  snapshots: MetricSnapshot[];
  total_lots_arrived: number;
  total_lots_completed: number;
  mean_queue_time: number;
  mean_cycle_time: number;
  tool_utilisation: number[];
}

export interface ComparisonResponse {
  results: SimulationResponse[];  // NEW: array of results
}

export interface ScenarioInfo {
  concept_title: string;
  concept_explainer: string;
  default_config: SimulationRequest;
  dispatching_rules: string[];
  arrival_distributions: string[];
}
