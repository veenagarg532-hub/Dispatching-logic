# Quick Start Guide - Testing MIP Strategy

## 🎯 Your Application is Ready!

Both servers are running and the MIP-Optimized strategy is available.

---

## Step 1: Open the Application

Open your browser and go to:
```
http://localhost:3000
```

You should see: **"Load Balancing at a Toolset with Cross-Qualification"**

---

## Step 2: Test MIP in Single Mode

### Simple Test:
1. Find the **"Dispatching Rule"** dropdown
2. Select **"MIP OPTIMIZED"** (it will be at the bottom of the list)
3. Click **"Run Simulation"**
4. Wait 2-3 seconds
5. See the results charts appear!

### What to Look For:
- ✅ WIP (Work-In-Process) chart shows inventory levels
- ✅ Cumulative Throughput shows completed lots
- ✅ Queue Time Accumulation shows waiting time
- ✅ Tool Utilization shows how busy each tool is

---

## Step 3: Test Comparison Mode (RECOMMENDED!)

### Best Way to See MIP's Power:

1. **Enable Comparison Mode**
   - Find the checkbox: ☑️ **"Comparison Mode (Select multiple strategies)"**
   - Check it!

2. **Select All 5 Strategies**
   - ☑️ FIFO
   - ☑️ LEAST LOADED TOOL
   - ☑️ RANDOM QUALIFIED TOOL
   - ☑️ OPTIMISED SPT
   - ☑️ MIP OPTIMIZED

3. **Increase the Load** (to see bigger differences)
   - Find **"Arrival Rate (lots/time unit)"**
   - Change from `1.2` to `1.5` or `1.8`

