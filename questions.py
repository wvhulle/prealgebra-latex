""""
Renders a list of basic arithmetic problems into a problem sheet which is output to LaTeX and eventually a pdf.
"""


from operators import RandomInverseOperator, parenthesis_op, linear_op, plus_op, minus_op, div_op, frac_op, power_op, identity_op, pythagorean_op, negate_op, sqrt_op, mul_op, is_binary_op, Number
from typing import Any, Set, Callable, List, Tuple, FrozenSet
from dataclasses import dataclass
from datetime import datetime
from sympy import simplify, N
from sympy.parsing.sympy_parser import parse_expr, split_symbols_custom
from math import sqrt,ceil,log, log2, log10, floor, ceil, log
from statistics import mean
from google_trans_new import google_translator  
from regex import sub
from copy import deepcopy
import random
from anytree import Node, RenderTree, AsciiStyle, LevelOrderIter,PreOrderIter
from anytree.util import leftsibling, rightsibling
import subprocess

@dataclass
class ProblemProperties:
    """Contains the properties of a mathematical question that are enough to reinstate 
    the numbers (and unknowns) in the question with changing any of the properties or arguments
    of this object.
    
    Args:
        age: the age at which this problem is usually given
        minutes: the time required to solve at the usual age
        operatorset: the (inverted) operators that may appear in the problem
        difficulty: 
    """
    age : int 
    minutes : int
    operatorset : FrozenSet[RandomInverseOperator]
    difficulty : int

@dataclass
class ProblemContext:
    """
    Arbitrary context of the problem that is largely independent of the inverse operators used in the computation.
    Should be mostly natural language or contextual information such as "imagine a ladder standing..., then compute ..."
    """
    url : str
    sketch : str
    imperative : str
    stepsign : str
    language : str

@dataclass
class ProblemExpressions:
    """
    The actual computations in the problem and the solutions, with the math written in LaTeX math mode but still surrounded by \( and \).
    """
    date : datetime
    hint : str
    question : str
    solution : str
    exactsolution : str
    

def latex_string_to_sympy(rand_expr):
    stripped_expr = sub(r'\\left', ' ', rand_expr)
    stripped_expr = sub(r'\\right', ' ', stripped_expr) # bug in sympy
    stripped_expr = sub(r'\\cdot', r'*', stripped_expr)
    stripped_expr = stripped_expr.replace(':','/')
    stripped_expr = sub(r'\\kgv', r'\\lcm', stripped_expr)
    
    if "=" in stripped_expr:
        stripped_expr = r"Eq(" + stripped_expr.replace("=", ",") + ")"
    
    def remove_frac(latex_expr):
        expr  = sub(r'\\frac\{((?>[^{}]+|\{(?1)\})*)\}\{((?>[^{}]+|\{(?1)\})*)\}', r'( (\1)/(\2))', latex_expr)
        return(expr)
    
    while r'\frac' in stripped_expr:
        stripped_expr = remove_frac(stripped_expr)
    
    stripped_expr = stripped_expr.replace('$','')
    stripped_expr = stripped_expr.replace('\\','')
    stripped_expr = stripped_expr.replace('{','(')
    stripped_expr = stripped_expr.replace('}',')')
    stripped_expr = stripped_expr.replace('^','**')
    print("Going to parse: ", stripped_expr)
    sympy_expr = parse_expr(stripped_expr, evaluate=False)
    return(sympy_expr)

naturalOperators = frozenset([parenthesis_op, plus_op, power_op, identity_op, mul_op, pythagorean_op])
integerOperators = naturalOperators.union([minus_op, negate_op])
rationalOperators = integerOperators.union([frac_op, div_op])
realOperators = rationalOperators.union([sqrt_op])
allOperatorClasses = [naturalOperators, integerOperators, rationalOperators,rationalOperators]



def extend_tree(op : RandomInverseOperator ,current_leaf):
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


def print_tree_simple(root):
    for pre, _, node in RenderTree(root):
        print("%s%s[%s]" % (pre, node.operator.name, node.number))

