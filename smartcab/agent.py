import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

# qtable with default values of 0 creation function 
def make_qtable():
    qtable = {}
    actions = [None, 'forward', 'left', 'right']
    light = ['red', 'green']
    for a in light:
        for b in actions:
            for c in actions:
                for d in actions[-3:]:
                    for e in actions:
                        qtable[((d, a, b, c), e)] = 0
    return qtable

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
    # number of runs for epsilon, and qtable for the qlearner itself
    num_runs = 0
    qtable = make_qtable()

    def __init__(self, env):
        super(LearningAgent, self).__init__(env) # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red' # override color
        self.planner = RoutePlanner(self.env, self) # simple route planner to get next_waypoint

        self.actions = [None, 'forward', 'left', 'right']
        self.alpha = 0.4
        self.gamma = 0.2
        self.edivir = 1.1
        self.previous_state = None

    def reset(self, destination=None):
        self.planner.route_to(destination)

        # increment number of runs every time it resets
        self.num_runs += 1

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        def update_state():
            state = (self.planner.next_waypoint(),
                     self.env.sense(self)['light'],
                     self.env.sense(self)['oncoming'],
                     self.env.sense(self)['left'])
            return state

        self.state = update_state()
        self.previous_state = update_state()
        
        # perfect actor
        if self.env.sense(self)['light'] == 'green':
           if self.planner.next_waypoint() == 'forward':
              paction = self.planner.next_waypoint()
           elif self.planner.next_waypoint() == 'left':
              if self.env.sense(self)['oncoming'] != 'right' and self.env.sense(self)['oncoming'] != 'forward':
                 paction = self.planner.next_waypoint()
              else:
                 paction = None
           else:
              paction = self.planner.next_waypoint()
        elif self.env.sense(self)['light'] == 'red':
           if self.planner.next_waypoint() == 'forward':
              paction = None
           elif self.planner.next_waypoint() == 'right':
              if self.env.sense(self)['left'] != 'forward':
                 paction = self.planner.next_waypoint()
              else:
                 paction = None
           else:
              paction = None
        else:
           paction = self.planner.next_waypoint()

        # qlearner
        if self.num_runs == 0:
           action = random.choice(self.actions)
        else:
           epsilon = 1/pow(self.num_runs, 1/self.edivir)
           if random.random() < epsilon:
              action = random.choice(self.actions)
           else:
              q_actions = [self.qtable[self.previous_state, f] for f in self.actions]
              action = self.actions[q_actions.index(max(q_actions))]
           
        reward = self.env.act(self, action)
        self.state = update_state()
        maxq = max([self.qtable[self.state, f] for f in self.actions])
        self.qtable[self.previous_state, action] = (1 - self.alpha) * self.qtable[self.previous_state, action] + self.alpha * (reward + self.gamma * maxq)

        # check qlearner's path against perfect path in the last 10 runs
        if self.num_runs >= 90:
           if paction != action:
              print "q.act"
           else:
              print "p.act"

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.0000001, display=False)  # create simulator:

    sim.run(n_trials=100)  # run for a specified number of trials

if __name__ == '__main__':
    run()
