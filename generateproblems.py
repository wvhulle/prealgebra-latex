import random
import pandas,sympy
from functools import reduce
from sympy import N
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import standard_transformations,implicit_multiplication_application
from pylatex import Command,Document, Package, NoEscape, Section
from pylatex.utils import italic, escape_latex
#from random import random, random.randint, choices,choice
import inspect
from anytree import Node, RenderTree, AsciiStyle, LevelOrderIter,PreOrderIter
from anytree.util import leftsibling, rightsibling
import collections
import regex
from operators import parenthesis_op, linear_op, plus_op, minus_op, div_op, frac_op, power_op, identity_op, pythagorean_op, negate_op, sqrt_op, mul_op, is_binary_op, Number
from math import ceil, floor

def remove_frac(latex_expr):
    expr  = regex.sub(r'\\frac\{((?>[^{}]+|\{(?1)\})*)\}\{((?>[^{}]+|\{(?1)\})*)\}', r'( (\1)/(\2))', latex_expr)
    return(expr)


def latex_string_to_sympy(rand_expr):
    stripped_expr = regex.sub(r'\\left', ' ', rand_expr)
    stripped_expr = regex.sub(r'\\right', ' ', stripped_expr) # bug in sympy
    stripped_expr = regex.sub(r'\\cdot', r'*', stripped_expr)
    stripped_expr = stripped_expr.replace(':','/')
    stripped_expr = regex.sub(r'\\kgv', r'\\lcm', stripped_expr)
    
    if "=" in stripped_expr:
        stripped_expr = r"Eq(" + stripped_expr.replace("=", ",") + ")"
    while r'\frac' in stripped_expr:
        stripped_expr = remove_frac(stripped_expr)
    
    stripped_expr = stripped_expr.replace('$','')
    stripped_expr = stripped_expr.replace('\\','')
    stripped_expr = stripped_expr.replace('{','(')
    stripped_expr = stripped_expr.replace('}',')')
    stripped_expr = stripped_expr.replace('^','**')
    #print(stripped_expr)
    sympy_expr = parse_expr(stripped_expr, evaluate=False)
    return(sympy_expr)


# generator gives a question math string (without $$) in LaTeX
def generate_latex_question_with_answer(question_generator,difficulty, solver):
    loop = 0
    max_loop = 40
    found = False
    while not found and loop < max_loop:
        generated_question = question_generator(difficulty)
        rand_expr = generated_question[0]
        #print(rand_expr)
        hints = generated_question [1]
        latex_question_math = '\[' + rand_expr + '\]'
        latex_question_math_parsed = latex_string_to_sympy(rand_expr)
        sympy_string = str(latex_question_math_parsed)
        reduced_latex_question = sympy.latex(latex_question_math_parsed)
        solutions = solver(latex_question_math_parsed)
        latex_solution = str(sympy.latex(solutions))
        
        ## check length to exclude weird questions
        
        
        if len(sympy_string)>3*difficulty and len(sympy_string) <  10 *difficulty:
            
            # question might fit on a line and is not just a number
            reduce_ratio = len(latex_solution) / len(reduced_latex_question)
            ideal_ratio = 0.5 #* (1/(difficulty-1))
            
           
            if abs(reduce_ratio  - ideal_ratio) < 1:
                found = True
                latex_question_difficulty = min(max(difficulty-1,1),4) 
                latex_answer_question_math = '$' + latex_solution + '$'
                #print(latex_answer_question_math)
                if not isinstance(solutions, list):
                   latex_answer_question_math_eval = '$' + sympy.latex(N(solutions,3)) + '$'
                else:
                    latex_answer_question_math_eval = "$" + str(solutions) +"$"
            else:
                 print('Reduction ratio skewed: ', str(reduce_ratio), 'with ideal ', str(ideal_ratio))
        else: 
            print('Parsing failed: Raw ',  rand_expr, '-> Sympy ', sympy_string, ' ->  Sympy Latex ' , reduced_latex_question, ' -> Solved Latex ',  latex_solution)
        loop += 1

    if loop >= max_loop:
        print('Generated too many long or short questions with generator ',  str(question_generator))
    return([latex_question_difficulty, [latex_question_math, hints],latex_answer_question_math, latex_answer_question_math_eval])




