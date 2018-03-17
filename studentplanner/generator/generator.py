import math
import random
from copy import deepcopy
from typing import Dict, Set, Tuple, List, Optional

import datetime

from schedules.models import TimeTable, Group


class TimeTableGroupsMap:
    LECTURER_PENALTY = 2.0
    PERIOD_PENALTY = 5.0
    GAP_PENALTY = 1.0

    def __init__(self, courses, loved_l, hated_l, hated_p):
        self.mapping = list()
        self.solution = list()
        self.length = 0
        self.loved_lecturers = loved_l
        self.hated_lecturers = hated_l
        self.hated_periods = hated_p
        self._cost = None

        class_types = [t[0] for t in Group.TYPE_CHOICES]

        for course in courses:
            course_groups = course.groups.distinct()
            for t in class_types:
                groups = course_groups.filter(type__iexact=t)
                if groups.exists():
                    self.solution.append(list())
                    self.mapping.append(list())
                    group_codes_set = {g.code for g in groups}
                    for code in group_codes_set:
                        self.solution[self.length].append(False)
                        self.mapping[self.length].append(list(groups.filter(code=code)))
                    self.length += 1

        if self.length > 0:
            self.random_solution()

    def random_solution(self):
        for i, _ in enumerate(self.solution):
            if len(self.solution[i]) > 1:
                rand_index = random.randint(0, len(self.solution[i]) - 1)
                self.solution[i][rand_index] = True
            elif len(self.solution[i]) == 1:
                self.solution[i][0] = True

    def selected_groups(self):
        for i, groups in enumerate(self.mapping):
            for j, group in enumerate(groups):
                if self.solution[i][j]:
                    for g in group:
                        yield g

    @classmethod
    def crossover(cls, parent1: 'TimeTableGroupsMap', parent2: 'TimeTableGroupsMap') -> 'TimeTableGroupsMap':
        assert parent1.mapping == parent2.mapping, "Mappings don't match, " \
                                                   "both TimeTableGroupMaps have to have the same " \
                                                   "underlying mapping for crossover"

        child = deepcopy(parent1)

        if len(parent1) > 3:
            x = random.randint(0, len(parent1) - 2)
            y = random.randint(x + 1, len(parent1) - 1)

            child.solution[x:y] = deepcopy(parent2.solution[x:y])
        else:
            x = random.randint(0, len(parent1) - 1)
            child.solution[x] = deepcopy(parent2.solution[x])

        return child

    def mutate(self, probability=0.05):
        for i, groups in enumerate(self.solution):
            length = len(groups)
            if probability > random.uniform(0, 1) and length > 1:
                x = random.randint(0, len(groups) - 1)
                y = random.randint(0, len(groups) - 1)
                self.solution[i][y], self.solution[i][x] = self.solution[i][x], self.solution[i][y]

    def is_valid(self):
        periods = {
            weekday: set() for weekday in range(0, 5)
        }
        periods_even = {
            weekday: set() for weekday in range(0, 5)
        }
        periods_odd = {
            weekday: set() for weekday in range(0, 5)
        }
        for group in self.selected_groups():
            wd = group.day
            s = group.start_time
            e = group.end_time
            if group.week_type == Group.NORMAL:
                for period in periods[wd]:
                    if period[0] <= s <= period[1] or period[0] <= e <= period[1]:
                        return False
            if group.week_type == Group.EVEN:
                for period in periods[wd]:
                    if period in periods_odd and period not in periods_even:
                        continue
                    if period[0] <= s <= period[1] or period[0] <= e <= period[1]:
                        return False
                periods_even[wd].add((s, e))
            if group.week_type == Group.ODD:
                for period in periods[wd]:
                    if period in periods_even and period not in periods_odd:
                        continue
                    if period[0] <= s <= period[1] or period[0] <= e <= period[1]:
                        return False
                periods_odd[wd].add((s, e))
            periods[wd].add((s, e))

        for wd, day_periods in periods.items():
            for period in day_periods.copy():
                if period in periods_even[wd] or period in periods_odd[wd]:
                    if period in periods_even[wd] and period in periods_odd[wd]:
                        continue
                    else:
                        periods[wd].remove(period)
        self._set_cost(periods)
        return True

    @property
    def cost(self):
        return self._cost

    def _set_cost(self, periods: Dict[int, Set]) -> None:
        self._cost = 0.0
        dummy_date = datetime.date.today()
        for wd, day_periods in periods.items():
            sorted_periods = sorted(day_periods, key=lambda x: x[0])
            for i, period in enumerate(sorted_periods[:-1]):
                last_end = datetime.datetime.combine(dummy_date, period[1])
                next_start = datetime.datetime.combine(dummy_date, sorted_periods[i+1][0])
                gap_delta: datetime.timedelta = next_start - last_end
                if gap_delta > datetime.timedelta(minutes=45):
                    gaps = math.ceil((gap_delta.total_seconds()/60)/60)
                    for h_period in self.hated_periods[wd]:
                        if last_end.time() <= h_period[0] and h_period[1] <= next_start.time():
                            gaps -= 0.5
                    self._cost += self.GAP_PENALTY * gaps
        for group in self.selected_groups():
            wd = group.day
            s = group.start_time
            e = group.end_time
            for h_period in self.hated_periods[wd]:
                if h_period[0] <= s <= h_period[1] or h_period[0] <= e <= h_period[1]:
                    self._cost += self.PERIOD_PENALTY
            if group.lecturer in self.loved_lecturers:
                self._cost -= self.LECTURER_PENALTY
            elif group.lecturer in self.hated_lecturers:
                self._cost += self.LECTURER_PENALTY * 1.5

    def is_better_than(self, other):
        return self._cost < other.cost

    def __len__(self):
        return self.length