def arithmetic_tree(max_height : int, max_digits : int, operators : List[RandomInverseOperator], single_use_operators: List[RandomInverseOperator]) -> any: # should be a tree
    """
    Starts with applying a single use random inverse operator and then continues with the other operators.
    Makes a tree by decomposing a number recursively with inverse operators.
    Breaks branches randomly, stops at a leave and at some fixed maximal depth/height it returns the tree.
    """
    max10 = max(20, 10**(max_digits-1))
    solution_number = random.randint(-max10,max10)
    print("==================\nGenerating expression with solution " + str(solution_number))
    root = Node(str(solution_number), parent=None, number=solution_number,operator=identity_op,render=identity_op.layout_function)
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
        # it is possible that this leaf is actually not appropriate,
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

class Problem:
    """
    A problem contains everything needed to generate similar computations to do for students on a problem sheet.
    The actual computation is initialized with the function expressionrenderer. Context may stay the same but can be manually updated.
    """
    properties :  ProblemProperties
    context : ProblemContext
    expressions : ProblemExpressions
    def __init__(self, properties, context):
        self.properties = properties
        self.context = context
        self.expressionrenderer()
        self.solutionrenderer()
        self.hintrenderer()

    def expressionrenderer(self):
        problemOperators = list(self.properties.operatorset)
        heightTree = int(ceil(self.properties.difficulty*log2(self.properties.minutes)))
        numberDigits = int(ceil(log10(self.properties.age+1)*2))
        underlyingOperatorClass = max(allOperatorClasses, key = lambda operatorClass : len(listintersection(operatorClass,problemOperators)))
        
        # TODO implement an if branch for when there is an unknown operator and paste together two trees with an unknown on one side
        # TODO even better would be to start with x . (1)  left and right with an arbitrary integer and then paste together
        # TODO but then the arithmetic_tree function has to be modified to get a number as argument
        expressiontree = arithmetic_tree(heightTree,numberDigits,list(problemOperators),list(underlyingOperatorClass))
        expression =  r'\(' +  str(render_tree(expressiontree))+r'\)'
        self.expressions = ProblemExpressions(datetime.now(), "", expression, "","")

    def solutionrenderer(self):
        latex_question_math_parsed = latex_string_to_sympy( self.expressions.question)
        self.expressions.solution = r'\(' + str(simplify(latex_question_math_parsed)) +r'\)'
        self.expressions.exactsolution = r'\(' + str(N(latex_question_math_parsed, 3))+r'\)'

    def hintrenderer(self):
        self.expressions.hint = r'Doe gewoon dit \(\rightarrow\).'

@dataclass
class Classroom: 
    """
    Stands for the level of familiarity a classroom of students has with specific operators. As well as their agerange etc.
    It also says whether answers should be printed at the end of the problem sheet.
    """
    language : str
    agerange : Tuple[int,int] #= (10,15)
    difficultyrange : Tuple[int,int]
    operators : Set[RandomInverseOperator]
    withanswers : bool = True

@dataclass
class TimedSection:
    """
    Args: 
        totalminutes: the time one section lasts.
        unseenproportion: the proportion of time that is spent on problems that where not generated in the last 2 months (are new)
        room: properties of the group of students
        statements: a list of the actual problems.
    """
    totalminutes : int #= 60
    unseenproportion: float #= 0.9
    room : Classroom
    statements : List[Problem]
    title : str

def trans(text,src,dst):
        translator = google_translator()
        translatedtext = translator.translate(text,lang_src=src,lang_tgt=dst)
        return(translatedtext)

def listintersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def generateTimedSection(minutes : int,room : Classroom) -> TimedSection:
    """ 
    Generate a section of exercises within the problem sheet based on the total time required for the section.
    """
    age = int(mean([room.agerange[0],room.agerange[1]]))
    difficulty = room.difficultyrange[1]
    """TODO 
    - load serialized database for problems
        - in case it is in csv format, read_csv("problem_database.csv") 
    - find problems that satisfy room and time requirements
        - initialize empty list of statements first
        - added problems have total time of seenminutes = (1-room.unseenproporition) * minutes 
    - initialize m = seenminutes, and complete with unseenexercises
    """
    m = 0
    title = trans("Oefeningen", 'dutch', room.language)
    statements = []
    while m < minutes:
        problem = Problem(
            ProblemProperties(age,minutes,room.operators, difficulty), 
            ProblemContext(r"https://github.com/wvhulle/prealgebra-latex", r"berekening", r"Los op", r'=','dutch')
        )
        problem.context.sketch = trans(problem.context.sketch,problem.context.language,room.language)
        problem.context.imperative = trans(problem.context.imperative,problem.context.language,room.language)    
        m = m + 1 
        statements.append(problem)
        #TODO add problem also to connected database
    timedSection = TimedSection(minutes,1, room, statements,title)
    #TODO close database
    return(timedSection)

