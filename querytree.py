import math


class QueryTree:
    def __init__(self, head_node = None, total_cost = 0, total_rows = 0, total_width = 0):
        self.head_node = head_node
        self.total_cost = total_cost
        self.total_rows = total_rows
        self.total_width = total_width

    def print_query_tree(node):
        """
        Print the current node's details with indentation based on the level in the tree
        """
        indent = "----" * node.level  # 4 spaces per level for indentation
        print(f"{indent}{node.operator} (cost={node.cost}, rows={node.rows}, width={node.width})", end= '')
        
        # If there's a condition, print it with extra indentation
        if node.additional_info:
            print(f"  Additional Info: {node.additional_info}", end= '')
        print()
        
        # Recursively print each child node at the next indentation level
        for child in node.children:
            QueryTree.print_query_tree(child)


class QueryNode:
    def __init__(self, operator : str, level : int, cost, rows, width):
        self.operator = operator
        self.cost = cost
        self.rows = rows
        self.width = width
        self.additional_info = []
        self.level = level
        self.children = []


def create_query_tree(plan):
    """
    Create a query tree from the QEP
    """
    head_node = None
    stack = []  # Stack to track the parent nodes
    total_rows = 0
    total_cost = 0
    total_width = 0

    for step in plan:
        line = step[0].strip()

        # Determine the nesting level by counting the leading spaces
        nesting_level = math.ceil((len(step[0]) - len(line)) / 6)

        # Parse details from the line
        if 'cost=' in line:
            operator = line.split('(')[0].replace('->', '').strip()
            cost_str = line.split('cost=')[1].split('..')
            cost = float(cost_str[1].split()[0]) - float(cost_str[0])
            total_cost += cost
            rows = int(line.split('rows=')[1].split()[0])
            total_rows += rows
            width = int(line.split('width=')[1].split(')')[0])
            total_width += width
            
            # Check for filter condition and include it in `condition`
        else:
            stack[-1].additional_info.append(line)
            continue

        # Create a new QueryNode
        new_node = QueryNode(operator=operator, level= nesting_level, cost=cost, rows=rows, width=width)

        # If it's the first node, set it as the head node
        if head_node is None:
            head_node = new_node
        else:
            # Maintain the stack based on the nesting level
            while stack[-1].level > nesting_level:
                stack.pop()
            
            # Attach new_node as a child of the last node in the stack (current parent)
            if stack:
                stack[-1].children.append(new_node)

        # Add the new node to the stack at the current level
        stack.append(new_node)
    qtree = QueryTree(head_node, total_cost, total_rows, total_width)
    return qtree
