# Service Schedule Optimizer

A Python application for optimizing service schedules using set cover algorithms and cluster-based pattern recognition.

## Overview

The Service Schedule Optimizer is a sophisticated tool designed to help operators optimize their service schedules. It uses advanced algorithms to analyze patterns in service requirements and generates optimal calendar-based scheduling solutions.

## Features

- **Interactive Calendar Interface**: User-friendly GUI for date selection and schedule visualization
- **Smart Pattern Recognition**: Identifies optimal service patterns using cluster analysis
- **Set Cover Optimization**: Employs an efficient algorithm to minimize resource usage while maintaining coverage
- **Holiday Handling**: Automatically accounts for holidays and special service days
- **Working Days Constraints**: Ensures solutions respect operational limitations
- **Schedule Optimization**: Merges overlapping service patterns when beneficial

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/train-calendar-generator.git
cd train-calendar-generator
```
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

To run the application, use the following command:
```bash
python main.py
```
The GUI will guide you through:
1. Selecting a date range
2. Choosing specific dates for service requirements
3. Generating optimized schedule patterns
4. Viewing and exporting results

## Architecture

The project consists of three main components:

### 1. Set Cover Solver
Implements an optimized solution for the set cover problem, using a greedy approach with cost-based optimization and set merging capabilities.

Key features:
- Configurable weights for missing and extra elements
- Working days constraints
- Solution optimization through set merging

### 2. Cluster Generator
Handles the creation and management of day clusters based on patterns and holidays.

Features:
- Single and multi-day cluster generation
- Holiday pattern recognition
- Working days pattern optimization

### 3. GUI Interface
Provides an intuitive interface for interacting with the scheduling system.

Components:
- Calendar-based date selection
- Date range management
- Results visualization

## Configuration

The system can be configured through two main configuration classes:

1. `SolverConfig`: Controls the set cover solver behavior
   - `missing_weight`: Weight for elements missing from parent set
   - `extra_weight`: Weight for extra elements not in parent set
   - `max_iterations`: Maximum iterations for solution finding

2. `ClusterConfig`: Manages cluster generation parameters
   - `year`: Target year for scheduling
   - `weekdays`: List of weekday names
   - `holidays`: List of holiday dates

## Testing

Run the test suite using:
```bash
pytest
```
The test suite includes:
- Set cover solver tests
- Cluster generator tests
- Various edge cases and constraints


## License

This project is licensed under the MIT License - see the [LICENSE file](LICENSE) for details.