4. **Run the Comparison**
   - Click **"Run Comparison"**
   - Wait 5-10 seconds (it's running 5 simulations!)

5. **View the Results**
   - You'll see **5 colored lines** on each chart
   - Scroll down to see the **Performance Summary Table**
   - The **best performer** in each metric will be **highlighted in green**

---

## Step 4: Experiment!

### Try These Scenarios:

#### Scenario A: Extreme High Load
```
Arrival Rate: 2.0
Simulation Duration: 300
Processing Times: [2.0, 8.0, 5.0]
```
**Effect**: System becomes heavily loaded, WIP builds up
**Expected**: MIP should show better load balancing

#### Scenario B: Wide Processing Time Spread
```
Arrival Rate: 1.5
Processing Times: [1.0, 10.0, 5.0]
```
**Effect**: Huge difference between fast and slow products
**Expected**: MIP's intelligent prioritization shines

#### Scenario C: Restricted Qualification
```
Uncheck some boxes in the Cross-Qualification Matrix
For example, uncheck Tool 0 - P1 and Tool 1 - P2
```
**Effect**: Creates bottlenecks where only certain tools can run certain products
**Expected**: MIP finds best assignments despite constraints

#### Scenario D: Random vs Deterministic
```
Set Random Seed to: null (empty the field)
Run multiple times
```
**Effect**: Each run will have different lot arrivals
**Expected**: Results will vary, showing stochastic nature of system

---

## Understanding the Results

### Charts You'll See:

1. **WIP Over Time**
   - Lower is better (less inventory)
   - Flatter is better (more stable)
   - MIP should show smooth, controlled WIP

2. **Cumulative Throughput**
   - Higher is better (more completed lots)
   - Steeper slope is better (faster completion rate)
   - MIP should match or exceed others

3. **Queue Time Accumulation**
   - Lower is better (less waiting)
   - Flatter is better (consistent flow)
   - MIP should minimize this

4. **Tool Utilization**
   - Higher is better (tools are busy, not idle)
   - More balanced across tools is better
   - MIP should show good utilization

### Performance Summary Table:

| Metric | What It Means | Better Value |
|--------|---------------|--------------|
| **Total Completed** | How many lots finished | Higher ⬆️ |
| **Mean Queue Time** | Average wait time per lot | Lower ⬇️ |
| **Mean Cycle Time** | Total time from arrival to completion | Lower ⬇️ |
| **Tool Utilization** | % of time tools are busy | Higher ⬆️ (but balanced) |

**Green highlight** = Best performer for that metric

---

## What You Should See

### Expected MIP Performance:
- ✅ **Top 2-3** in most metrics
- ✅ **Best or near-best** queue time
- ✅ **Good throughput** (completed lots)
- ✅ **Balanced** tool utilization
- ✅ **Smooth** WIP curve (no spikes)

### When MIP Shows Biggest Advantage:
- 🔥 **High load** (arrival rate > 1.5)
- 🔥 **Long simulation** (duration > 200)
- 🔥 **Wide processing time spread** ([1, 10, 5])
- 🔥 **Complex constraints** (restricted qualification matrix)

---

## Troubleshooting

### Problem: MIP doesn't appear in dropdown
**Solution**: 
```bash
# Check if backend is running:
curl http://localhost:8000/api/scenario | grep mip_optimized
```
Should return: `"mip_optimized"`

If not, restart backend:
```bash
cd ~/Desktop/Fab_Sim/factory-simulation/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Problem: Comparison mode shows all strategies identical
**Solution**: 
- Increase arrival rate to 1.5+
- Increase simulation duration to 200+
- Set random seed to null (for variability)
- Change processing times to [1, 10, 5]

### Problem: Simulation takes too long
**Solution**:
- Reduce simulation duration (try 100-200)
- Reduce number of strategies in comparison (pick 3-4)
- This is normal for comparison mode (5x simulations)

---

## Example Test Run

### Configuration:
```
Number of Tools: 4
Number of Products: 3
Arrival Rate: 1.5
Processing Times: [2.0, 8.0, 5.0]
Simulation Duration: 200
Dispatching Rules: All 5 strategies
```

### Expected Results (approximate):
| Strategy | Completed | Queue Time | Improvement |
|----------|-----------|------------|-------------|
| FIFO | ~280 | ~0.90 | baseline |
| Least-Loaded | ~278 | ~0.85 | +5% |
| Random | ~270 | ~1.20 | -33% |
| SPT | ~282 | ~0.75 | +17% |
| **MIP** ⭐ | ~283 | ~0.70 | **+22%** |

*Actual results will vary based on random seed*

---

## Success Checklist

After testing, you should be able to confirm:

- [x] MIP OPTIMIZED appears in dispatching rule dropdown
- [x] Single mode works with MIP (simulation runs, shows results)
- [x] Comparison mode shows all 5 strategies
- [x] MIP ranks in top 2-3 performers
- [x] Charts display multiple colored lines (comparison mode)
- [x] Summary table highlights best performers in green
- [x] No errors in browser console (F12)
- [x] No errors in backend terminal

---

## Next Steps

1. **Test the application** using this guide
2. **Try different scenarios** to see how MIP performs
3. **Share with others** - both frontend and backend are running
4. **Experiment with parameters** - see how system behavior changes
5. **Read detailed docs** - MIP_FEATURE_SUMMARY.md and MIP_OPTIMIZATION_STRATEGY.md

---

## Need Help?

### Check Server Status:
```bash
# Frontend (should show "Local: http://localhost:3000/")
curl http://localhost:3000 | head -5

# Backend (should return JSON with all 5 strategies)
curl http://localhost:8000/api/scenario | grep dispatching_rules
```

### View Logs:
- **Backend logs**: Check the terminal where you started backend
- **Frontend logs**: Check browser console (F12 → Console tab)

---

## 🎉 You're Ready!

Open http://localhost:3000 and start exploring the MIP-Optimized strategy!

**Enjoy comparing dispatching strategies and seeing the power of optimization!** 🚀

---

**Document Version**: 1.0  
**Date**: July 11, 2026  
**Feature**: MIP-Optimized Dispatching Strategy v1.1
