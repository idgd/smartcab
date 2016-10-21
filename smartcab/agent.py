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
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # Initialize any additional variables here
        self.actions = [None,'forward','left','right']
        self.gamma = 0.1
        self.alpha = 0.1
        self.edivir = 1.1
        self.previous_state = None

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # Prepare for a new trip; reset any variables here, if required
        self.num_runs += 1

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
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

        # Select action according to your policy

        # update qtable with qfunction
        self.previous_state = update_state()
        action = random.choice(self.actions)
        reward = self.env.act(self,action)
        self.state = update_state()

        maxq = max([self.qtable[self.state, f] for f in self.actions])

        self.qtable[self.previous_state,action] = self.qtable[self.state,action] + self.alpha * (reward + self.gamma * maxq - self.qtable[self.previous_state,action])

        # for f in self.actions:
        #     uncomment to see qvalues
        #     if self.qtable[self.state,f] == 0.0:
        #        q_action.append(self.qtable[self.state,f])
        #        print ["Undefined Qvalue", self.qtable[self.state,f]]
        #     elif self.qtable[self.state,f] > 0.0:
        #        q_action.append(self.qtable[self.state,f])
        #        print ["Proper Qvalue action", self.qtable[self.state,f]]
        #     else:
        #        q_action.append(self.qtable[self.state,f])
        #        print ["Negative Qvalue", self.qtable[self.state,f]]

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

        # random choice
        # action = random.choice(self.actions)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # report successes past the deadline if enforce_deadline = False
        # if self.env.done and deadline < 0:
        #    print 'Soft Success'

        # report successes before the deadline
        if self.env.done and deadline > 0:
           print 'Hard Success'

        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.00001, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
