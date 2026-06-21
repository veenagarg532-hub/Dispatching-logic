# Multi-Strategy Comparison Feature

## Overview

The **Multi-Strategy Comparison** feature allows users to run multiple dispatching strategies simultaneously and compare their performance side-by-side. This is invaluable for understanding the relative strengths and weaknesses of different dispatching approaches.

---

## Feature Highlights

✅ **Select Multiple Strategies**: Choose 2 or more dispatching rules to compare  
✅ **Side-by-Side Charts**: Overlay multiple strategies on the same charts  
✅ **Performance Summary Table**: Compare key metrics at a glance  
✅ **Automatic Best Highlighting**: Best performers highlighted in green  
✅ **Key Insights**: Automated analysis of results  

---

## How to Use

### Step 1: Enable Comparison Mode

1. In the **Input Panel** (left side), find the **"Comparison Mode"** checkbox
2. Check the box to enable comparison mode
3. The dispatching rule selector will change to show checkboxes

### Step 2: Select Strategies

1. Select **2 or more** dispatching strategies you want to compare:
   - ☑️ FIFO
   - ☑️ LEAST LOADED TOOL
   - ☑️ RANDOM QUALIFIED TOOL
   - ☑️ OPTIMISED SPT

2. You can select all 4 strategies to see a complete comparison

### Step 3: Configure Other Parameters

Configure your simulation parameters as usual:
- Number of tools
- Number of products
- Arrival rate
- Processing times
- Cross-qualification matrix
- Simulation duration

**Note**: All strategies will use the same configuration parameters

### Step 4: Run Comparison

1. Click **"Run Comparison"** button
2. The system will run all selected strategies sequentially
3. Wait a few seconds (time depends on number of strategies and simulation duration)

### Step 5: Analyze Results

The **Comparison Panel** shows:

#### 1. Performance Summary Table
- Side-by-side metrics for all strategies
- **Highlighted cells** show the best performer for each metric
- Metrics shown:
  - Completed Lots
  - Mean Queue Time ⭐
  - Mean Cycle Time ⭐
  - Average Utilisation

#### 2. Overlay Charts
- **WIP Comparison**: See how queue lengths differ
- **Cumulative Moves**: Compare throughput over time
- **Queue Time Accumulation**: Identify which strategy minimizes waiting

All strategies are shown on the same chart with different colors

#### 3. Key Insights
- Automatic summary of best performers
- Quick takeaways for decision-making

---

## Example Use Cases

### Use Case 1: Find the Best Strategy
**Goal**: Identify which dispatching rule minimizes queue time

**Steps**:
1. Enable comparison mode
2. Select all 4 strategies
3. Run comparison
4. Check the **Performance Summary Table**
5. Look for the highlighted **Mean Queue Time** — that's your winner!

**Typical Result**: OPTIMISED (SPT) usually wins for queue time

---

### Use Case 2: FIFO vs. Optimised
**Goal**: Show the impact of moving from FIFO to an optimised strategy

**Steps**:
1. Enable comparison mode
2. Select only **FIFO** and **OPTIMISED SPT**
3. Run comparison
4. Compare the charts side-by-side

**Typical Result**: SPT reduces queue time by 20-40% compared to FIFO

---

### Use Case 3: Impact of Load Balancing
**Goal**: Understand how load balancing affects utilisation

**Steps**:
1. Enable comparison mode
2. Select **FIFO** and **LEAST LOADED TOOL**
3. Configure with uneven processing times (e.g., Product 0: 2.0, Product 1: 8.0, Product 2: 5.0)
4. Run comparison
5. Check **Average Utilisation** in the summary table

**Typical Result**: Least-Loaded-Tool achieves higher overall utilisation

---

### Use Case 4: Restricted Qualification Impact
**Goal**: See how cross-qualification restrictions affect different strategies

**Steps**:
1. Restrict the qualification matrix (uncheck some tool-product pairs)
2. Enable comparison mode
3. Select all strategies
4. Run comparison
5. Observe WIP differences

**Typical Result**: Some strategies handle restrictions better than others

---

## Technical Details

### Backend Implementation

#### New Endpoint: `/api/simulate/compare`

**Request**:
```json
{
  "num_tools": 4,
  "num_products": 3,
  "dispatching_rules_to_compare": ["fifo", "optimised_spt"],
  "arrival_rate": 0.8,
  ...other parameters...
}
```

**Response**:
```json
{
  "results": [
    {
      "dispatching_rule": "fifo",
      "snapshots": [...],
      "mean_queue_time": 12.45,
      ...
    },
    {
      "dispatching_rule": "optimised_spt",
      "snapshots": [...],
      "mean_queue_time": 7.23,
      ...
    }
  ]
}
```

#### How It Works
1. Backend receives list of strategies to compare
2. For each strategy:
   - Run simulation with same parameters
   - Collect results independently
3. Return array of results
4. Frontend overlays results on same charts

---

### Frontend Implementation

#### New Components

