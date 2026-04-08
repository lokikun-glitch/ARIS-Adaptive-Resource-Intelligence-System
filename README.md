# ARIS — Adaptive Resource Intelligence System

A Flask-based engineering dashboard for visualising and comparing classic optimisation algorithms. Enter your data, run an algorithm, and get results, a chart, and step-by-step execution logs in one place.

## Algorithms

| Module | Algorithm | Complexity |
|---|---|---|
| Algorithm Selector | Rule-based keyword matching | — |
| Cargo Optimization | Fractional Knapsack (Greedy) | O(n log n) |
| Job Scheduling | Activity Selection (Greedy) | O(n log n) |
| Network Optimization | Kruskal's MST | O(E log E) |
| Conflict Resolution | Graph Coloring (Backtracking) | O(m^n) |

## Project Structure

```
ARIS/
├── app.py                  # Flask app & API routes
├── requirements.txt
├── algorithms/
│   ├── cargo.py            # Fractional Knapsack
│   ├── scheduling.py       # Activity Selection
│   ├── network.py          # Kruskal's MST
│   ├── conflict.py         # Graph Coloring
│   └── selector.py         # Rule-based algorithm recommender
├── templates/
│   └── index.html          # Single-page UI
└── static/
    ├── style.css
    └── app.js
```

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

- Use the **Algorithm Selector** panel to describe your problem in plain English and get a recommendation.
- Each algorithm panel has a **Random Input** button so you can try it immediately.
- Enable **Show steps** to see the algorithm's decision log.
- All results include execution time in milliseconds.