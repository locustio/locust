from locust import User, tag
from locust.exception import RescheduleTask
from locust.user.markov_taskset import (
    InvalidTransitionError,
    MarkovTaskSet,
    MarkovTaskTagError,
    NoMarkovTasksError,
    NonMarkovTaskTransitionError,
    transition,
    transitions,
)

import random

from .testcases import LocustTestCase


class TestMarkovTaskSet(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.locust = User(self.environment)

    def test_basic_markov_chain(self):
        """Test a simple markov chain with transitions between tasks"""
        log = []

        class MyMarkovTaskSet(MarkovTaskSet):
            @transition("t2")
            def t1(self):
                log.append(1)

            @transition("t3")
            def t2(self):
                log.append(2)

            @transition("t1")
            def t3(self):
                log.append(3)
                if len(log) >= 9:
                    self.interrupt(reschedule=False)

        ts = MyMarkovTaskSet(self.locust)
        self.assertRaises(RescheduleTask, lambda: ts.run())

        # Since transitions are deterministic in this test, we expect a repeating pattern
        self.assertEqual([1, 2, 3, 1, 2, 3, 1, 2, 3], log)

    def test_multiple_transitions(self):
        """Test multiple transitions"""
        log = []
        random.seed(12345)

        class MyMarkovTaskSet(MarkovTaskSet):
            @transition("t2")
            def t1(self):
                log.append(1)

            @transition("t1")
            @transition("t3")
            def t2(self):
                log.append(2)
                if len(log) >= 10:
                    self.interrupt(reschedule=False)

            @transition("t1")
            def t3(self):
                log.append(3)

        ts = MyMarkovTaskSet(self.locust)
        self.assertRaises(RescheduleTask, lambda: ts.run())

        # Check that we have at least one of each task type
        self.assertIn(1, log)
        self.assertIn(2, log)
        self.assertIn(3, log)

    def test_weighted_transitions(self):
        """Test transitions with different weights"""
        log = []
        random.seed(12345)

        class MyMarkovTaskSet(MarkovTaskSet):
            @transition("t2", weight=1)
            def t1(self):
                log.append(1)

            @transitions({"t1": 2, "t3": 1})
            def t2(self):
                log.append(2)
                if len(log) >= 10:
                    self.interrupt(reschedule=False)

            @transition("t1")
            def t3(self):
                log.append(3)

        ts = MyMarkovTaskSet(self.locust)
        self.assertRaises(RescheduleTask, lambda: ts.run())

        # Check that we have at least one of each task type
        self.assertIn(1, log)
        self.assertIn(2, log)
        self.assertIn(3, log)

    def test_transitions_list_format(self):
        """Test using the transitions decorator with a list format"""
        log = []
        random.seed(12345)

        class MyMarkovTaskSet(MarkovTaskSet):
            @transitions([("t2", 1), "t3"])  # t3 has default weight of 1
            def t1(self):
                log.append(1)

            @transition("t1")
            def t2(self):
                log.append(2)

            @transition("t1")
            def t3(self):
                log.append(3)
                if len(log) >= 10:
                    self.interrupt(reschedule=False)

        ts = MyMarkovTaskSet(self.locust)
        self.assertRaises(RescheduleTask, lambda: ts.run())

        # Check that we have at least one of each task type
        self.assertIn(1, log)
        self.assertIn(2, log)
        self.assertIn(3, log)

    def test_validation_no_markov_tasks(self):
        """Test that an exception is raised when no markov tasks are defined"""
        with self.assertRaises(NoMarkovTasksError) as context:
            class EmptyMarkovTaskSet(MarkovTaskSet):
                ...

        self.assertIn("No Markov tasks defined", str(context.exception))

    def test_validation_invalid_transition(self):
        """Test that an exception is raised when a transition points to a non-existent task"""
        with self.assertRaises(InvalidTransitionError) as context:
            class InvalidTransitionTaskSet(MarkovTaskSet):
                @transition("non_existent_task")
                def t1(self):
                    pass

        self.assertIn("invalid since no such element exists", str(context.exception))

    def test_validation_non_markov_transition(self):
        """Test that an exception is raised when a transition points to a non-markov task"""
        with self.assertRaises(NonMarkovTaskTransitionError) as context:
            class NonMarkovTransitionTaskSet(MarkovTaskSet):
                @transition("t2")
                def t1(self):
                    pass

                def t2(self):
                    pass

        self.assertIn("cannot be used as a target for a transition", str(context.exception))

    def test_validation_unreachable_tasks(self):
        """Test that a warning is logged when there are unreachable tasks"""

        class UnreachableTaskSet(MarkovTaskSet):
            @transition("t2")
            def t1(self):
                pass

            @transition("t1")
            def t2(self):
                pass

            @transition("t3")  # This task is unreachable from t1 and t2
            def t3(self):
                pass

        UnreachableTaskSet(self.locust)

        # Check that a warning was logged
        self.assertTrue(any("unreachable" in warning for warning in self.mocked_log.warning))

    def test_validation_unreachable_tasks_because_of_weights(self):
        """Test that a warning is logged when there are unreachable tasks"""

        class UnreachableTaskSet(MarkovTaskSet):
            @transition("t2", 0)
            def t1(self):
                pass

            @transition("t1")
            def t2(self):
                pass

        UnreachableTaskSet(self.locust)

        # Check that a warning was logged
        self.assertTrue(any("unreachable" in warning for warning in self.mocked_log.warning))

    def test_validation_no_tags(self):
        """Test that an exception is raised when a task has tags"""
        with self.assertRaises(MarkovTaskTagError) as context:
            class TaggedTaskSet(MarkovTaskSet):
                @tag("tag1")
                @transition("t2")
                def t1(self):
                    pass

                @transition("t1")
                def t2(self):
                    pass

        self.assertIn("Tags are unsupported", str(context.exception))

    def test_abstract_markov_taskset(self):
        """Test that abstract MarkovTaskSets are not validated"""

        # Define a class with abstract=True explicitly
        class AbstractMarkovTaskSet(MarkovTaskSet):
            abstract = True

        # This should not raise an exception even though it has no tasks
        AbstractMarkovTaskSet(self.locust)
