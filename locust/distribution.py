import math
from itertools import combinations_with_replacement
from operator import attrgetter
from typing import Dict, List, Type

from locust import User


def weight_users(user_classes: List[Type[User]], user_count: int) -> Dict[str, int]:
    """
    Compute the desired state of users using the weight of each user class.

    :param user_classes: the list of user class
    :param user_count: total number of users
    :return: the set of users to run
    """
    assert user_count >= 0

    if len(user_classes) == 0:
        return {}

    user_classes = sorted(user_classes, key=attrgetter("__name__"))

    user_classes_count = {user_class.__name__: 0 for user_class in user_classes}

    # If the number of users is less than the number of user classes, at most one user of each user class
    # is chosen. User classes with higher weight are chosen first.
    if user_count <= len(user_classes):
        user_classes_count.update(
            {
                user_class.__name__: 1
                for user_class in sorted(user_classes, key=attrgetter("weight"), reverse=True)[:user_count]
            }
        )
        return user_classes_count

    # If the number of users is greater than or equal to the number of user classes, at least one user of each
    # user class will be chosen. The greater number of users is, the better the actual distribution
    # of users will match the desired one (as dictated by the weight attributes).
    weights = list(map(attrgetter("weight"), user_classes))
    relative_weights = [weight / sum(weights) for weight in weights]
    user_classes_count = {
        user_class.__name__: round(relative_weight * user_count) or 1
        for user_class, relative_weight in zip(user_classes, relative_weights)
    }

    if sum(user_classes_count.values()) == user_count:
        return user_classes_count

    else:
        user_classes_count = _find_ideal_users_to_add_or_remove(
            user_classes, user_count - sum(user_classes_count.values()), user_classes_count
        )
        assert sum(user_classes_count.values()) == user_count
        return user_classes_count


def _find_ideal_users_to_add_or_remove(
    user_classes: List[Type[User]], user_count_to_add_or_remove: int, user_classes_count: Dict[str, int]
) -> Dict[str, int]:
    sign = -1 if user_count_to_add_or_remove < 0 else 1

    user_count_to_add_or_remove = abs(user_count_to_add_or_remove)

    assert user_count_to_add_or_remove <= len(user_classes), user_count_to_add_or_remove

    # Formula for combination with replacement
    # (https://www.tutorialspoint.com/statistics/combination_with_replacement.htm)
    number_of_combinations = math.factorial(len(user_classes) + user_count_to_add_or_remove - 1) / (
        math.factorial(user_count_to_add_or_remove) * math.factorial(len(user_classes) - 1)
    )

    # If the number of combinations with replacement is above this threshold, we simply add/remove
    # users for the first "number_of_users_to_add_or_remove" users. Otherwise, computing the best
    # distribution is too expensive in terms of computation.
    max_number_of_combinations_threshold = 1000

    if number_of_combinations <= max_number_of_combinations_threshold:
        user_classes_count_candidates: Dict[float, Dict[str, int]] = {}
        for user_classes_combination in combinations_with_replacement(user_classes, user_count_to_add_or_remove):
            # Copy in order to not mutate `user_classes_count` for the parent scope
            user_classes_count_candidate = user_classes_count.copy()
            for user_class in user_classes_combination:
                user_classes_count_candidate[user_class.__name__] += sign
            distance = distance_from_desired_distribution(user_classes, user_classes_count_candidate)
            if distance not in user_classes_count_candidates:
                user_classes_count_candidates[distance] = user_classes_count_candidate.copy()

        return user_classes_count_candidates[min(user_classes_count_candidates.keys())]

    else:
        # Copy in order to not mutate `user_classes_count` for the parent scope
        user_classes_count_candidate = user_classes_count.copy()
        for user_class in user_classes[:user_count_to_add_or_remove]:
            user_classes_count_candidate[user_class.__name__] += sign
        return user_classes_count_candidate


def distance_from_desired_distribution(user_classes: List[Type[User]], user_classes_count: Dict[str, int]) -> float:
    actual_ratio_of_user_class = {
        user_class: user_class_count / sum(user_classes_count.values())
        for user_class, user_class_count in user_classes_count.items()
    }

    expected_ratio_of_user_class = {
        user_class.__name__: user_class.weight / sum(map(attrgetter("weight"), user_classes))
        for user_class in user_classes
    }

    differences = [
        actual_ratio_of_user_class[user_class] - expected_ratio
        for user_class, expected_ratio in expected_ratio_of_user_class.items()
    ]

    return math.sqrt(math.fsum(map(lambda x: x ** 2, differences)))
