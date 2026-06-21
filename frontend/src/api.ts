/**
 * API client for communicating with the FastAPI backend.
 */
import axios from 'axios';
import type { SimulationRequest, SimulationResponse, ComparisonResponse, ScenarioInfo } from './types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const api = {
  async getScenarioInfo(): Promise<ScenarioInfo> {
    const response = await axios.get<ScenarioInfo>(`${API_BASE}/api/scenario`);
    return response.data;
  },

  async runSimulation(config: SimulationRequest): Promise<SimulationResponse> {
    const response = await axios.post<SimulationResponse>(
      `${API_BASE}/api/simulate`,
      config
    );
    return response.data;
  },

  async runComparison(config: SimulationRequest): Promise<ComparisonResponse> {
    const response = await axios.post<ComparisonResponse>(
      `${API_BASE}/api/simulate/compare`,
      config
    );
    return response.data;
  },
};