def renderTimedSectionLaTeX(section : TimedSection) -> str:
    LaTeXString = r""
    LaTeXString = LaTeXString + r"\begin{enumerate}" + "\n"
    for problem in section.statements:
        LaTeXString = LaTeXString + r'\begin{minipage}{\linewidth}'+ "\n" + r'\item ' + problem.context.imperative + r': '
        if not section.room.withanswers:
            LaTeXString = LaTeXString + trans(problem.context.sketch, problem.context.language, section.room.language)  + "\n"
            LaTeXString = LaTeXString + problem.expressions.question
            LaTeXString = LaTeXString + r'\derivblank{' + str(problem.properties.difficulty -1) + r'}{' + problem.context.stepsign + r'}' + "\n"
        else:            
            LaTeXString = LaTeXString + problem.expressions.question
            LaTeXString = LaTeXString + r'\derivblanksolution{' + problem.expressions.solution + '}{' + problem.expressions.exactsolution + r'}' + "\n"
        LaTeXString = LaTeXString + r'\end{minipage} \\' + "\n"
    LaTeXString = LaTeXString + r"\end{enumerate}" + "\n"
    return(LaTeXString)

def renderSectionTitleLaTeX(section : TimedSection) -> str:
    titleString = ""
    section_title_string = section.title + ' ('+ str(section.totalminutes) + " min." +r')'
    n = len(section.statements)
    if not section.room.withanswers:
        punten_telling = r'\margintext{' + ".../"+ str(n) + r'}'
    else: 
        punten_telling = r'\margintext{' +  str(n) + "/"+ str(n) +r'}'
    titleString = titleString + r"\section{"+section_title_string+r"}"+ punten_telling + "\n"
    return(titleString)

def renderLaTeX(title, author, sections:List[TimedSection]) -> str:
    """
    Return a LaTeX string of the problem sheet that should be written to a file and compiled with LateX
    """
    language = sections[0].room.language
    doc = r""
    questionsections = []
    answersections = []

    for section in sections:
        if not section.room.withanswers:
            questionsections.append(section)
        else:
            answersections.append(section)
    doc = r"\part{"+trans("Vragen","dutch",section.room.language)+"}" +"\n" + doc
    for section in questionsections:
        doc = doc + renderSectionTitleLaTeX(section)
        doc = doc + renderTimedSectionLaTeX(section)
    if len(answersections) > 0:
        doc = doc + r"\part{"+trans("Antwoorden","dutch",section.room.language)+r"}" + "\n"
        for section in answersections:
            doc = doc + renderSectionTitleLaTeX(section)
            doc = doc + renderTimedSectionLaTeX(section)
    # use section.room to make document title and close document
    docpreamble = r"\documentclass["+ language + r",course]{lecture}" + "\n" + r"\title{" + doctitle + r"} \author{"+ docauthor + r"}"+"\n" + r"\begin{document}" + "\n"
    docpostamble = r"\end{document}" + "\n"
    doc = docpreamble + doc + docpostamble
    return(doc)

def writePDF(doctitle : str, docauthor : str, sections : List[TimedSection]):
    doc = renderLaTeX(doctitle,docauthor, sections)
    text_file = open("doc.tex", "w")
    text_file.write(doc)
    text_file.close()
    bashCommand = "latexmk doc.tex"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE,cwd='./')
    output, error = process.communicate()

doctitle = "TITLE"
docauthor = "AUTHOR"

exampleRoom = Classroom("english",(10,12),(0,3),[plus_op,minus_op,frac_op],False)
exampleSection = generateTimedSection(20, exampleRoom)
exampleSectionWithAnswers = deepcopy(exampleSection)
exampleSectionWithAnswers.room.withanswers = True

writePDF(doctitle,docauthor,[exampleSection, exampleSectionWithAnswers])