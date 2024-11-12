import networkx as nx


class Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes = []
        self.edges = []
        self.node_counter = 0  # for ID generation

    def parse_qep(self, qep):
        """
        Parse the query execution plan (QEP) and build the nodes and edges for the graph.
        """

        def traverse_plan(plan_tree, parent_id=None):
            node_id = self.node_counter  # Use the counter as the node ID
            self.node_counter += 1
            node_label = plan_tree['Node Type']
            total_cost = plan_tree.get('Total Cost', 0)
            rows = plan_tree.get('Plan Rows', 0)
            node_info = {
                'id': node_id,
                'label': node_label,
                'cost': total_cost,
                'rows': rows,
                'info': plan_tree
            }
            # print(f"Appending node: {node_info}")
            self.nodes.append(node_info)

            if parent_id is not None:
                # print(f"Appending edge: {parent_id} -> {node_id}")
                self.edges.append((parent_id, node_id))

            if 'Plans' in plan_tree:
                for subplan in plan_tree['Plans']:
                    # Recursively traverse the plan tree
                    # print(f"Traversing subplan: {subplan['Node Type']}")
                    traverse_plan(subplan, parent_id=node_id)

        # Start traversing from the root plan
        root_plan = qep[0]['Plan']
        # Traverse the plan tree
        traverse_plan(root_plan)

    def print_graph(self):
        """
        Print the nodes and edges of the graph.
        """
        print(self.nodes)
        print(self.edges)

    def build_graph(self):
        """
        Build the graph from the nodes and edges.
        """

        for node in self.nodes:
            self.G.add_node(node['id'], label=node['label'], cost=node['cost'], rows=node['rows'], info=node['info'])
        for edge in self.edges:
            self.G.add_edge(edge[0], edge[1])

        return self.G
