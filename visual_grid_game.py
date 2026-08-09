# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        # IT24103447 - added current facing direction for local perception
        self.facing_direction = 'Right'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        # IT24103447 - changed percept to provide only local boolean information
        x, y = self.agent_pos
        ahead_x = x
        ahead_y = y

        if self.facing_direction == 'Up':
            ahead_y += 1
        elif self.facing_direction == 'Down':
            ahead_y -= 1
        elif self.facing_direction == 'Left':
            ahead_x -= 1
        elif self.facing_direction == 'Right':
            ahead_x += 1

        # IT24103447 - wall_ahead is True if the adjacent cell is a wall
        wall_ahead = (
            ahead_x < 0
            or ahead_x >= self.width
            or ahead_y < 0
            or ahead_y >= self.height
            or (ahead_x, ahead_y) in self.walls
        )

        # IT24103447 - food_here is True only when food is at the agent's current location
        food_here = tuple(self.agent_pos) in self.food_positions

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here,
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }



    def execute_action(self, action: str):
        self.steps += 1

        # IT24103447 - update facing direction based on the action
        self.facing_direction = action

        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

# IT24103447 - Simple Reflex Agent
class SimpleReflexAgent:

    def sense_and_act(self, percept):
        if percept['food_here']:
            return 'Right'

        if percept['wall_ahead']:
            return 'Up'

        return 'Right'

# IT24103447 - Model-Based Agent
class ModelBasedAgent:

    def __init__(self):
        self.model_x = 0
        self.model_y = 0
        # IT24103447 - Store cells that the agent has already visited.
        self.visited_cells = set()
        # IT24103447 - Remember the previous action taken by the agent.
        self.last_action = None

    def sense_and_act(self, percept):

        current_cell = (self.model_x, self.model_y)

        # IT24103447 - Add the current cell to memory so the agent knows that it has already visited this location.
        self.visited_cells.add(current_cell)

        if percept['food_here']:
            action = 'Right'
        elif percept['wall_ahead']:
            if self.last_action == 'Right':
                action = 'Up'
            elif self.last_action == 'Up':
                action = 'Left'
            elif self.last_action == 'Left':
                action = 'Down'
            else:
                action = 'Right'
        else:
            # IT24103447 - When there is no wall ahead, the default behaviour is to continue moving Right.
            action = 'Right'
            # IT24103447 - Check whether the cell to the Right has already been visited.
            if (self.model_x + 1, self.model_y) in self.visited_cells:
                if (self.model_x, self.model_y + 1) not in self.visited_cells:
                    action = 'Up'
                elif (self.model_x - 1, self.model_y) not in self.visited_cells:
                    action = 'Left'
                elif (self.model_x, self.model_y - 1) not in self.visited_cells:
                    action = 'Down'

        if action == 'Right':
            self.model_x += 1

        elif action == 'Left':
            self.model_x -= 1

        elif action == 'Up':
            self.model_y += 1

        elif action == 'Down':
            self.model_y -= 1

        # IT24103447 - Store the selected action so it can be used as part of the decision-making process during the next step.
        self.last_action = action
        return action

class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        # IT24103447 - create Simple Reflex Agent
        #agent = SimpleReflexAgent()

        # IT24103447 - Step 1.3: create Model-Based Agent
        agent = ModelBasedAgent()

        def step():
            if not self.env.is_done():
                # IT24103447 - get local percept
                percept = self.env.get_percept()
                action = agent.sense_and_act(percept)

                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()