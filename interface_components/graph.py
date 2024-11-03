import networkx as nx
import plotly.graph_objects as go


class Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes = []
        self.edges = []

    def parse_qep(self, qep):
        """Parse the QEP JSON into a format suitable for NetworkX."""

        def traverse_plan(plan_tree, parent_id=None):
            node_id = plan_tree.get('Plan Node Type ID', id(plan_tree))  # Unique identifier
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
        print(self.nodes)
        print(self.edges)

    def hierarchy_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        '''
        Position nodes in a hierarchical layout.
        '''
        if not nx.is_tree(G):
            raise TypeError('Cannot use hierarchy_pos on a graph that is not a tree')

        if root is None:
            root = next(iter(nx.topological_sort(G)))  # Find a root node

        def _hierarchy_pos(G, node, left, right, vert_loc, xcenter, pos):
            children = list(G.successors(node))
            if not children:
                pos[node] = (xcenter, vert_loc)
            else:
                dx = (right - left) / len(children)
                nextx = left + dx / 2
                for child in children:
                    pos = _hierarchy_pos(G, child, nextx - dx / 2, nextx + dx / 2, vert_loc - vert_gap, nextx, pos)
                    nextx += dx
                pos[node] = (xcenter, vert_loc)
            return pos

        return _hierarchy_pos(G, root, 0, width, vert_loc, xcenter, {})

    def build_graph(self):
        """Build the graph from the parsed QEP."""

        for node in self.nodes:
            self.G.add_node(node['id'], label=node['label'], cost=node['cost'], rows=node['rows'], info=node['info'])
        for edge in self.edges:
            self.G.add_edge(edge[0], edge[1])

    def plot_graph(self):

        pos = self.hierarchy_pos(self.G)  # Ensure self.G is passed correctly
        edge_x = []
        edge_y = []

        # Create edges
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create nodes
        node_x = []
        node_y = []
        node_text = []

        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            data = self.G.nodes[node]
            text = f"{data['label']}<br>Cost: {data['cost']}<br>Rows: {data['rows']}"
            node_text.append(text)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            textposition="bottom center",
            textfont_size=10,
            marker=dict(
                size=20,
                color='#1f78b4',
                line=dict(width=2, color='black')
            ),
            text=[self.G.nodes[node]['label'] for node in self.G.nodes()],
            hoverinfo='text',
            hovertext=node_text
        )

        return go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            # title='Query Execution Plan',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))
