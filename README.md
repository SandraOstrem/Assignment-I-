# ACIT-4420-Python-Programming-Assignment-I-

# Smart Fitness Session Analyzer

**ACIT4420 – Python Programming Assignment I**  
**Option A: Smart Fitness Session Analyzer**

**Student:** Sandra Østrem  

## 1. Project Description

This project is a Python application that analyzes simulated fitness data using object-oriented programming.

The program uses the data generator provided with the assignment to simulate measurements from wearable fitness devices. It validates the measurements, calculates statistics, compares them with the participant's baseline values, and classifies each fitness session.

The program can identify five different session types:
- Resting
- Moderate activity
- High activity
- Recovering
- Insufficient data

## 2. Project Structure

    Assignment-I-/
    |
    |-- option_a_fitness/
    |   |-- DATA_DESCRIPTION.md
    |   |-- data_generator.py
    |   |-- example_usage.py
    |
    |-- main.py
    |-- sample_data.py
    |-- tests.py
    |-- requirements.txt
    |-- README.md

The `option_a_fitness` folder contains the original files provided with the assignment. The data generator has not been modified.

The remaining Python files contain my implementation of the fitness analyzer.

## 3. Class Design

The program uses four classes:

### Participant

Stores the participant's ID and baseline measurements for heart rate, skin response and temperature.

### Observation

Represents a single sensor observation.

The `from_dict()` class method creates an observation from the dictionaries provided by the data generator. It also validates the measurements before creating the object.

### FitnessSession

Contains a participant and the observations collected during a fitness session.

It handles adding observations, rejecting invalid data and analyzing the complete session.

### AnalysisResult

Stores the results of the analysis, including the classification, statistics, changes from baseline and the number of accepted and rejected observations.

The results can also be returned as a dictionary.

## 4. Object-Oriented Programming

**Composition:** FitnessSession contains a Participant object and multiple Observation objects.

**Encapsulation:** Observations are stored in the protected-style `_observations` attribute. New observations are added using `add_observation()`, and a read-only tuple is available through the `observations` property.

**Class method:** `Observation.from_dict()` creates observation objects from dictionaries.

**Inheritance:** Composition was chosen instead of inheritance because the four classes represent different concepts and do not have a natural parent-child relationship. Inheritance and method overriding would add unnecessary complexity to this design.

The program also uses standalone functions for validation, calculations, recovery detection, classification and reporting.

## 5. Validation and Classification

The program validates all incoming observations before using them.

Observations are rejected if they contain missing or invalid measurements, values outside the allowed ranges, poor signal quality or duplicate timestamps.

Signal quality must be at least 0.60.

A session requires at least four valid observations, and at least 50% of the observations must be usable.

The classification uses the following rules:

| Classification | Rule |
|---|---|
| Resting | Low activity and heart rate near baseline |
| Moderate activity | Activity >= 0.25 or heart rate >= 15 above baseline |
| High activity | Activity >= 0.65 and heart rate >= 40 above baseline |
| Recovering | Heart rate and activity decrease significantly toward the end |
| Insufficient data | Not enough valid observations |

Recovery is detected by comparing the first third and last third of the session.

The program also calculates the average, minimum and maximum values for each sensor measurement.

These classification thresholds are assumptions made for this assignment, not medical guidelines.

## 6. Installation and Running

The program requires Python 3 and uses only the Python standard library. No additional packages are required.

Clone the repository:

    git clone https://github.com/SandraOstrem/Assignment-I-.git

Open the project folder:

    cd Assignment-I-

Run the program:

    python main.py

On systems that use `python3`, run:

    python3 main.py

The program automatically generates and analyzes all five required scenarios.

## 7. Example Output

An example of the console output:

    RESTING
    Classification: resting
    Reason: Low activity and heart rate near baseline.
    Usable: 12
    Rejected: 0

    heart_rate {'average': 80, 'min': 76, 'max': 85}

    Changes from baseline:
    {'heart_rate': 2, 'skin_response': 0.02,
     'temperature': 0.02}

The program produces similar reports for moderate activity, high activity, recovery and poor-quality data.

## 8. Testing

The program includes unit tests in `tests.py`.

Run the tests with:

    python -m unittest tests -v

The tests cover:
- All five required fitness scenarios
- Invalid sensor observations
- Duplicate timestamps
- Result structure and encapsulation

All four unit tests passed during local testing.

## 9. Known Limitations

- The program uses simulated data rather than real wearable devices.
- Classification is based on predefined thresholds.
- Recovery detection compares only the beginning and end of a session.
- The classification rules are simplified and are not intended for medical use.
- The program does not store results between runs.
