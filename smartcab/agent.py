import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

def make_qtable():
    qtable = {}
    actions = [None,'forward','left','right']
    truncated_actions = ['forward','left','right']
    light = ['red','green']
    for a in light:
        for b in actions:
            for c in actions:
                for d in truncated_actions:
                    for e in actions:
                        qtable[((d, a, b, c), e)] = 0
    return qtable

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
    num_runs = 0
    qtable = make_qtable()

    def __init__(self, env):
        super(LearningAgent, self).__init__(env) # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red' # override color
        self.planner = RoutePlanner(self.env, self) # simple route planner to get next_waypoint

        self.actions = [None,'forward','left','right']
        self.gamma = 0.1
        self.alpha = 0.1
        self.edivir = 1.1
        self.previous_state = None

    def reset(self, destination=None):
        self.planner.route_to(destination)

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

        # update qtable with qfunction
        self.previous_state = update_state()
        action = random.choice(self.actions)
        reward = self.env.act(self,action)
        self.state = update_state()
        maxq = max([self.qtable[self.state, f] for f in self.actions])
        # qfunction
        self.qtable[self.previous_state,action] = self.qtable[self.state,action] + self.alpha * (reward + self.gamma * maxq - self.qtable[self.previous_state,action])

        # get list of qvalues for possible actions
        q_actions = [self.qtable[self.previous_state, f] for f in self.actions]

        # always start random
        if self.num_runs == 0:
           action = random.choice(self.actions)
        # from then on random choice between random and best qvalue transition
        elif self.num_runs != 0:
           epsilon = 1/pow(self.num_runs,1/self.edivir)
           if random.random() < epsilon:
              action = random.choice(self.actions)
           else:
              action = self.actions[q_actions.index(max(q_actions))]

        # Execute action and get reward
        reward = self.env.act(self, action)

        # report successes
        if self.env.done and deadline > 0:
           print 'Success'

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.00001, display=False)  # create simulator

    sim.run(n_trials=100)  # run for a specified number of trials

if __name__ == '__main__':
    run()
