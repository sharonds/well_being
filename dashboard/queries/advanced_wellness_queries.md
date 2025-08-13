# Advanced Wellness Dashboard Queries

## Next 10 Analytics Panels to Add

### 6. Weekly Comparison

**Description**: Compare this week's average to last week's to see if you're improving.

**Visualization Type**: Bar Gauge or Stat

**Query**:
```flux
thisWeek = from(bucket: "metrics")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> mean()
  |> map(fn: (r) => ({r with _time: now(), week: "This Week"}))

lastWeek = from(bucket: "metrics")
  |> range(start: -14d, stop: -7d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> mean()
  |> map(fn: (r) => ({r with _time: now(), week: "Last Week"}))

union(tables: [thisWeek, lastWeek])
  |> pivot(rowKey:["_time"], columnKey: ["week"], valueColumn: "_value")
  |> map(fn: (r) => ({
      r with
      change: (r["This Week"] - r["Last Week"]),
      change_pct: ((r["This Week"] - r["Last Week"]) / r["Last Week"]) * 100.0
  }))
```

---

### 7. Best & Worst Days

**Description**: Table showing your top 5 best and worst scoring days with contributing factors.

**Visualization Type**: Table

**Query**:
```flux
// Best days
best = from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> top(n: 5)
  |> map(fn: (r) => ({r with category: "Best Days"}))

// Worst days  
worst = from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> bottom(n: 5)
  |> map(fn: (r) => ({r with category: "Worst Days"}))

union(tables: [best, worst])
  |> keep(columns: ["_time", "_value", "band", "category"])
  |> sort(columns: ["category", "_value"], desc: true)
```

---

### 8. Streak Counter

**Description**: Shows current streak of consecutive days above 70 (good scores).

**Visualization Type**: Stat

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> map(fn: (r) => ({
      r with
      good_day: if r._value >= 70 then 1 else 0
  }))
  |> sort(columns: ["_time"], desc: true)
  |> difference(nonNegative: false, columns: ["_time"])
  |> cumulativeSum(columns: ["good_day"])
  |> last()
```

---

### 9. Sleep Impact Analysis

**Description**: Correlation between sleep hours and next day's score.

**Visualization Type**: Scatter plot

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_contrib" and r.metric == "sleep")
  |> join(
      tables: {score: from(bucket: "metrics")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")},
      on: ["_time"]
  )
  |> map(fn: (r) => ({
      x: r._value_score,
      y: r._value * 8.0,  // Convert to hours
      label: "Sleep vs Score"
  }))
```

---

### 10. Day of Week Pattern

**Description**: Average score by day of week to identify patterns.

**Visualization Type**: Bar chart

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> map(fn: (r) => ({
      r with
      dayOfWeek: date.weekDay(t: r._time),
      dayName: if date.weekDay(t: r._time) == 0 then "Sunday"
               else if date.weekDay(t: r._time) == 1 then "Monday"
               else if date.weekDay(t: r._time) == 2 then "Tuesday"
               else if date.weekDay(t: r._time) == 3 then "Wednesday"
               else if date.weekDay(t: r._time) == 4 then "Thursday"
               else if date.weekDay(t: r._time) == 5 then "Friday"
               else "Saturday"
  }))
  |> group(columns: ["dayOfWeek", "dayName"])
  |> mean()
  |> sort(columns: ["dayOfWeek"])
```

---

### 11. Recovery Rate

**Description**: How quickly you bounce back from low scores.

**Visualization Type**: Time series

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> derivative(unit: 1d, nonNegative: false)
  |> map(fn: (r) => ({
      r with
      recovery: if r._value > 0 then r._value else 0.0,
      decline: if r._value < 0 then r._value else 0.0
  }))
```

---

### 12. Monthly Heatmap

**Description**: Calendar heatmap showing score intensity by day.

**Visualization Type**: Heatmap

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> map(fn: (r) => ({
      day: date.monthDay(t: r._time),
      hour: date.hour(t: r._time),
      score: r._value,
      intensity: r._value / 100.0
  }))
  |> group(columns: ["day"])
```

---

### 13. Missing Data Indicator

**Description**: Shows percentage of complete data over time.

**Visualization Type**: Time series (area)

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_contrib")
  |> group(columns: ["_time"])
  |> count()
  |> map(fn: (r) => ({
      r with
      completeness: (r._value / 4.0) * 100.0  // 4 metrics expected
  }))
```

---

### 14. Score Volatility

**Description**: Standard deviation of scores showing consistency.

**Visualization Type**: Stat

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> stddev()
  |> map(fn: (r) => ({
      r with
      volatility: if r._value < 5 then "Very Stable"
                  else if r._value < 10 then "Stable"
                  else if r._value < 15 then "Variable"
                  else "Highly Variable"
  }))
```

---

### 15. Predictive Trend

**Description**: Simple linear regression showing where scores are heading.

**Visualization Type**: Time series with forecast

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score" and r._field == "score")
  |> timedMovingAverage(every: 1d, period: 3d)
  |> holtWinters(n: 7, seasonality: 7)
```

---

## Dashboard Layout Recommendations

### Improved Layout (4 Rows):

```
Row 1: Key Metrics
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Current  │  7-Day   │  Week    │  Streak  │Volatility│
│  Score   │ Average  │ Change   │  Counter │  Level   │
└──────────┴──────────┴──────────┴──────────┴──────────┘

Row 2: Analysis
┌─────────────────┬─────────────────┬──────────────────┐
│   Component     │  Day of Week    │  Best/Worst      │
│   Breakdown     │   Pattern       │    Days          │
└─────────────────┴─────────────────┴──────────────────┘

Row 3: Trends
┌──────────────────────────┬──────────────────────────┐
│   Score Timeline         │   Recovery Rate          │
│   with Moving Average    │   Analysis               │
└──────────────────────────┴──────────────────────────┘

Row 4: Insights
┌─────────────────┬─────────────────┬──────────────────┐
│  Monthly        │   Sleep         │   Predictive     │
│  Heatmap        │   Impact        │    Trend         │
└─────────────────┴─────────────────┴──────────────────┘
```

## Quick Improvements for Current Dashboard

1. **Fix Bar Chart**: Add grouping by range name
2. **Add threshold lines** to timeline (70 for "good", 50 for "caution")
3. **Add annotations** for best/worst days
4. **Color code** the table based on score ranges
5. **Add sparklines** to the stat panels

Would you like me to create the complete enhanced dashboard JSON with all 15 panels?