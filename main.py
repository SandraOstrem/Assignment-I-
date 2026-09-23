
from math import isfinite
from statistics import mean

from sample_data import load_scenario
from option_a_fitness.data_generator import available_scenarios


# Valid ranges for sensor measurements
RANGES = {
    "heart_rate": (35, 205),
    "skin_response": (0, 100),
    "temperature": (25, 42),
    "activity_level": (0, 1),
    "signal_quality": (0, 1)
}


# Standalone functions

def valid_number(value, low, high):
    return (
        type(value) in (int, float)
        and isfinite(value)
        and low <= value <= high
    )


def validate_observation(data):
    if not isinstance(data, dict):
        return ["not a dictionary"]

    errors = []

    if type(data.get("timestamp")) is not int or data["timestamp"] < 0:
        errors.append("invalid timestamp")

    for field, (low, high) in RANGES.items():
        if not valid_number(data.get(field), low, high):
            errors.append("invalid " + field)

    if (valid_number(data.get("signal_quality"), 0, 1)
            and data["signal_quality"] < 0.6):
        errors.append("poor signal quality")

    return errors


def summarize(values):
    return {
        "average": round(mean(values), 2),
        "min": min(values),
        "max": max(values)
    }


def detect_recovery(observations, baseline):
    if len(observations) < 6:
        return False

    ordered = sorted(observations, key=lambda obs: obs.timestamp)
    third = len(ordered) // 3

    first = ordered[:third]
    last = ordered[-third:]

    first_hr = mean(obs.heart_rate for obs in first)
    last_hr = mean(obs.heart_rate for obs in last)

    first_activity = mean(obs.activity_level for obs in first)
    last_activity = mean(obs.activity_level for obs in last)

    return (
        first_hr >= baseline + 25
        and first_hr - last_hr >= 20
        and first_activity - last_activity >= 0.25
    )


def classify(observations, baseline, total):
    if len(observations) < 4 or len(observations) * 2 < total:
        return "insufficient data", "Too few usable observations."

    if detect_recovery(observations, baseline):
        return "recovering", "Heart rate and activity fell toward the end."

    activity = mean(obs.activity_level for obs in observations)
    hr_change = mean(obs.heart_rate for obs in observations) - baseline

    if activity >= 0.65 and hr_change >= 40:
        return "high activity", "High activity and heart rate above baseline."

    if activity >= 0.25 or hr_change >= 15:
        return "moderate activity", "Activity or heart rate above resting levels."

    return "resting", "Low activity and heart rate near baseline."


# Class 1: Participant

class Participant:
    def __init__(self, profile):
        if (not isinstance(profile.get("participant_id"), str)
                or not profile["participant_id"].strip()):
            raise ValueError("Missing participant ID")

        baselines = {
            "baseline_heart_rate": (35, 205),
            "baseline_skin_response": (0, 100),
            "baseline_temperature": (25, 42)
        }

        for field, (low, high) in baselines.items():
            if not valid_number(profile.get(field), low, high):
                raise ValueError("Invalid " + field)

        self.id = profile["participant_id"]
        self.heart_rate = profile["baseline_heart_rate"]
        self.skin_response = profile["baseline_skin_response"]
        self.temperature = profile["baseline_temperature"]


# Class 2: Observation

class Observation:
    def __init__(self, data):
        self.timestamp = data["timestamp"]

        for field in RANGES:
            setattr(self, field, data[field])

    @classmethod
    def from_dict(cls, data):
        errors = validate_observation(data)

        if errors:
            raise ValueError(", ".join(errors))

        return cls(data)


# Class 3: AnalysisResult

class AnalysisResult:
    def __init__(self, participant_id, label, reason,
                 summary, changes, usable, rejected):

        self.data = {
            "participant": participant_id,
            "classification": label,
            "reason": reason,
            "summary": summary,
            "baseline_changes": changes,
            "usable": usable,
            "rejected": rejected
        }

    def to_dict(self):
        return self.data.copy()


# Class 4: FitnessSession

class FitnessSession:
    def __init__(self, participant):
        self.participant = participant
        self._observations = []
        self._rejected = []

    @property
    def observations(self):
        return tuple(self._observations)

    def add_observation(self, data):
        try:
            observation = Observation.from_dict(data)

        except ValueError as error:
            self._rejected.append(str(error))
            return False

        if any(obs.timestamp == observation.timestamp
               for obs in self._observations):
            self._rejected.append("duplicate timestamp")
            return False

        self._observations.append(observation)
        return True

    def analyze(self):
        total = len(self._observations) + len(self._rejected)

        label, reason = classify(
            self._observations,
            self.participant.heart_rate,
            total
        )

        summary = {}

        if self._observations:
            for field in RANGES:
                values = [
                    getattr(obs, field)
                    for obs in self._observations
                ]
                summary[field] = summarize(values)

        changes = {}

        for field in ("heart_rate", "skin_response", "temperature"):
            if summary:
                changes[field] = round(
                    summary[field]["average"]
                    - getattr(self.participant, field),
                    2
                )

        return AnalysisResult(
            self.participant.id,
            label,
            reason,
            summary,
            changes,
            len(self._observations),
            self._rejected.copy()
        )


# Console report

def print_report(name, result):
    data = result.to_dict()

    print("\n", name.upper())
    print("Classification:", data["classification"])
    print("Reason:", data["reason"])
    print("Usable:", data["usable"])
    print("Rejected:", len(data["rejected"]))

    for field, values in data["summary"].items():
        print(field, values)

    print("Changes from baseline:", data["baseline_changes"])

    if data["rejected"]:
        print("Example rejection:", data["rejected"][0])


# Run all five scenarios

def main():
    for name in available_scenarios():
        profile, raw_data = load_scenario(name)

        participant = Participant(profile)
        session = FitnessSession(participant)

        for item in raw_data:
            session.add_observation(item)

        result = session.analyze()
        print_report(name, result)


if __name__ == "__main__":
    main()