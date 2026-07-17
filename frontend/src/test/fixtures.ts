/**
 * Shared test fixtures for frontend component tests.
 * Import these instead of duplicating mock data across test files.
 */
import type { SimulationResponse, SimulationRequest } from '../types';

/** A minimal valid SimulationRequest (mirrors conftest.py base_config). */
export const mockConfig: SimulationRequest = {
  num_tools: 4,
  num_products: 3,
  arrival_rate: 0.5,
  arrival_distribution: 'exponential',
  processing_times: [2.0, 8.0, 5.0],
  qualification_matrix: [
    [true,  true,  false],
    [true,  false, true],
    [false, true,  true],
    [true,  true,  true],
  ],
  dispatching_rule: 'fifo',
  sim_duration: 100.0,
  snapshot_interval: 1.0,
  random_seed: 42,
};

/**
 * A mock SimulationResponse for rendering tests.
 * Contains 5 snapshots so chart rendering logic can be tested without a
 * live backend.
 */
export const mockResults: SimulationResponse = {
  dispatching_rule: 'fifo',
  total_lots_arrived: 50,
  total_lots_completed: 47,
  mean_queue_time: 1.2345,
  mean_cycle_time: 5.6789,
  tool_utilisation: [0.72, 0.68, 0.75, 0.80],
  snapshots: [
    { time: 0,   wip: 0, cumulative_moves: 0,  cumulative_queue_time: 0.0,  tool_utilisation: [0.0,  0.0,  0.0,  0.0]  },
    { time: 25,  wip: 2, cumulative_moves: 10, cumulative_queue_time: 5.0,  tool_utilisation: [0.60, 0.55, 0.65, 0.70] },
    { time: 50,  wip: 3, cumulative_moves: 22, cumulative_queue_time: 12.0, tool_utilisation: [0.65, 0.60, 0.70, 0.72] },
    { time: 75,  wip: 2, cumulative_moves: 35, cumulative_queue_time: 18.5, tool_utilisation: [0.68, 0.64, 0.72, 0.76] },
    { time: 100, wip: 1, cumulative_moves: 47, cumulative_queue_time: 24.3, tool_utilisation: [0.72, 0.68, 0.75, 0.80] },
  ],
};

/** A result where nothing completed — tests divide-by-zero guards. */
export const mockEmptyResults: SimulationResponse = {
  dispatching_rule: 'fifo',
  total_lots_arrived: 0,
  total_lots_completed: 0,
  mean_queue_time: 0.0,
  mean_cycle_time: 0.0,
  tool_utilisation: [0.0, 0.0, 0.0, 0.0],
  snapshots: [
    { time: 0, wip: 0, cumulative_moves: 0, cumulative_queue_time: 0.0, tool_utilisation: [0.0, 0.0, 0.0, 0.0] },
  ],
};
