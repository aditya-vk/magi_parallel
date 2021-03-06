
######################################
# Need to empty unnecessary functions and add parallel processes at the root node 
# for visualization
######################################


# import logging
from abc import abstractmethod
# from actions.base import ActionError
# from actions.base import CheckpointError
# from actions.Sequence import SequenceAction, SequenceSolution
# from actions.Parallel import ParallelAction
# from contextlib import contextmanager
# from Queue import Queue
import multiprocessing
import time


# logger = logging.getLogger(__name__)

# class TimeoutException(Exception):
#     pass

# @contextmanager
# def TimeLimit(seconds):
#     # http://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call-in-python
#     def signal_handler(signum, frame):
#         raise TimeoutException('Failed to complete task before timeout')
#     import signal
#     signal.signal(signal.SIGALRM, signal_handler)
#     signal.alarm(seconds)
#     try:
#         yield
#     finally:
#         signal.alarm(0)

class Planner(object):
    def plan_timed(self, env, action, timeout=30, output_queue=None):
        """
        Plan for a user specified amount of time
        Raises TimeoutException if timelimit is encountered
        @param env The OpenRAVE environment to plan in
        @param action The Action to plan
        @param timeout planning time limit in seconds
        @param output_queue Queue object that is updated with Solutions as they
                            become available
        @return A Solution
        """
        with TimeLimit(timeout):
            return self.plan_action(env, action, output_queue=output_queue)

    @abstractmethod
    def plan_action(self, env, action, output_queue=None):
        """
        Generate and return a solution for an action of type SequenceAction
        @param env The OpenRAVE environment to plan in
        @param action The Action to plan
        @return A Solution
        """
        pass

def _build_tree(action, G, node_map, parent_nodes=[]):
    import networkx as nx
    G = nx.read_gpickle("G.gpickle")
    for n in G.nodes():
        node_map[str(n)] = None

# def _build_tree(action, G, node_map, parent_nodes=[]):
#     """
#     Recursively expand a Sequence action
#     @parent action The action to expand
#     @param G The tree
#     @param node_map A map from node names in the tree to action objects
#     @param parent_nodes The parents for this action
#     """
#     if isinstance(action, SequenceAction):
#         for a in action.actions:
#             parent_nodes = _build_tree(a, G, node_map, parent_nodes=parent_nodes)
#         return parent_nodes

#     elif isinstance(action, ParallelAction):
#         parallel_actions = []
#         for a in action.actions:
#             parallel_actions += _build_tree(a, G, node_map, parent_nodes=parent_nodes)
#         return parallel_actions 

#     else:
#         aname = action.get_name()
#         node_name = '%s-%d' % (aname, len(G.nodes()))
#         node_map[node_name] = action

#         G.add_node(node_name)
#         for p in parent_nodes:
#             G.add_edge(p, node_name)
#         return [ node_name ]