**ComparisonPanel** (`components/ComparisonPanel.tsx`):
- Displays comparison results
- Merges snapshots from multiple simulations by time
- Renders overlay charts with different colors per strategy
- Shows performance summary table with highlighting

**InputPanel Updates**:
- Comparison mode checkbox
- Multi-select for strategies (checkboxes instead of dropdown)
- Dynamic button text ("Run Comparison" vs "Run Simulation")

**App Updates**:
- State management for comparison mode
- Selected strategies tracking
- Conditional rendering (ComparisonPanel vs ResultsPanel)

---

## Performance Considerations

### Simulation Time
- **Single strategy**: 2-5 seconds (1,000 lots)
- **2 strategies**: 4-10 seconds
- **4 strategies**: 8-20 seconds

Each strategy runs sequentially, so time scales linearly.

### Future Optimization (Phase 2)
- Run simulations in parallel (backend threading)
- Cache common simulation setup
- Progressive results streaming

---

## Benefits

### For Educators
- **Visual learning**: Students see differences immediately
- **What-if analysis**: Change one parameter, compare strategies
- **Hypothesis testing**: Predict winner, then verify

### For Engineers
- **Data-driven decisions**: Choose strategy based on metrics
- **Trade-off analysis**: See queue time vs. utilisation trade-offs
- **Sensitivity analysis**: How does performance change with load?

### For Researchers
- **Benchmarking**: Compare custom strategies to baselines
- **Publication-ready**: Export comparison charts and tables
- **Reproducible**: Same seed ensures identical comparisons

---

## Limitations (Phase 1)

- ❌ **No parallel execution**: Strategies run sequentially
- ❌ **No result export**: Cannot download comparison data (yet)
- ❌ **No custom strategies**: Limited to 4 built-in strategies
- ❌ **No statistical analysis**: No confidence intervals or significance testing

---

## Future Enhancements (Phase 2+)

### Planned Features
- ✅ Parallel execution (run strategies simultaneously)
- ✅ Export to CSV/Excel (download comparison data)
- ✅ Custom strategy upload (Python code or rules)
- ✅ Statistical comparison (t-tests, confidence intervals)
- ✅ Multi-scenario comparison (compare across different configs)
- ✅ Historical comparison (save and reload comparisons)

### Advanced Features
- ✅ Real-time comparison (update charts as simulations run)
- ✅ Sensitivity analysis (vary one parameter across strategies)
- ✅ Pareto frontier (optimal trade-off curve)
- ✅ Machine learning (recommend best strategy for given config)

---

## Troubleshooting

### Problem: Comparison button is disabled
**Solution**: Make sure you've selected at least one strategy

### Problem: Charts look cluttered with 4 strategies
**Solution**: Use fewer strategies (2-3) for clearer visualization

### Problem: Comparison takes too long
**Solution**: Reduce simulation duration or use fewer strategies

### Problem: Can't see difference between strategies
**Solution**: Increase load (higher arrival rate) to stress the system

---

## API Reference

### POST `/api/simulate/compare`

**Request Body**:
```typescript
{
  num_tools: number;
  num_products: number;
  arrival_rate: number;
  arrival_distribution: 'exponential' | 'fixed';
  processing_times: number[];
  qualification_matrix: boolean[][];
  dispatching_rules_to_compare: string[];  // List of strategies
  sim_duration: number;
  snapshot_interval: number;
  random_seed: number | null;
}
```

**Response**:
```typescript
{
  results: Array<{
    dispatching_rule: string;
    snapshots: MetricSnapshot[];
    total_lots_arrived: number;
    total_lots_completed: number;
    mean_queue_time: number;
    mean_cycle_time: number;
    tool_utilisation: number[];
  }>;
}
```

---

## Code Examples

### Running Comparison Programmatically

```typescript
import { api } from './api';

const config = {
  num_tools: 4,
  num_products: 3,
  arrival_rate: 0.8,
  dispatching_rules_to_compare: ['fifo', 'optimised_spt'],
  // ... other params
};

const response = await api.runComparison(config);
console.log(response.results);
```

### Accessing Comparison Data

```typescript
// Find best strategy by queue time
const best = response.results.reduce((best, current) =>
  current.mean_queue_time < best.mean_queue_time ? current : best
);

console.log(`Best strategy: ${best.dispatching_rule}`);
console.log(`Queue time: ${best.mean_queue_time}`);
```

---

## User Guide

### Quick Start
1. ☑️ Enable "Comparison Mode"
2. ☑️ Select 2+ strategies
3. 🏃 Click "Run Comparison"
4. 📊 View side-by-side results

### Pro Tips
- Start with 2 strategies for clearer comparison
- Use same random seed for fair comparison (default: 42)
- Increase simulation duration for more stable results
- Restrict qualification matrix to see strategy differences

---

## Support

For questions or feature requests:
- Check the main `README.md` for general documentation
- See `ARCHITECTURE.md` for technical details
- Contact project team as per SOW-001

---

**Feature Status**: ✅ Implemented  
**Version**: 1.1.0  
**Date**: April 2026  
**SOW Reference**: SOW-001 (Phase 1 Enhancement)