def generate_exercises(question_generator,max_depth,max_number_of_exercises, title, advice, imperative,render_factorize_hint,solver):
    # Generate questions
    qas = []
    for i in range(max_number_of_exercises):
        difficulty = random.randint(ceil(max_depth/2),max_depth)
        qa = generate_latex_question_with_answer(question_generator, difficulty,solver)
        
        qas.append(qa)
    return([title,advice,imperative,qas,render_factorize_hint])


def add_exercises(doc, full_qas, with_answers):
    
    qas = full_qas[3]
    #print('First question with answers in section is saved as :, ', qas[0] )
    advice_for_exercises = full_qas[1]
    title = full_qas[0]
    imperative =full_qas[2]
    hint_renderer = full_qas[4]
    n =str(len(qas))
    # Generate section header LaTeX
    if not with_answers:
        punten_telling = r'\margintext{' + ".../"+ n + '}'
        section_title_string = title + ' ('+ '*' * (qas[0])[0]  +') '
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(punten_telling))
        doc.append(NoEscape(advice_for_exercises))
        doc.append(NoEscape(r"""
        %\begin{multicols}{2}
        \begin{enumerate}
        """))
    else: 
        punten_telling = r'\margintext{' +  n + "/"+ n +'}'
        section_title_string = title + r' (oplossing)' + ' ('+ '*' * (qas[0])[0] +')' 
        
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(punten_telling))
        doc.append(NoEscape(r"""
        \begin{multicols}{2}
        \begin{enumerate}
        """))

    for qa in qas:
        stars = min(3,max(1,qa[0]))
        initial_question = qa[1][0]
        if 'x' in initial_question:
            derivsep = r'\Leftrightarrow'
        else:
            derivsep = r'='
       # print('The initial questions is ', initial_question)
        hints = qa[1][1]
        #print('outputting question ', initial_question, ' with hints ', hints)
        doc.append(NoEscape(r'\begin{minipage}{\linewidth}  \item ' + imperative + r': '))
        doc.append(NoEscape(initial_question))
        if not with_answers:
            if len(hints) > 0 :
                # start hints
                doc.append(NoEscape(r'\begin{center}'))
                for hint in hints:
                   # doc.append(NoEscape(r'\item'))
                    rendered_hint = hint_renderer(hint)
                    #print('The hint '+ str(hint) + ' will be rendered as ', rendered_hint)
                    doc.append(NoEscape(rendered_hint))
                # start emptylines
                doc.append(NoEscape(r'\end{center}'))
            #doc.append(NoEscape(r'\derivblank{' + str(stars -1) +'}{'+derivsep+'}'))
            doc.append(NoEscape(r'\derivblank{' + str(stars -1) +'}{'+derivsep+r'} \end{minipage} \\'))
        else:
            doc.append(NoEscape(r'\derivblanksolution{' + qa[2] + '}{' + qa[3] + r'} \end{minipage} \\'))
    if with_answers:
        doc.append(NoEscape(r"""
        \end{enumerate}
        \end{multicols}
        """))
    else: 
        doc.append(NoEscape(r"""
        \end{enumerate}
        %\end{multicols}
        """))

# TODO: question types: simplify, factorize/expand




def print_tree_simple(root):
    for pre, _, node in RenderTree(root):
        print("%s%s[%s]" % (pre, node.operator.name, node.number))

