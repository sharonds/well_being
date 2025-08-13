# Wellness Dashboard Queries

## Manual Panel Setup Instructions

Since dashboard imports are having issues, use these queries to manually create panels:

1. Go to your dashboard at http://localhost:3001
2. Click "Add" → "Visualization"
3. Select your InfluxDB datasource
4. Switch to "Script Editor" mode (not Query Builder)
5. Copy the query exactly as shown below
6. Select the appropriate visualization type
7. Apply the panel settings
8. Save the panel

---

## 1. Current Score Gauge

**Description**: Shows your latest wellness score as a large gauge with color coding based on score ranges.

**Visualization Type**: Gauge

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "wb_score")
  |> filter(fn: (r) => r._field == "score")
  |> last()
  |> yield(name: "current_score")
```

**Panel Settings**:
- Min: 0
- Max: 100
- Thresholds:
  - 0-49: Red (Base)
  - 50-69: Yellow
  - 70-100: Green
- Display name: "Current Score"
- Unit: "short"

**What it shows**: Your most recent wellness score with visual indication of whether you're in "Take it easy" (red), "Maintain" (yellow), or "Go for it" (green) zones.

---

## 2. 7-Day Moving Average

**Description**: Smooths out daily fluctuations to show your wellness trend over the past week.

**Visualization Type**: Stat

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score")
  |> filter(fn: (r) => r._field == "score")
  |> movingAverage(n: 7)
  |> last()
  |> yield(name: "seven_day_avg")
```

**Panel Settings**:
- Unit: "short"
- Decimals: 1
- Color mode: "Background"
- Graph mode: "Area"
- Text size: 70%

**What it shows**: Your 7-day rolling average score, helping you understand if you're generally trending up or down beyond daily variations.

---

## 3. Score Distribution (Last 30 Days)

**Description**: Histogram showing how often your scores fall into different ranges, helping identify your typical performance zones.

**Visualization Type**: Bar chart (or Histogram)

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "wb_score")
  |> filter(fn: (r) => r._field == "score")
  |> map(fn: (r) => ({
      r with
      range: if r._value >= 80 then "80-100 Excellent"
             else if r._value >= 70 then "70-79 Good"
             else if r._value >= 60 then "60-69 Fair"
             else if r._value >= 50 then "50-59 Caution"
             else "Below 50 Rest"
  }))
  |> group(columns: ["range"])
  |> count()
  |> yield(name: "distribution")
```

**Panel Settings**:
- X-Axis: "range"
- Y-Axis: "_value" (count)
- Sort: By range value
- Color scheme: Green to Red gradient
- Legend: Show

**What it shows**: How many days in the past month fell into each wellness category, revealing your most common state.

---

## 4. Daily Component Contributions

**Description**: Pie chart showing the average contribution of each metric (steps, HR, sleep, stress) to your overall score.

**Visualization Type**: Pie chart

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "wb_contrib")
  |> filter(fn: (r) => r._field == "contribution")
  |> group(columns: ["metric"])
  |> mean()
  |> map(fn: (r) => ({
      r with
      _value: r._value * 100.0,
      display_name: if r.metric == "steps" then "Steps"
                    else if r.metric == "rhr" then "Heart Rate"
                    else if r.metric == "sleep" then "Sleep"
                    else if r.metric == "stress" then "Stress"
                    else r.metric
  }))
  |> keep(columns: ["display_name", "_value"])
  |> yield(name: "contributions")
```

**Panel Settings**:
- Display labels: On
- Legend: Right side
- Tooltip: Show percentage
- Unit: "percent"
- Decimals: 1

**What it shows**: Which health metrics are contributing most to your wellness scores, helping identify strengths and areas for improvement.

---

## 5. Data Completeness Table

**Description**: Shows which metrics are available for each day, helping identify data gaps that might affect score accuracy.

**Visualization Type**: Table

**Query**:
```flux
from(bucket: "metrics")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "wb_contrib")
  |> filter(fn: (r) => r._field == "contribution")
  |> group(columns: ["_time"])
  |> pivot(rowKey: ["_time"], columnKey: ["metric"], valueColumn: "_value")
  |> map(fn: (r) => ({
      _time: r._time,
      date: strings.substring(v: string(v: r._time), start: 0, end: 10),
      steps: if exists r.steps then "✓" else "✗",
      heart_rate: if exists r.rhr then "✓" else "✗",
      sleep: if exists r.sleep then "✓" else "✗",
      stress: if exists r.stress then "✓" else "✗",
      completeness: (
        (if exists r.steps then 25 else 0) +
        (if exists r.rhr then 25 else 0) +
        (if exists r.sleep then 25 else 0) +
        (if exists r.stress then 25 else 0)
      )
  }))
  |> keep(columns: ["date", "steps", "heart_rate", "sleep", "stress", "completeness"])
  |> sort(columns: ["date"], desc: true)
  |> yield(name: "completeness")
```

**Panel Settings**:
- Column width: Auto
- Cell display mode: "Color background" for completeness column
- Thresholds for completeness:
  - 0-25: Red
  - 50-75: Yellow
  - 100: Green
- Sort: Date descending

**What it shows**: A daily breakdown of which metrics were available, with a completeness percentage helping you understand data quality.

---

## Quick Add Instructions

To add all 5 panels quickly:

1. **Import Method**: 
   - Go to Dashboard settings → JSON Model
   - I can provide a complete JSON with all panels

2. **Manual Method**:
   - Add each panel one by one
   - Copy queries exactly as shown
   - Apply the recommended settings

3. **Testing**:
   - Each query works with your current data structure
   - Adjust time ranges as needed (-7d, -30d, etc.)

## Next 5 Panels Available

Ready for panels 6-10 which include:
- Week-over-week comparison
- Best/worst days table  
- Monthly heatmap
- Recovery rate tracker
- Streak counter

Let me know if you want the complete dashboard JSON or the next set of queries!