class Generator:
    POP_SIZE = 30
    MAX_RETRIES = 10
    PRETENDERS_NUM = 3
    MAX_GENERATIONS = 100
    MUTATION_PROBABILITY = 0.02

    def __init__(self, student, courses=None, loved_lecturers=None, hated_lecturers=None, hated_periods=None):
        self.student = student
        self.courses = courses
        self.loved_lecturers = loved_lecturers
        self.hated_lecturers = hated_lecturers
        self.hated_periods = hated_periods
        self.population = list()

    def random_population(self) -> None:
        assert len(self.population) == 0
        for i in range(0, self.POP_SIZE):
            tries = 0
            valid = False
            while not valid:
                tries += 1
                if tries > self.MAX_RETRIES:
                    break
                else:
                    groups_map = TimeTableGroupsMap(self.courses, self.loved_lecturers, self.hated_lecturers, self.hated_periods)
                    valid = groups_map.is_valid()
            if valid:
                self.population.append(groups_map)
        self.POP_SIZE = len(self.population)

    def get_population_best(self) -> Tuple[List[Group], float]:
        best_cost: float = float('inf')
        best: int = 0
        for i, groups_map in enumerate(self.population):
            c = groups_map.cost
            if c < best_cost:
                best_cost = c
                best = i
        return list(self.population[best].selected_groups()), best_cost

    def generate(self) -> Optional[TimeTable]:

        def parent_selection(size: int) -> int:
            size = min(self.POP_SIZE, size)
            b_cost, b_index = float('inf'), 0
            for x in random.sample(range(0, self.POP_SIZE), size):
                c = self.population[x].cost
                if c < b_cost:
                    b_cost, b_index = c, x
            return b_index

        self.random_population()

        if not self.population:
            return None

        the_best_groups, the_best_cost = self.get_population_best()

        stagnation = 0

        for generation in range(0, self.MAX_GENERATIONS):
            new_population = list()
            for _ in range(0, self.POP_SIZE):
                tries = 0
                valid = False
                while not valid:
                    tries += 1
                    if tries > self.MAX_RETRIES:
                        break
                    else:
                        i: int = parent_selection(self.PRETENDERS_NUM)
                        j: int = parent_selection(self.PRETENDERS_NUM)
                        offspring = TimeTableGroupsMap.crossover(self.population[i], self.population[j])
                        offspring.mutate(probability=self.MUTATION_PROBABILITY)
                        valid = offspring.is_valid()
                if not valid:
                    new_population.append(
                        self.population[i]
                        if self.population[i].is_better_than(self.population[j])
                        else self.population[j])
                else:
                    new_population.append(offspring)

            self.population = list(new_population)
            best_groups, best_cost = self.get_population_best()

            if best_cost <= the_best_cost:
                the_best_groups = best_groups
                the_best_cost = best_cost

            if best_cost < the_best_cost:
                stagnation = 0
            else:
                stagnation += 1
                if stagnation > int(math.ceil(self.MAX_GENERATIONS / 10)):
                    break

        time_table = TimeTable(field_of_study=self.student.field_of_study)
        time_table.save()
        time_table.groups.add(*the_best_groups)
        time_table.save()

        return time_table
