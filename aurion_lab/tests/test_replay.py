import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aurion_lab.replay import ContractError, choose_action, run, transform


class ReplayTests(unittest.TestCase):
    def test_action_choice_is_order_independent(self):
        actions = [
            {"type": "wait"},
            {"target": "slime-1", "type": "attack"},
            {"direction": "north", "type": "move"},
        ]
        expected = choose_action(actions)
        self.assertEqual(expected, choose_action(list(reversed(actions))))

    def test_transform_is_stable(self):
        source = {
            "schema": "aurion.rl.observation.v1",
            "episode_id": "episode",
            "tick": 4,
            "observation": {"hp": 8},
            "available_actions": [{"type": "wait"}, {"type": "attack", "target": "x"}],
        }
        self.assertEqual(transform(source), transform(json.loads(json.dumps(source))))

    def test_empty_actions_fail_closed(self):
        with self.assertRaises(ContractError):
            transform({
                "schema": "aurion.rl.observation.v1",
                "episode_id": "episode",
                "tick": 0,
                "available_actions": [],
            })

    def test_file_replay_is_byte_reproducible(self):
        root = Path(__file__).resolve().parents[1]
        fixture = root / "fixtures" / "sample_observations.jsonl"
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.jsonl"
            b = Path(tmp) / "b.jsonl"
            self.assertEqual(run(fixture, a), 3)
            self.assertEqual(run(fixture, b), 3)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(
                hashlib.sha256(a.read_bytes()).hexdigest(),
                hashlib.sha256(b.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