def extend_tree(op,current_leaf):
    current_integer = current_leaf.number
    children_numbers = op.inverse_map(current_integer)
    #print("Splitting up "+str(current_integer)+" with operator "+str(op.name)+" into "+ str(op.inverse_map(current_integer)))
    current_leaf.render = op.layout_function
    current_leaf.children = list(map(lambda n : Node(str(n), parent=current_leaf, number = n,render=lambda n : Number(n), operator=op),children_numbers))
    first_child = current_leaf.children[0]
    return(first_child)

def is_right_argument(child_node):
    return(leftsibling(child_node) != None) 

def is_left_argument(child_node):
    return(rightsibling(child_node) != None) 

def compute_solution_number(max_digits):
    max10 = max(20, 10**(max_digits-1))
    solution_number = random.randint(-max10,max10)
    return(solution_number)

def arithmetic_tree(max_height, max_digits, operators, single_use_operators):
    solution_number = compute_solution_number(max_digits)
    print("==================\nGenerating expression with solution " + str(solution_number))
    root = Node(str(solution_number), parent=None, number=solution_number,operator=identity_op,render=identity_op.layout_function)
    #max_n_operators = len(single_use_operators)+int(len(operators))
    single_use_used = 0
    for i in range(max_height):
        r = random.random()
        if single_use_used < len(single_use_operators) and r < 0.8:
            op = single_use_operators[single_use_used]
            single_use_used = single_use_used + 1
        else:
            op = random.choices(operators)[0]
        leaf_weights = list(map((lambda leaf : op.likelihood_number_is_output(leaf.number)),list(root.leaves)))
        current_leaf =  random.choices(population=root.leaves, weights=leaf_weights)[0]
        ## it is possible that this leaf is actually not appropriate,
        if current_leaf.number < 0:
            # we have to turn it in a negation operator
            current_leaf = extend_tree(negate_op, current_leaf)
        if op.likelihood_number_is_output(current_leaf.number) > 0: 
            # make new child node
            if (not current_leaf.is_root):
                # check if the child node needs a bracket
                parent_op = current_leaf.operator
                if is_binary_op(parent_op) and is_binary_op(op):
                    associativity = parent_op.is_associative
                    descending_in_the_wrong_way = (is_right_argument(current_leaf) and (associativity == "left")) or (is_left_argument(current_leaf) and (associativity == "right"))
                    non_associativity =  descending_in_the_wrong_way and (op.order_of_application == parent_op.order_of_application)
                    precedence_problem = (is_binary_op(op) and parent_op.order_of_application < op.order_of_application)
                    put_brackets_around_leaf =  precedence_problem or non_associativity  and parent_op != identity_op and parent_op != parenthesis_op

                    #print("Parent operator: "+str(parent_op.name)+", current number: "+str(current_leaf.number)+", new operator: "+str(op.name)+", is guarded with  brackets: "+str(put_brackets_around_leaf))

                    if put_brackets_around_leaf:
                        current_leaf = extend_tree(parenthesis_op, current_leaf)
            extend_tree(op, current_leaf)
    print_tree_simple(root)
    return(root)



def render_tree(node):
    if node.is_leaf:
        return(node.render(node.number))
    else:
        return(node.render(list(map(render_tree, node.children))))

def stackOperators(max_height,max_digits, operators,single_use_operators):
    root = arithmetic_tree(max_height, max_digits, operators, single_use_operators)
    #apply_inverse_identities(root,[example_identity])
    latex_math_expr = render_tree(root)
    # TODO perform post-processing on tree with identities such as (a+b)^2 = a^2 + ....

    #print(sympy.latex(sympy.expand(latex_string_to_sympy(str(latex_math_expr)))))
    #latex_math_expr = str(sympy.latex(sympy.expand(latex_string_to_sympy(str(latex_math_expr)))))
    #print("Generated expression: "+ str(latex_math_expr))
    #actual_solution = N(latex_string_to_sympy(str(latex_math_expr)))
    # solution_number = compute_solution_number(max_digits)
    # if actual_solution != solution_number:
    #     print("Actual solution "+str(actual_solution)+" is not equal to "+str(solution_number))
    return(latex_math_expr )      

