# agent.py
# IT24103447 - Lab03 - Step 1.2 - imported data structures required for BFS, DFS and UCS
from collections import deque
import heapq

# IT24103447 - Lab04 - Step 1.1 - imported math for Euclidean distance
import math

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


# IT24103447 - Lab03 - Step 1.2 - added SearchAgent for uninformed search
class SearchAgent:

    # IT24103447 - Lab03 - Step 1.3 - added plan and active search algorithm
    def __init__(self):
        self.plan = []
        self.active_algo = 'UCS'

        # IT24103447 - Lab03 - Step 1.3 - stores the current agent position
        self.current_pos = (0, 0)

    # IT24103447 - Lab03 - Step 1.2 - returns valid neighbouring cells and their actions
    def get_successors(self, position, walls, grid_size):

        x, y = position
        width, height = grid_size

        possible_moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        successors = []

        for action, next_position in possible_moves:

            next_x, next_y = next_position

            if (
                0 <= next_x < width
                and 0 <= next_y < height
                and next_position not in walls
            ):
                successors.append((action, next_position))

        return successors


    # IT24103447 - Lab03 - Step 1.2 - implemented BFS using a FIFO queue
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = deque()
        frontier.append((start_pos, []))

        reached = {start_pos}

        while frontier:

            current_pos, path = frontier.popleft()

            if current_pos == goal_pos:
                return path

            for action, next_pos in self.get_successors(
                current_pos, walls, grid_size
            ):

                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append(
                        (next_pos, path + [action])
                    )

        return None


    # IT24103447 - Lab03 - Step 1.2 - implemented DFS using a LIFO stack
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = [(start_pos, [])]

        reached = {start_pos}

        while frontier:

            current_pos, path = frontier.pop()

            if current_pos == goal_pos:
                return path

            for action, next_pos in self.get_successors(
                current_pos, walls, grid_size
            ):

                if next_pos not in reached:

                    reached.add(next_pos)

                    frontier.append(
                        (next_pos, path + [action])
                    )

        return None


    # IT24103447 - Lab03 - Step 1.2 - implemented UCS using a priority queue
    def ucs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = []
        heapq.heappush(frontier, (0, start_pos, []))

        reached = set()

        while frontier:

            cost, current_pos, path = heapq.heappop(frontier)

            if current_pos in reached:
                continue

            reached.add(current_pos)

            if current_pos == goal_pos:
                return path

            for action, next_pos in self.get_successors(
                current_pos, walls, grid_size
            ):

                if next_pos not in reached:

                    heapq.heappush(
                        frontier,
                        (cost + 1, next_pos, path + [action])
                    )

        return None

    # IT24103447 - Lab03 - Step 1.3 - creates and executes an offline plan
    def sense_and_act(self, percept):

        # IT24103447 - Lab03 - Step 1.3 - create a new plan when the current plan is empty
        if not self.plan:

            all_food = percept['all_food']
            walls = percept['walls']
            grid_size = percept['grid_size']

            if not all_food:
                return None

            # IT24103447 - Lab03 - Step 1.3 - find the closest food pellet
            closest_food = min(
                all_food,
                key=lambda food:
                    abs(food[0] - self.current_pos[0])
                    + abs(food[1] - self.current_pos[1])
            )

            # IT24103447 - Lab03 - Step 1.3 - create the plan using the selected algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(
                    self.current_pos,
                    closest_food,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(
                    self.current_pos,
                    closest_food,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(
                    self.current_pos,
                    closest_food,
                    walls,
                    grid_size
                )

            # IT24103447 - Lab04 - Step 1.3 - added A* to the agent decision loop
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    self.current_pos,
                    closest_food,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )

            if self.plan is None:
                self.plan = []

        if not self.plan:
            return None

        # IT24103447 - Lab03 - Step 1.3 - execute the first action from the stored plan
        action = self.plan.pop(0)


        # IT24103447 - Lab03 - Step 1.3 - update the stored position after the action
        x, y = self.current_pos

        if action == 'Up':
            y += 1
        elif action == 'Down':
            y -= 1
        elif action == 'Left':
            x -= 1
        elif action == 'Right':
            x += 1

        self.current_pos = (x, y)

        return action

    # IT24103447 - Lab04 - Step 1.1 - added Manhattan distance heuristic
    def manhattan_distance(self, pos, goal):

        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


    # IT24103447 - Lab04 - Step 1.1 - added Euclidean distance heuristic
    def euclidean_distance(self, pos, goal):

        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            + (pos[1] - goal[1]) ** 2
        )


    # IT24103447 - Lab04 - Step 1.2 - implemented A* Search using path cost and heuristic cost
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        # IT24103447 - Lab04 - Step 1.2 - created priority queue and reached states
        frontier = []
        reached_states = set()

        # IT24103447 - Lab04 - Step 1.2 - calculate heuristic value for the starting position
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        g_cost = 0
        f_cost = g_cost + h_cost

        # IT24103447 - Lab04 - Step 1.2 - added starting state to the priority queue
        heapq.heappush(
            frontier,
            (f_cost, g_cost, start_pos, [])
        )

        while frontier:

            # IT24103447 - Lab04 - Step 1.2 - remove the state with the lowest f cost
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # IT24103447 - Lab04 - Step 1.2 - expand valid neighbouring states
            for action, next_pos in self.get_successors(
                current_pos,
                walls,
                grid_size
            ):

                if next_pos not in reached_states:

                    new_g_cost = g_cost + 1

                    # IT24103447 - Lab04 - Step 1.2 - calculate heuristic cost for the neighbour
                    if heuristic_type == 'euclidean':
                        new_h_cost = self.euclidean_distance(
                            next_pos,
                            goal_pos
                        )
                    else:
                        new_h_cost = self.manhattan_distance(
                            next_pos,
                            goal_pos
                        )

                    new_f_cost = new_g_cost + new_h_cost

                    # IT24103447 - Lab04 - Step 1.2 - add neighbour according to its f cost
                    heapq.heappush(
                        frontier,
                        (
                            new_f_cost,
                            new_g_cost,
                            next_pos,
                            path_taken + [action]
                        )
                    )

        return None    

# IT24103447 - Lab04 - Step 1.1 - testing heuristic functions
if __name__ == "__main__":

    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)

    print("Manhattan Distance:", agent.manhattan_distance(start, goal))
    print("Euclidean Distance:", agent.euclidean_distance(start, goal))