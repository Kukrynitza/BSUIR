
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        if not self.children:
            return self.value
        return f"({f' {self.value} '.join(map(str, self.children))})"

def parse(tokens):
    stack = []
    while tokens:
        token = tokens.pop(0)
        if token == '(':
            node = parse(tokens)
            stack.append(node)
        elif token == ')':
            break
        elif token in ['/\\', '\\/']:
            stack.append(token)
        else:
            stack.append(Node(token))
    while len(stack) >= 3:
        left, op, right = stack[0], stack[1], stack[2]
        if isinstance(op, str) and isinstance(left, Node) and isinstance(right, Node):
            new_node = Node(op, [left, right])
            stack = [new_node] + stack[3:]
        else:
            break
    return stack[0]

def parse_formula_to_tree(s: str) -> Node:
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] == '(' or s[i] == ')':
            tokens.append(s[i])
            i += 1
        elif s[i:i+2] in ['/\\', '\\/']:
            tokens.append(s[i:i+2])
            i += 2
        elif s[i] == '!':
            if i + 1 < len(s) and s[i+1].isupper():
                tokens.append(s[i:i+2])
                i += 2
            else:
                raise ValueError("Invalid negation")
        elif s[i].isupper():
            tokens.append(s[i])
            i += 1
        else:
            raise ValueError(f"Unexpected character: {s[i]}")
    return parse(tokens)


def is_literal(node: Node) -> bool:
    return not node.children

def is_disjunction(node: Node) -> bool:
    if node.value != '\\/':
        return False
    if len(node.children) != 2:
        return False

    left, right = node.children
    if right.value == '\\/':
        return False

    return (is_disjunction(left) or is_literal(left)) and is_literal(right)

def is_clause(node: Node) -> bool:
    return is_disjunction(node) or is_literal(node)

def is_conjunction(node: Node) -> bool:
    if node.value != '/\\':
        return False
    if len(node.children) != 2:
        return False

    left, right = node.children
    if right.value == '/\\':
        return False

    return (is_conjunction(left) or is_clause(left)) and is_clause(right)

def is_strict_cnf_tree(node: Node) -> bool:
    return is_conjunction(node) or is_clause(node)