class ParallelPlanner(Planner):

    def __init__(self, max_action_attempts=5, monitor=None, use_frustration=False, keep_trying=True):
        """
        @param max_action_attempts The max times to attempt to plan an action
          at any  particular visit to a node
        @param monitor The monitor to register planning progress to
        @param use_frustration Use frustration style backtracking instead of a pure DFS
        @param keep_trying Continue to restart until success or timeout (if used)
        """
        self.num_attempts = max_action_attempts
        self.monitor = monitor
        self.G = None
        self.node_map = dict()
        self.use_frustration = use_frustration
        self.keep_trying = keep_trying
        
        # Internal value that marks if we are currently in a frustrated state to
        # avoid unnecessary computation
        self.frustrated = False     

    def __str__(self):
         if self.use_frustration:
             return 'frustration'
         else:
             return 'parallel'

    def plan_action(self, env, action, output_queue=None):
        # """
        # @param env The environment to plan in
        # @param action The starting HGPC action to plan from
        # @param output_queue A queue of solutions to put out when a checkpoint is reached
        # """
        import networkx as nx
        self.G = nx.DiGraph(format='svg')
        _build_tree(action, self.G, self.node_map)
        print self.node_map

        if self.monitor is not None:
            self.monitor.set_graph(self.G, self.node_map)

        # self.output_queue = output_queue
        
        # if self.output_queue is not None:
        #     # If the user wants an output queue as we go, setup an action and solution stack
        #     self.output_actions = []
        #     self.output_solutions = []
        
        # if self.use_frustration:
        #     # Initialize a data structure to track whether or not a 
        #     #  particular node of the graph has been expanded and failed all m times
        #     self.failure_map = { n: 0 for n in self.G.nodes() }

        # # Now get the roots of the tree and plan
        # roots = [ n for n in self.G.nodes() if self.G.in_degree(n) == 0 ]
        
        # # If we want to keep trying, repeat until finished or the timelimit kills us
        # if self.keep_trying:
        #     while True:
        #         try:
        #             solutions = self._plan_recursive(env, roots, self.num_attempts)
        #             break
        #         except CheckpointError:
        #             raise
        #         except ActionError as e:
        #             logger.warning('All planning failed, but time remains so trying again.')  
                    
        #             # Reset internal variables  
        #             if self.use_frustration:
        #                 # Re-Initialize a data structure to track whether or not a 
        #                 #  particular node of the graph has been expanded and failed all m times
        #                 self.failure_map = { n: 0 for n in self.G.nodes() }                  
        # else:
        #     solutions = self._plan_recursive(env, roots, self.num_attempts)

        # return SequenceSolution(
        #     action=action,
        #     solutions=solutions)
    
    # def _plan_recursive(self, env, node_ids, num_attempts):
        # monitor = self.monitor

        # # If this was called on a leaf node, we are all done
        # if not node_ids:
        #     if monitor is not None:
        #         monitor.set_planning_action(None)
                
        #     # If we were prepping an output queue, send it out
        #     if self.output_queue is not None:    
        #         if self.output_actions:
        #             self.output_queue.put(
        #               SequenceSolution(SequenceAction(self.output_actions),self.output_solutions))
        #             self.output_actions=[]
        #             self.output_solutions=[]
        #     return []

        # # TODO: Eventually we want to spin off threads with environment clones
        # #  For now, just randomly pick a branch to walk down
        # import numpy as np
        # node_order = np.random.permutation(len(node_ids))

        # deterministic=True
        # for n in node_order[0:max(num_attempts, len(node_ids))]:
        #     node_id = node_ids[n]
        #     action = self.node_map[node_id]
            
        #     # The number of attempts may change as we go if our frustration changes
        #     i = 0
        #     while i < num_attempts:
        #         i = i + 1
                
        #         solution = None

        #         try:
        #             logger.info("Planning for action %s", action.get_name())
        #             if action.checkpoint:
        #                 logger.info("This action is a checkpoint: %s", action.get_name())
                    
        #             if monitor is not None:
        #                 monitor.set_planning_action(action)
        #             solution = action.plan(env)
        #             deterministic = deterministic and solution.deterministic

        #             # mark the action as being successfully planned
        #             if monitor is not None:
        #                 monitor.update(action, True, solution.deterministic)
                
        #             # If we have succeeded and the user wants an output queue, add the solution
        #             if self.output_queue is not None:    
        #                 self.output_actions.append(action)
        #                 self.output_solutions.append(solution)
                    
        #                 # If this action is a checkpoint, push out the accumulated solutions
        #                 if action.checkpoint:
        #                     self.output_queue.put(
        #                         SequenceSolution(SequenceAction(self.output_actions),self.output_solutions))
        #                     self.output_actions=[]
        #                     self.output_solutions=[]

        #             # Log an info message on successful plan 
        #             if self.use_frustration:
        #                 logger.info('Attempt %d of %d (frustration %d) for action %s: Planning Succeeded.',
        #                             i, num_attempts, self.failure_map[node_id], action.get_name())
        #             else:
        #                 logger.info('Attempt %d of %d for action %s: Planning Succeeded.',
        #                             i, num_attempts, action.get_name())
                    
        #         except ActionError as e:
        #             # Log an warning on unsuccessful plan and if using frustration, update those variables
        #             if self.use_frustration:
        #                 logger.warning('Attempt %d of %d (frustration %d) for action %s: Planning failed: %s',
        #                                i, num_attempts, self.failure_map[node_id], action.get_name(), str(e))
                        
        #                 # Update the failure map
        #                 self.failure_map[node_id] += 1
        #                 self.frustrated = True
        #             else:
        #                 logger.warning('Attempt %d of %d for action %s: Planning failed: %s',
        #                                i, num_attempts, action.get_name(), str(e))

        #             deterministic = deterministic and e.deterministic

        #             # mark the action as being failed
        #             if monitor is not None:
        #                 monitor.update(action, False, e.deterministic)

        #             if e.deterministic:
        #                 # No need to retry planning
        #                 i = num_attempts

        #         if solution is not None:
        #             # Recursively find solutions to the remaining actions.
        #             with solution.save_and_jump(env):
        #                 checkpoint_keep_trying = True
        #                 while checkpoint_keep_trying:
        #                     checkpoint_keep_trying = False
        #                     try:
        #                         # For the child nodes, set the num_attempts based on the frustration level
        #                         if self.use_frustration:
        #                             # If we successfully planned the first time on this node, we must have
        #                             # made it around the frustrating part. Reset frustration map
        #                             if self.frustrated and self.failure_map[node_id] == 0:
        #                                 logger.info("Planning a new node after frustration! Resetting failure map.")
        #                                 self.failure_map = { n: 0 for n in self.G.nodes() }
        #                                 self.frustrated = False
                                
        #                             # Calculate the number of attempts to try
        #                             next_num_attempts = max(1, self.num_attempts - self.failure_map[node_id])
        #                         else:
        #                             next_num_attempts = num_attempts

        #                         successor_actions = [ n for n in self.G.successors(node_id) ]
        #                         next_solutions = self._plan_recursive(env, successor_actions, next_num_attempts)
        #                         return [solution] + next_solutions
        #                     except CheckpointError as e:
        #                         # If we get a checkpoint error, just keep passing it up the chain
        #                         raise
        #                     except ActionError as e:
        #                         if action.checkpoint and self.output_queue is not None:
        #                             if self.keep_trying:
        #                                 # If we were asked to keep going, we keep going...
        #                                 checkpoint_keep_trying = True
        #                                 if self.use_frustration:
        #                                     self.failure_map[node_id]=0
                                            
        #                                 logger.warning("Failed to plan after checkpoint, but continuing to try until timeout.")
        #                             else:
        #                                 # If this is a checkpoint we cant backtrack past here
        #                                 raise CheckpointError(
        #                                     'Planning failed after checkpoint %s.'.format(action.get_name()))
        #                         else:
        #                             # If we need to backtrack, pop off this action and solution from the stack
        #                             if self.output_queue is not None and len(self.output_actions) >0: 
        #                                 self.output_actions.pop()
        #                                 self.output_solutions.pop()

        #                             if self.use_frustration:
        #                                 # Even if the children failed, if they made more progress
        #                                 # our frustration will have been reset.
        #                                 if self.failure_map[node_id] is 0:
        #                                     num_attempts = self.num_attempts
                                  
        #                                 # Update the failure map
        #                                 self.failure_map[node_id] += 1
        #                                 self.frustrated = True

        #                             if solution.deterministic:
        #                                 # No reason to retry this action
        #                                 i = num_attempts

        # # Log a warning that we have exhausted all our children
        # if self.use_frustration:
        #     logger.warning('Attempt %d of %d (frustration %d) for action %s: Planning of children failed',
        #            i, num_attempts, self.failure_map[node_id], action.get_name())

        # else:
        #     logger.warning('Attempt %d of %d for action %s: Planning of children failed',
        #            i, num_attempts, action.get_name())    

        # raise ActionError(
        #     'Planning failed in all {:d} attempts for action %s.'.format(num_attempts, action.get_name()),
        #     deterministic=deterministic)
