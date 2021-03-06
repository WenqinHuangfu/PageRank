"""
This class implements the simple pagerank algorithm
as described in the first part of the project.
"""
class SimplePageRank(object):

    """
    Keeps track of the rdd used as the input data. 
    This should be a list of lines similar to the example input files.
    You do not need to change this method, but feel free to do so to suit your needs. 
    However, the signature MUST stay the same.
    """
    def __init__(self, input_rdd):
        self.input_rdd = input_rdd

    """
    Computes the pagerank algorithm for num_iters number of iterations.
    You do not need to change this method, but feel free to do so to suit your needs. 
    However, the signature MUST stay the same.
    The output should be a rdd of (pagerank score, node label) pairs, 
    sorted by pagerank score in descending order.
    """
    def compute_pagerank(self, num_iters):
        nodes = self.initialize_nodes(self.input_rdd)
        num_nodes = nodes.count()
        print num_nodes
        for i in range(0, num_iters):
            nodes = self.update_weights(nodes, num_nodes)
        return self.format_output(nodes)

    """
    Converts the input_rdd to a rdd suitable for iteration with
    the pagerank update algorithm.
    The rdd nodes should be enough to calculate the next iteration
    of the pagerank update algorithm by itself, without using any
    external structures.
    That means that all the edges must be stored somewhere,
    as well as the current weights of each node.
    You do not need to change this method, but feel free to do so to suit your needs.
    In the default implemention, the rdd is simply a collection of (node label, (current weight, target)) tuples.
    Lines in the input_rdd file will either be blank or begin with "#", which
    should be ignored, or be of the form "source[whitespace]target" where source and target
    are labels for nodes that are integers. 
    For example, the line:
    1    3
    tells us that there is an edge going from node 1 to node 3.
    """
    @staticmethod
    def initialize_nodes(input_rdd):
        # takes in a line and emits edges in the graph corresponding to that line
        def emit_edges(line):
            # ignore blank lines and comments
            if len(line) == 0 or line[0] == "#":
                return []
            # get the source and target labels
            source, target = tuple(map(int, line.split()))
            # emit the edge
            edge = (source, frozenset([target]))
            # also emit "empty" edges to catch nodes that do not have any
            # other node leading into them, but we still want in our list of nodes
            self_source = (source, frozenset())
            self_target = (target, frozenset())
            return [edge, self_source, self_target]

        # collects all outgoing target nodes for a given source node
        def reduce_edges(e1, e2):
            return e1 | e2 

        # sets the weight of every node to 0, and formats the output to the 
        # specified format of (source (weight, targets))
        def initialize_weights((source, targets)):
            return (source, (1.0, targets))
            
        nodes = input_rdd\
                .flatMap(emit_edges)\
                .reduceByKey(reduce_edges)\
                .map(initialize_weights)
        return nodes

    """
    Performs one iteration of the pagerank update algorithm on the set of node data.
    Details about the update algorithm are in the spec on the website.
    You are allowed to change the signature if you desire to.
    """
    @staticmethod
    def update_weights(nodes, num_nodes):
        """
        Mapper phase.
        Distributes pagerank scores for a given node to each of its targets,
        as specified by the update algorithm.
        Some important things to consider:
        We can't just emit (target, weight) values to the reduce phase, 
        because then the reduce phase will lose information on the outgoing edges
        for the nodes. We have to emit the (node, targets) pairs too so that 
        the edges can be remembered for the next iteration.
        Think about the best output format for the mapper so the reducer can
        get both types of information.
        You are allowed to change the signature if you desire to.
        """
        def distribute_weights((node, (weight, targets))):
            # YOUR CODE HERE
            Number_of_Targets = len(targets)
            List_of_Targets = list(targets)
            
            # Deal with situation of current node has no connections with others
            if Number_of_Targets == 0:
                Number_of_Targets = num_nodes - 1
                List_of_Targets = range(0, num_nodes)
                List_of_Targets.pop(node)
            
            # Scores of randomly following link
            Randomly_Follow_Link = 0.85 * weight / Number_of_Targets
            Distributed_Scores = list()
            for iteration in range(0, len(List_of_Targets)):
               Distributed_Scores.append((List_of_Targets[iteration], Randomly_Follow_Link))
            
            # Scores of staying on the same page
            Stay_on_the_Same_Page = (node, 0.05 * weight)
            Distributed_Scores.append(Stay_on_the_Same_Page)
            
            # Connection information
            Distributed_Scores.append((node, targets))
            
            return Distributed_Scores    

        """
        Reducer phase.
        We are given a node as a key and a list of all the values emitted by the mappers
        corresponding to that key.
        There should be two types of values:
        Pagerank scores, which represent how much score an incoming node is giving to us,
        and edge data, which we need to collect and store for the next iteration.
        The output of this phase should be in the same format as the input to the mapper.
        You are allowed to change the signature if you desire to.
        """
        def collect_weights((node, values)):
            # YOUR CODE HERE
            List_of_Values = list(values)
            
            # Connections
            for i in List_of_Values:
                if type(i) is frozenset:
                    targets = i
                    List_of_Values.remove(i)
            
            # Scores from randomly go to any page in the graph
            weight = 0.1
            
            # Scores collected from other pages
            for iteration in range(0, len(List_of_Values)):
                weight = weight + List_of_Values[iteration]
            
            return (node,(weight,targets))
        
        return nodes\
                .flatMap(distribute_weights)\
                .groupByKey()\
                .map(collect_weights)

    """
    Formats the output of the data to the format required by the specs.
    If you changed the format of the update_weights method you will 
    have to change this as well.
    Otherwise, this is fine as is.
    """
    @staticmethod
    def format_output(nodes):
        return nodes\
                .map(lambda (node, (weight, targets)): (weight, node))\
                .sortByKey(ascending = False)\
                .map(lambda (weight, node): (node, weight))