def generate_Z_arithm_questions(difficulty, number):
    def question_Z_arithm_generator(difficulty):
        hints = []
        ops = [negate_op, sqrt_op,plus_op,mul_op,power_op,pythagorean_op, div_op]
        main_question = str(stackOperators(difficulty,2,ops,[]))
        #main_question = str(randomExpression(0.05,difficulty, True, False, fractions))
        #print(main_question)
        return([main_question,hints])

    title = r"Volgorde van de bewerkingen in Z"
    advice = r"""
    Vereenvoudig de volgende uitdrukkingen zoveel mogelijk in deze volgorde: (1) haakjes, (2) machten en wortels, (3) vermenigvuldiging en deling en (4) optelling en aftrekking.
    \begin{itemize}
    \item Exponenten groter dan $4$ hoeven niet berekend te worden. 
    \end{itemize}
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises( question_Z_arithm_generator,difficulty,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)


def question_Q_arithm_generator(difficulty):
        hints = []
        ops = [minus_op, negate_op, sqrt_op,plus_op,frac_op,mul_op,power_op,pythagorean_op,div_op ]
        main_question = str(stackOperators(difficulty,2,ops,[]))
        #print(main_question)
        return([main_question,hints])


def generate_Q_arithm_questions(difficulty, number):
    title = r"Volgorde van de bewerkingen in Q"
    advice = r"""
    Vereenvoudig de volgende uitdrukkingen zoveel mogelijk in deze volgorde: (1) haakjes, (2) machten en wortels, (3) vermenigvuldiging en deling en (4) optelling en aftrekking.
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises( question_Q_arithm_generator,difficulty,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)


def generate_Z_unknown_questions(difficulty, number):
    def question_Z_unknown_generator(difficulty):
        hints = []
        ops = [minus_op,identity_op,negate_op,plus_op,mul_op,power_op,pythagorean_op,div_op]
        prop_ops =  [linear_op]
        random.shuffle(prop_ops)
        without_x = str(stackOperators(difficulty,2,ops,[plus_op,mul_op]))
        with_x = str(stackOperators(difficulty,2,ops,prop_ops))
        if random.random() < 0.5:
            left_eq = with_x
            right_eq = without_x
        else:
            left_eq = without_x
            right_eq = with_x
        main_question = left_eq + r'='+right_eq
        return([main_question,hints])
    title = r"Vergelijkingen in Z"
    advice = r"""
    Breng alle onbekenden naar het linkerlid. Als er alleen maar een constante voor $x$ staat, moet je die constante ook naar het andere lid brengen door die te laten zakken. Wat is $x$?
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    def solver(eq):
        return(sympy.solve(eq,sympy.Symbol('x')))
        
    full_problems = generate_exercises( question_Z_unknown_generator,difficulty,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)

def generate_proportions(difficulty, number):
    def question_proportions_generator(difficulty):
        hints = []
        ops = [identity_op,minus_op,negate_op,plus_op,mul_op,power_op,pythagorean_op]
        prop_ops =  [frac_op, linear_op]
        random.shuffle(prop_ops)
        without_x = str(stackOperators(difficulty,2,ops,[frac_op]))
        with_x = str(stackOperators(difficulty,2,ops,prop_ops))
        if random.random() < 0.5:
            left_eq = with_x
            right_eq = without_x
        else:
            left_eq = without_x
            right_eq = with_x
        main_question = left_eq + r'='+right_eq
        return([main_question,hints])
    title = r"Evenredigheden in Z"
    advice = r"""
    Gebruik de hoofdeigenschap van evenredigheden (de kruisregel) en los op naar de onbekende $x$. Wat is $x$?
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    def solver(eq):
        return(sympy.solve(eq,sympy.Symbol('x')))
        
    full_problems = generate_exercises( question_proportions_generator,difficulty,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)



