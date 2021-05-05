### Ideas for applying identities

def flatten_list_of_lists(x):
    return([j for i in x for j in i])



def compare_trees(big_tree,symbolic_tree):
    c1 = [n.operator for n in big_tree.children]
    c2 = [n.operator for n in symbolic_tree.children] 
    if len(c2) == 0:
        print("The expression "+str(symbolic_tree.symbolic_expression)+" should be equal to "+str(big_tree.number))
        return(Eq(parse_expr(symbolic_tree.symbolic_expression),parse_expr(str(big_tree.number))))
    elif c1 == c2:
        print("Descending into tree for comparison.")
        return(flatten_list_of_lists(list(map(lambda i : compare_trees(c1[i],c2[2]), range(len(c1)))) ))
    else:
        return([])

def tip_of_small_tree(big_tree,small_tree):
    # returns top of small_tree in big_tree
    expanded_tree_top_matches = [node for node in  LevelOrderIter(big_tree, filter_=lambda n: n.operator == small_tree.operator)]
    if len(expanded_tree_top_matches)> 0:
        for subtree in expanded_tree_top_matches:
            comparison = compare_trees(subtree,small_tree)
            if comparison != None:
                subtree, matched_leaves = comparison
                if len(matched_leaves)>0:
                    return([subtree, matched_leaves])


### (a+b)^2
### -> a + b
###    -> a
###    -> b

simplified = Node("simplified",operator=identity_op,symbolic_expression="(a+b)^2", children=[Node("variable",operator=power_op,symbolic_expression="a+b", children= [Node("variable", operator=plus_op, symbolic_expression="a")]), Node("variable", operator=plus_op, symbolic_expression="b")])

# TODO need a way to generate these trees from text: a^2 + 2ab + b^2 => (a+b)^2
expanded = Node("expanded", operator=identity_op, symbolic_expression="a^2+b^2+2ab", children = [Node("leaf", operator=plus_op,symbolic_expression="a^2+b^2"),Node("leaf", operator=plus_op, symbolic_expression = "2ab")])

example_identity = (simplified, expanded)

def apply_inverse_identities(tree,identities_list):
    for identity in identities_list:
        expanded_tree, simplified_tree = identity   
        ## expanded tree and simplified contain leaves with the same unknowns a,b,c ....
        comparison  = tip_of_small_tree(tree,expanded_tree)
        if comparison != None:
            tree_to_replace, matched_leaves = comparison
            ## 1. set tip of tree_to_replace equal to tip of simplified_tree
            tree_to_replace.parent.children = [simplified_tree if n != tree_to_replace else n for n in tree_to_replace.parent.children]
            ## 2. determine values of unknowns a,b,c by looping over expanded_tree
            equation_list = matched_leaves
            values = sympy.solve(equation_list)
            for n in simplified_tree.leaves:
                current_expression = parse_expr(n.symbolic_expression)
                n.number = current_expression.xreplace(values)
                ### how can i just substitute the solved variables in an expression?

