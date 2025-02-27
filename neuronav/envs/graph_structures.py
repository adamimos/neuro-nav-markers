import enum
import numpy as np


class GraphStructure(enum.Enum):
    two_step = "two_step"
    ring = "ring"
    two_way_linear = "two_way_linear"
    linear = "linear"
    t_graph = "t_graph"
    neighborhood = "neighborhood"
    human_a = "human_a"
    human_b = "human_b"
    t_loop = "t_loop"
    variable_magnitude = "variable_magnitude"
    three_arm_bandit = "three_arm_bandit"


def two_step():
    reward_locs = {3: 1, 4: -1, 5: 0.5, 6: 0.5}
    edges = [[1, 2], [3, 4], [5, 6], [], [], [], []]
    objects = {'rewards': reward_locs}
    return objects, edges


def three_arm_bandit():
    reward_locs = {1: 1, 2: 0.5, 3: -0.5}
    edges = [[1, 2, 3], [], [], []]
    objects = {'rewards': reward_locs}
    return objects, edges



def two_way_linear():
    reward_locs = {4: 1}
    edges = [[0, 1], [0, 2], [1, 3], [2, 4], [3, 4]]
    objects = {'rewards': reward_locs}
    return objects, edges


def ring():
    reward_locs = {4: 1}
    edges = [[1, 5], [0, 2], [1, 3], [2, 4], [3, 5], [4, 0]]
    objects = {'rewards': reward_locs}
    return objects, edges


def linear():
    reward_locs = {5: 1}
    edges = [[1], [2], [3], [4], [5], []]
    objects = {'rewards': reward_locs}
    return objects, edges


def t_graph():
    reward_locs = {5: 1}
    edges = [[1, 0], [2, 1], [3, 4], [5, 3], [6, 4], [], []]
    objects = {'rewards': reward_locs}
    return objects, edges


def neighborhood():
    reward_locs = {14: 1}
    edges = [
        [1, 2, 3, 4],
        [0, 2, 3, 4],
        [5, 1, 0, 4],
        [10, 4, 0, 1],
        [0, 1, 2, 3],
        [2, 6, 8, 9],
        [5, 8, 7, 9],
        [5, 9, 6, 8],
        [7, 6, 5, 9],
        [6, 7, 8, 11],
        [3, 12, 13, 14],
        [9, 12, 13, 14],
        [10, 11, 13, 14],
        [11, 10, 12, 14],
        [10, 12, 11, 13],
    ]
    objects = {'rewards': reward_locs}
    return objects, edges


def human_a():
    reward_locs = {4: 10, 5: 1}
    edges = [[2], [3], [4], [5], [], []]
    objects = {'rewards': reward_locs}
    return objects, edges


def human_b():
    reward_locs = {3: 15, 5: 30}
    edges = [[1, 2], [3, 4], [4, 5], [3, 3], [4, 4], [5, 5]]
    objects = {'rewards': reward_locs}
    return objects, edges


def t_loop():
    reward_locs = {12: 1, 11: 1}
    edges = [
        [1, 0],
        [2, 1],
        [3, 4],
        [5, 3],
        [6, 4],
        [7, 5],
        [8, 6],
        [9, 7],
        [10, 8],
        [11, 9],
        [12, 10],
        [0, 11],
        [0, 12],
    ]
    objects = {'rewards': reward_locs}
    return objects, edges


def variable_magnitude():
    # Values taken from original author's code availabe here: https://osf.io/ux5rg/
    fmax = 10.0
    sigma = 200
    utility_func = lambda r: (fmax * np.sign(r) * np.abs(r) ** (0.5)) / (
        np.abs(r) ** (0.5) + sigma ** (0.5)
    )
    reward_locs = {
        1: utility_func(0.1),
        2: utility_func(0.3),
        3: utility_func(1.2),
        4: utility_func(2.5),
        5: utility_func(5),
        6: utility_func(10),
        7: utility_func(20),
    }
    edges = [
        [((1, 2, 3, 4, 5, 6, 7), (0.067, 0.090, 0.148, 0.154, 0.313, 0.151, 0.077))],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    ]
    objects = {'rewards': reward_locs}
    return objects, edges


structure_map = {
    GraphStructure.two_step: two_step,
    GraphStructure.two_way_linear: two_way_linear,
    GraphStructure.ring: ring,
    GraphStructure.linear: linear,
    GraphStructure.t_graph: t_graph,
    GraphStructure.neighborhood: neighborhood,
    GraphStructure.human_a: human_a,
    GraphStructure.human_b: human_b,
    GraphStructure.t_loop: t_loop,
    GraphStructure.variable_magnitude: variable_magnitude,
    GraphStructure.three_arm_bandit: three_arm_bandit,
}