def generate_N_division_questions(difficulty, number):
    def question_N_division_generator(difficulty):
        dn = abs(random.randint(10**(difficulty),10**difficulty+1))
        d = abs(random.randint(10**(difficulty-1),10**(difficulty)))
        math = MixfixWithoutCurlyBrackets(Number(dn),":",Number(d))
        hints = [r' \opdiv[resultstyle=\gobble,remainderstyle=\gobble,maxdivstep=5,dividendbridge] {' + str(dn) + r'}' +r'{'+ str(d) + r'}']
        return([str(math),hints])

    title = r"Delen in N"
    advice = r"""
    Gebruik de staartdeling of lange deling om deze deling uit te voeren. Geef ook de rest. Bijvoorbeeld $5:2 = 2 + 1:2 = 2 + 1/2$. 
    """
    imperative = "Deel"
    hinter = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises(question_N_division_generator,difficulty+1,number, title, advice, imperative,hinter,solver)
    return(full_problems)

def generate_pdf_with_questions(latex_section_list):
    doc = Document()
    doc.documentclass = Command(
            'documentclass',
            options=['dutch','course','headersection','theoremsection','cleardoublepage','twoside'],
            arguments=['lecture'],
        )
    doc.preamble.append(NoEscape(r"""
    \title{Toets 3}
    \subtitle{Vergelijkingen in Z, bewerkingen in Q, evenredigheden, vraagstukken en procenten}
    \shorttitle{BASIS}
    \author{Student: \underline{\hspace{5cm}}}
    \speaker{Leerkracht: Willem Vanhulle}
    %\email{willemvanhulle [at] gmail.com}
    \date{16}{11}{2020}
    \dateend{12}{01}{2021} 
    \conference{Lessenreeks aan CVO Volt}
    \place{Leuven, Belgi\"e}
    \flag{Geschreven op \today}
    \attn{Derde toets voor studenten aan het CVO. De eerste oefeningen zijn alleen bedoeld voor studenten die een onvoldoende hadden voor de vorige testen en dienen als inhaaltoets.}


    %De moeilijkheidsgraad van elke oefening is aangegeven met een aantal ``*''-en. Schrijf berekeningen op als volgt:
    %\noindent
    %    \begin{align*}
    %     &= \hspace{0.2cm}\underline{\mystrut \text{Voorlaatste stap in berekening}  }  \\
        %   &=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %symbolisch antwoord} }  $\approx$ \underline{ \text{Decimale %benadering tot 3 cijfers} }}
        %&=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %antwoord} } }
        %\end{align*}
    """))

    doc.append(NoEscape(r"\part{Vragen}"))
    for full_section in latex_section_list:
        add_exercises(doc,full_section,False)

    doc.append(NoEscape(r"\part{Antwoorden}"))
    for full_section in latex_section_list:
        add_exercises(doc,full_section,True)
    #add_factorize_exercises(3,2)
    #add_factorize_exercises(3,4)
    #add_lcm_exercises(3,4)

    #add_add_fractions_exercises(3,4)

    # Print out the questions with answers in Latex
    # add_simplify_root_exercises(root_questions_with_answers, True)


    #add_exercise_order_operations(6,20, fractions = False, hard_exponents = False)
    #add_simplify_fractions_exercises(3,10)
    #add_lcm_exercises(2,10)
    #add_add_fractions_exercises(1,10)
    #add_add_fractions_exercises(3,10)
    #add_exercise_order_operations(5,20, fractions = True, hard_exponents= False)
    #add_exercise_order_operations(7,20, fractions = False, hard_exponents= False)

    doc.generate_tex('build/assignment')
    doc.generate_pdf('build/assignment', silent=True)


generate_pdf_with_questions([generate_Q_arithm_questions(6,20), generate_Z_unknown_questions(3,4),generate_proportions(3,4)])