# ARIS — Adaptive Resource Intelligence System

A Flask-based engineering dashboard for visualising and comparing classic optimisation algorithms. Describe your problem in plain English to get an algorithm recommendation, then enter your data to get results, a chart, and a step-by-step execution log — all in one place.

---

## Algorithms

| Module | Algorithm | Complexity | Problem Solved |
|---|---|---|---|
| Algorithm Selector | Rule-based keyword matching | — | Recommends the right algorithm from a plain-English description |
| Cargo Optimization | Fractional Knapsack (Greedy) | O(n log n) | Maximise profit from items with weights under a capacity constraint |
| Job Scheduling | Activity Selection (Greedy) | O(n log n) | Select the maximum number of non-overlapping time intervals |
| Network Optimization | Kruskal's MST | O(E log E) | Connect all nodes in a graph at the minimum total edge cost |
| Conflict Resolution | Graph Coloring (Backtracking) | O(m^n) | Assign resources so no two conflicting entities share the same one |

---

## Project Structure

```
ARIS/
├── app.py                    # Flask app & all API routes
├── requirements.txt
├── algorithms/
│   ├── cargo.py              # Fractional Knapsack
│   ├── scheduling.py         # Activity Selection
│   ├── network.py            # Kruskal's MST
│   ├── conflict.py           # Graph Coloring (Backtracking)
│   └── selector.py           # Rule-based algorithm recommender
├── pages/                    # Per-algorithm page logic helpers
│   ├── cargo_page.py
│   ├── scheduling_page.py
│   ├── network_page.py
│   ├── conflict_page.py
│   └── selector_page.py
├── templates/
│   └── index.html            # Single-page UI
└── static/
    ├── style.css
    └── app.js
```

---

## API Reference

Each algorithm exposes two endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/selector` | POST | Recommend an algorithm from a plain-English description |
| `/api/cargo` | POST | Run Fractional Knapsack on item data |
| `/api/cargo/random` | GET | Generate random cargo items |
| `/api/scheduling` | POST | Run Activity Selection on job data |
| `/api/scheduling/random` | GET | Generate random jobs |
| `/api/network` | POST | Run Kruskal's MST on a graph |
| `/api/network/random` | GET | Generate a random graph |
| `/api/conflict` | POST | Run Graph Coloring on a conflict graph |
| `/api/conflict/random` | GET | Generate a random conflict graph |

Every `POST` response includes: result data, `exec_time_ms`, `steps` (decision log), and `chart` (Base64-encoded PNG).

### Input Formats

**Cargo** (`/api/cargo`)
```
capacity: <number>
items:
  <name>, <weight>, <profit>
  <name>, <weight>, <profit>
```

**Scheduling** (`/api/scheduling`)
```
jobs:
  <name>, <start>, <end>
  <name>, <start>, <end>
```

**Network** (`/api/network`)
```
<node1>, <node2>, <node3>, ...
<u>, <v>, <weight>
<u>, <v>, <weight>
```

**Conflict** (`/api/conflict`)
```
<node1>, <node2>, <node3>, ...
<u>, <v>
<u>, <v>
```

---

## Algorithm Selector

The selector (`algorithms/selector.py`) uses rule-based keyword scoring — no ML required:

- **Keywords** matched in your description → **1 point** each
- **Phrases** matched → **2 points** each (higher signal)
- **Confidence tiers:** High (≥ 4 signals), Medium (2–3), Low (1)
- **Ambiguity flag:** raised when the top two candidates are within 1 point of each other

Example input: *"I need to schedule non-overlapping meetings across time slots"*
→ Recommends **Activity Selection (Greedy)** with High confidence.

---

## Installation

```bash
pip install -r requirements.txt
```

**Dependencies:** `flask`, `matplotlib`, `networkx`

## Running

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

1. Use the **Algorithm Selector** panel to describe your problem in plain English and receive a recommendation.
2. Navigate to the relevant algorithm panel and click **Random Input** to auto-fill sample data.
3. Click **Run** to execute — results include a chart, key metrics, and execution time in milliseconds.
4. Enable **Show steps** to see the algorithm's full decision log.

---

## Security & Stability

- **1 MB request cap** (`MAX_CONTENT_LENGTH`) to prevent oversized payloads.
- **Per-line input validation** with descriptive error messages for each malformed entry.
- Graph Coloring (exponential backtracking) is implicitly bounded by the request size limit to prevent DoS.
