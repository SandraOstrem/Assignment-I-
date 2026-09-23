import unittest

from main import Participant, FitnessSession, Observation
from sample_data import load_scenario


class FitnessTests(unittest.TestCase):

    def make_session(self, name):
        profile, data = load_scenario(name)
        session = FitnessSession(Participant(profile))

        for item in data:
            session.add_observation(item)

        return session

    def test_five_scenarios(self):
        expected = {
            "resting": "resting",
            "moderate_activity": "moderate activity",
            "high_activity": "high activity",
            "recovery": "recovering",
            "poor_quality": "insufficient data"
        }

        for name, label in expected.items():
            with self.subTest(name=name):
                result = self.make_session(name).analyze().to_dict()
                self.assertEqual(result["classification"], label)

    def test_invalid_observation(self):
        _, data = load_scenario("resting")
        data[0]["heart_rate"] = None

        with self.assertRaises(ValueError):
            Observation.from_dict(data[0])

    def test_duplicate_timestamp(self):
        profile, data = load_scenario("resting")
        session = FitnessSession(Participant(profile))

        self.assertTrue(session.add_observation(data[0]))
        self.assertFalse(session.add_observation(data[0]))

    def test_results_and_encapsulation(self):
        session = self.make_session("high_activity")

        self.assertIsInstance(session.observations, tuple)

        result = session.analyze().to_dict()
        self.assertIn("heart_rate", result["summary"])


if __name__ == "__main__":
    unittest.main()