import random
import pandas,sympy
from functools import reduce
from math import sqrt,ceil,log, log2, log10, floor, ceil, log
from sympy import N
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import standard_transformations,implicit_multiplication_application
from pylatex import Command,Document, Package, NoEscape, Section
from pylatex.utils import italic, escape_latex
#from random import random, random.randint, choices,choice
from sympy.ntheory import factorint
import inspect
from anytree import Node, RenderTree
from anytree.util import leftsibling
from numpy import prod
import collections
import regex

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

%\maketitle

%	\vspace{3em}
%\textbf{Naam student:} \hrulefill\\

%De moeilijkheidsgraad van elke oefening is aangegeven met een aantal ``*''-en. Schrijf berekeningen op als volgt:
%\noindent
%    \begin{align*}
   %     &= \hspace{0.2cm}\underline{\mystrut \text{Voorlaatste stap in berekening}  }  \\
     %   &=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %symbolisch antwoord} }  $\approx$ \underline{ \text{Decimale %benadering tot 3 cijfers} }}
      %&=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %antwoord} } }
    %\end{align*}
"""))

def remove_frac(latex_expr):
    expr  = regex.sub(r'\\frac\{((?>[^{}]+|\{(?1)\})*)\}\{((?>[^{}]+|\{(?1)\})*)\}', r'( (\1)/(\2))', latex_expr)
    return(expr)


def latex_string_to_sympy(rand_expr):
    # compute slightly simplified question with sympy from latex
    stripped_expr = regex.sub(r'\\left', ' ', rand_expr)
    # stripped_expr = stripped_expr.replace('\\left','')
    # stripped_expr = stripped_expr.replace('\\right','')

    stripped_expr = regex.sub(r'\\right', ' ', stripped_expr) # bug in sympy
    stripped_expr = regex.sub(r'\\cdot', r'*', stripped_expr)
    stripped_expr = stripped_expr.replace(':','/')
    stripped_expr = regex.sub(r'\\kgv', r'\\lcm', stripped_expr)
    
    if "=" in stripped_expr:
        stripped_expr = r"Eq(" + stripped_expr.replace("=", ",") + ")"
    # print(stripped_expr)
    # if  not "lcm" in stripped_expr:
    #     sympy_expr = parse_latex(stripped_expr)
    # else:
    
   # stripped_expr = re.sub(r'\{ *([^()]+?) *\})', r'$1', stripped_expr)
    while r'\frac' in stripped_expr:
        stripped_expr = remove_frac(stripped_expr)
    
    stripped_expr = stripped_expr.replace('$','')
    stripped_expr = stripped_expr.replace('\\','')

    #stripped_expr = stripped_expr.replace(':','/')
    stripped_expr = stripped_expr.replace('{','(')
    stripped_expr = stripped_expr.replace('}',')')
    stripped_expr = stripped_expr.replace('^','**')
    #print('Parsing unlatexified:    ', stripped_expr)
    sympy_expr = parse_expr(stripped_expr, evaluate=False)
    return(sympy_expr)


def add_exercises_knowledge( max_difficulty, max_number_of_exercises):
    punten_telling = r'\margintext{' + ".../"+str(max_difficulty)+'}'
    section_title_string = r'Korte kennisvragen over $\mathbb{Z}$ of $\mathbb{Q}$ ('+ '*' * ceil(log(max_difficulty)) +')'
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(punten_telling))
    doc.append(NoEscape(r"""
    Beantwoord de volgende vragen onmiddellijk. Ze komen uit een vaste verzameling vragen en zullen dus terugkeren. Tussenstappen of lange antwoorden zijn meestal niet nodig.
    \begin{multicols}{2}
    \begin{enumerate}
    """))
    problems_frame = pandas.read_csv("problem_database.csv", 
                            sep=";",             
                            dtype={"difficulty" : int, "question" : str, "natural_question": str}
                            ) 
    problems_to_ask = problems_frame[problems_frame.difficulty < max_difficulty].sample(max_number_of_exercises)
    # ask given problems
    derivsep = r"="
    for _, row in problems_to_ask.iterrows():
        latex_question_math = '$'+row['question']+'$'
        latex_question_difficulty = row['difficulty']
        latex_question_natural_question = str(row['natural_question'])
        latex_question_full = r'\item ' + latex_question_natural_question + latex_question_math + r'\derivblank{' + str(latex_question_difficulty) +'}{' + derivsep + "}"
        print(latex_question_full)
        doc.append(NoEscape(latex_question_full)) #uncomment for standard questions
    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))

def add_long_division(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    doc.append(NoEscape(r"""
     Bereken de deling: \\
    \opdiv[resultstyle=\gobble,remainderstyle=\gobble,maxdivstep=5,dividendbridge]
    """))
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

def add_substraction(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    doc.append(NoEscape(r"""
     Bereken de aftrekking: \\
    \opsub[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))


def add_addition(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r"""
     Bereken de optelling: \\
    \opadd[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

# add_long_division(4)

def add_multiplication(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'Bereken het product '+'$'+str(dn) + r'\cdot' + str(d)+'$'))
    doc.append(NoEscape(r"""   
    \opmul[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholde]
    """))
    
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

#add_multiplication(5)

def add_simple_arithmetic_exercises(digits,max_number_of_exercises):
    punten_telling = r'\hfill' + ".../"+str(max_number_of_exercises)
    section_title_string = r'Fundamentele bewerkingen in $\mathbb{N}$ ('+ '*' * ceil(log(digits)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Bereken de volgende operaties volgens de kolommethode of de Euclidische deling (eigenlijk de Franse lange deling).
    \begin{itemize}
    \item Werk van boven naar onder bij alle bewerkingen.
    \item Schrijf alle tussenstappen op de juiste plaats op. 
    \item Werk bij deling van links naar rechts. Bij vermenigvuldiging, aftrekken en optellen bewerk je te cijfers van rechts naar links.
    \end{itemize}

    \begin{multicols}{2}
    \begin{enumerate}
    """))
    for i in range(max_number_of_exercises):
        doc.append(NoEscape(r"""
        \item \begin{center}
        """))
        #f = random.choice([add_multiplication, add_long_division, add_substraction,add_addition])
        f = random.choice([add_multiplication, add_long_division, add_substraction])

        f(digits)
        doc.append(NoEscape(r"""
        \end{center}
        """))
    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def recurse_factors(previous_total_product,max_total_product, even_powers=False):
    a = random.choice([-5,-4,-3,-2,-1,1,2,3,4,5])
    if even_powers: b = 2*random.randint(1,2)
    else: b = random.randint(1,4)
    new_product = max_total_product
    tries = 0
    while abs(new_product) > max_total_product/2 and tries < 5:
        a = random.randint(2,20)
        if even_powers: b = 2*random.randint(1,2)
        else: b = random.randint(1,4)
        new_power = a ** b
        new_product = previous_total_product *  new_power 
        tries +=1
    if abs(new_product) < max_total_product:
        #print('adding factor to ', new_product)
        return recurse_factors(new_product,max_total_product)
    else:
        return previous_total_product


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


def add_exercises(full_qas, with_answers):
    
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
            doc.append(NoEscape(r'\derivblank{' + str(2) +'}{'+derivsep+r'} \end{minipage} \\'))
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

def generate_Z_arithm_questions(difficulty, number):
    def question_Z_arithm_generator(difficulty):
        hints = []
        ops = [negate_op, sqrt_op,plus_op,mul_op,power_op,pythagorean_op, div_op]
        main_question = str(stackOperators(2,difficulty,ops,[]))
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

def generate_Q_sum_questions(difficulty, number):
    def generate_fraction_add(difficulty):
        max_nominator = max(10,10**(difficulty))
        terms = random.randint(2,3)
        for i in range(0,terms):
            # this is such that there is always a common factor in at least one of the terms so that students have to learn to simplify first (no minus signs yet)
            common_factor = random.choice([*range(1,5)])
            signnom = random.choice([-1,1])
            nominator = signnom*recurse_factors(common_factor, max_nominator, even_powers=False)
            signden = random.choice([-1,1])
            denominator = signden*recurse_factors(common_factor, max_nominator, even_powers=False)
            fraction = PrefixBinaryWithCurlyBrackets(Number(nominator),r'\frac', Number(denominator))
            if i == 0:
                fraction_sum = fraction
            else : 
                fraction_sum = MixfixWithoutCurlyBrackets(fraction_sum,'+', fraction)
        hints = []
        if terms > 2:
            hints.append('\\ (zet eerst alle breuken op dezelfde noemer)')
        return([str(fraction_sum),hints])

    title = r"Optellen van breuken in Q"
    advice = r"""
    Vereenvoudig de termen (gebruik indien nodig een factorizatietabel), maak ze gelijknamig en tel ze op.
    """
    imperative = "Tel op"
    hinter = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises( generate_fraction_add,difficulty,number, title, advice, imperative,hinter,solver)
    return(full_problems)


def generate_lcm_questions(difficulty, number):
    def generate_lcm_question(difficulty):
        max_total_product = max(10,10**(difficulty+1))
        product1 = recurse_factors(1, max_total_product, even_powers=False)
        product2 = recurse_factors(1, max_total_product, even_powers=False)
        lcm_expr = PrefixUnaryWithCurvyBrackets(r'\lcm', MixfixWithoutCurlyBrackets(Number(product1),r', ',Number(product2)))
        subquestion1 = str(Number(product1))
        subquestion2 = str(Number(product2))
        output = [r''+str(lcm_expr), [subquestion1, subquestion2]]
        return output
    def render_factorize_hint(product):
        rows = ceil(log2(len(product)))+2
        return(r'\emptyrows{' + str(rows) + '}{'+str(product)+'}')
    title = r"Kleinst gemeen veelvoud in N"
    advice = r"""
    Factorizeer beide getallen en bepaal kleinst gemeenschappelijk veelvoud. Probeer te delen door priemgetallen, van klein naar groot en herhaal indien mogelijk: $2, 3, 5, 7,11,13,17,19, ...$. 
    """
    imperative = "Bereken"
    def solver(expr): 
        return(sympy.simplify(expr))
    full_problems = generate_exercises(generate_lcm_question,difficulty,number, title, advice, imperative, render_factorize_hint,solver)
    return(full_problems)

class Expression:
    pass

class Number(Expression):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return str(self.num)

class MixfixWithCurlyBrackets(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return "{"+str(self.left) +"}"+ self.op + "{" + str(self.right) +"}"


class MixfixWithoutCurlyBrackets(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return str(self.left) + self.op + str(self.right) 


class PrefixBinaryWithCurlyBrackets(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return  self.op +  "{"+ str(self.left) + "}" +"{"  + str(self.right) + "}"

class ParenthesizedExpression(Expression):
    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return r"\left(" + str(self.exp) + r'\right)'

class PrefixUnaryWithCurlyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + "{" + str(self.exp) + "}"

class PrefixUnaryWithoutCurlyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + str(self.exp)

class PostfixUnaryWithoutCurlyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return str(self.exp) +  self.op


class PrefixUnaryWithCurvyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + r'\left(' + str(self.exp) + r'\right)'
        #return self.op + r'(' + str(self.exp) + r')'

class MathOp:
    def __init__(self,name, li,pr,sp,ex,ass):
        self.name =name
        self.li = li # probability as function of parent number in tree
        self.pr = pr # precedence
        self.sp = sp # function of parent number to generate leaves or operand numbers
        self.ex = ex # function of leaves expressions to format full operator
        self.ass = ass # in case of n-ary operators, visually separates arguments?
    def __str__(self):
        return "precedence: " + str(self.pr) + ", weight: " + str(self.li)


function_precedence = 5

identity_op = MathOp("id", lambda n : 1/10, function_precedence, lambda n : [n], lambda le : PrefixUnaryWithoutCurlyBrackets("", le[0]),True)


def li_neg(n):
    if n > 0:
        l = 1/6
    else:
        l = 1/10
    return(l)

neg_print = lambda le : PrefixUnaryWithoutCurlyBrackets("-",le[0])
negate_op = MathOp("neg", li_neg, 3,lambda n : [-n] , neg_print ,True)

def li_root(current_integer): 
    li = 2/(5*(len(str(current_integer))*(current_integer<=20)+1))
    return(li)



sqrt_op = MathOp("sqrt", li_root, function_precedence, lambda x : [x**2], lambda le : PrefixUnaryWithCurlyBrackets(r'\sqrt',le[0]),True)


def li_pythagorean(current_integer):
    factorization = factorint(int(current_integer))
    primes = list(factorization.keys())
    hypotenuses = [5, 13, 61, 181, 421]
    if len(primes) == 1 and all(power == 2 for power in factorization.values()) and  primes[0] in hypotenuses:
        pythagorean = True
    else:
        pythagorean  = False
    #print("Sqrt prob is ", str(li))
    return(pythagorean*2*(current_integer > 0))

def decompose_pythagorean(current_integer):
    if current_integer == 5**2:
        return([3,2,4,2])
    elif current_integer == 13 ** 2:
        return([5,2,12,2])
    elif current_integer == 61**2:
        return([11,2,60,2])
    else: 
        return([0,0,0,0])

def print_pythagorean(le):
    expr = MixfixWithoutCurlyBrackets(MixfixWithCurlyBrackets(le[0], '^', le[1]), "+", MixfixWithCurlyBrackets(le[2], '^', le[3]))
    return(expr)

pythagorean_op= MathOp("pyth", li_pythagorean, 5,decompose_pythagorean, print_pythagorean, False)



def li_power(current_integer):
    factorization = factorint(int(current_integer))
    unique_factors = list(set(list(factorization.keys())))
    if len(unique_factors) == 1 and list(factorization.values())[0] > 1:
        perfect_power = True
    else:
        perfect_power = False
    #n = len(str(current_integer))
    
    return(2*(current_integer>=0)*int(perfect_power))

def decompose_power(current_integer):
    factorization = factorint(int(current_integer))
    base = list(factorization.keys())[0]
    power = factorization[base]
    return([base, power])
    # (MixfixWithCurlyBrackets(base, operator, power))

power_op = MathOp("power", li_power, 2, decompose_power, lambda le : (MixfixWithCurlyBrackets(le[0], r'^', le[1]) ), True)

def smooth_number(max_digits):
    max10 = 10**(max_digits-1)
    p2 = 2**random.randint(0,int(log(max10, 2)))
    p3 = 3**random.randint(0,int(log(max10, 3)))
    p5 = 5**random.randint(0,int(log(max10, 5)))
    #p7 = 7**random.randint(0,int(log(max10, 7)))
    p7 =1
    return(p2*p3*p5*p7)

def likelihood_minus(ci):
    return((1/4)*len(str(ci)))



def minus_decompose(current_integer):
     difference = random.randint(-current_integer-10, current_integer+10)
     #smooth_number(int(log10(floor(abs(current_integer)+1))+1))
     term_1 = current_integer+difference
     term_2 = difference
     return([term_1,term_2])


minus_op = MathOp("minus", likelihood_minus, 4, minus_decompose, lambda le  : MixfixWithoutCurlyBrackets(le[0], "-", le[1]), False)


def plus_decompose(current_integer):
    m = abs(int(current_integer))
    term1_num = random.randint(-m,m)
    term2_num = floor(current_integer - term1_num)
    return([term1_num,term2_num])

plus_op = MathOp("plus", lambda n : (1/4)*len(str(n)), 4, plus_decompose, lambda le  : MixfixWithoutCurlyBrackets(le[0], "+", le[1]), True)




def frac_decompose(current_integer):
    extra_factor = random.randint(2,10)    
    multiple = extra_factor*current_integer
    if multiple/extra_factor != current_integer:
        print("Fraction problem.")
    return([multiple,extra_factor])

frac_op = MathOp("fraction", lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: PrefixBinaryWithCurlyBrackets(le[0], r'\frac',le[1]),False)

div_op = MathOp("division", lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: MixfixWithoutCurlyBrackets(le[0], r':',le[1]), False)

def mul_decompose(current_integer):
    a = abs(current_integer)
    sign = current_integer/a
    factorization = factorint(int(a))
    factors = list(factorization.keys())
    n_factors = ceil(len(factors)/2)
    factor1_num = max(1,prod(random.choices(population=factors,k=n_factors)))
    factor2_num = a / factor1_num 
    return([int(sign*factor1_num),int(factor2_num)])


def mul_likelihood(n):
    l = (3/5)*len(str(n))*(n!=0)*(not sympy.isprime(n))
    return(l)

mul_op=MathOp("mult",mul_likelihood, 3, mul_decompose, lambda le : MixfixWithoutCurlyBrackets(le[0], r' \cdot ', le[1]),True)

linear_op = MathOp("unknown x", lambda n : (2/len(str(n))), 2, lambda n : [n], lambda le :  PrefixUnaryWithoutCurlyBrackets(r' x\cdot  ', le[0]), True)


parenthesis_op = MathOp("brackets", lambda n : 1, 0, lambda n : [n], lambda le : PrefixUnaryWithCurvyBrackets("",le[0]), True)


def is_binary_op(op):
    return(len(op.sp(10))>1)

def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]


def print_tree_simple(root):
    for pre, _, node in RenderTree(root):
        print("%s%s (precedence %s) argument: %s" % (pre, node.operator.name, node.operator.pr, node.number))

def extend_tree(op,current_leaf):
    current_integer = current_leaf.number
    children_numbers = op.sp(current_integer)
    #print("Splitting up "+str(current_integer)+" with operator "+str(op.name)+" into "+ str(op.sp(current_integer)))
    current_leaf.render = op.ex
    current_leaf.children = list(map(lambda n : Node(str(n), parent=current_leaf, number = n,render=lambda n : Number(n), operator=op),children_numbers))
    first_child = current_leaf.children[0]
    return(first_child)

def is_right_argument(child_node):
    return(leftsibling(child_node) != None) 

def compute_solution_number(max_digits):
    max10 = max(20, 10**(max_digits-1))
    solution_number = random.randint(-max10,max10)
    return(solution_number)

def arithmetic_tree(max_height, max_digits, operators, single_use_operators):
    print("==================\nGenerating arithmetic expression...")
    solution_number = compute_solution_number(max_digits)
    print("Solution should be "+ str(solution_number))
    root = Node(str(solution_number), parent=None, number=solution_number,operator=identity_op)
    #max_n_operators = len(single_use_operators)+int(len(operators))
    single_use_used = 0
    operator_list = []
    for i in range(max_height):
        r = random.random()
        if single_use_used < len(single_use_operators) and r < 0.8:
            new_op = single_use_operators[single_use_used]
            operator_list.append(new_op)
            single_use_used = single_use_used + 1
        else:
            operator_list.append(random.choices(operators)[0])
    for op in operator_list: 
        leaf_weights = list(map((lambda leaf : op.li(leaf.number)),list(root.leaves)))
        current_leaf =  random.choices(population=root.leaves, weights=leaf_weights)[0]
        ## it is possible that this leaf is actually not appropriate,
        if current_leaf.number < 0:
            # we have to turn it in a negation operator
            current_leaf = extend_tree(negate_op, current_leaf)
        if not current_leaf.is_root:
            parent_op = current_leaf.operator
            non_associativity =  (is_binary_op(parent_op) and is_binary_op(op) and is_right_argument(current_leaf) and (not parent_op.ass) and (op.pr == parent_op.pr))
            precendence_problem = (is_binary_op(op) and parent_op.pr < op.pr)
            put_brackets_around_leaf =  precendence_problem or non_associativity  and parent_op != identity_op and parent_op != parenthesis_op

            print("Parent operator: "+str(parent_op.name)+", current number: "+str(current_leaf.number)+", new operator: "+str(op.name)+", is guarded with  brackets: "+str(put_brackets_around_leaf))

            if put_brackets_around_leaf:
                
                current_leaf = extend_tree(parenthesis_op, current_leaf)

        if op.li(current_leaf.number) > 0:
            extend_tree(op, current_leaf)
    print_tree_simple(root)
    return(root)

def test_division():
    arithmetic_tree(3, 2, [div_op], [power_op])


def test_minus_neg():
    arithmetic_tree(3, 2, [minus_op, negate_op], [plus_op])
def render_tree(node):
    if node.is_leaf:
        return(node.render(node.number))
    else:
        return(node.render(list(map(render_tree, node.children))))

def stackOperators(max_height,max_digits, operators,single_use_operators):

    root = arithmetic_tree(max_height, max_digits, operators, single_use_operators)
    latex_math_expr = render_tree(root)
    print("Generated expression: "+ str(latex_math_expr))
    actual_solution = N(latex_string_to_sympy(str(latex_math_expr)))
    solution_number = compute_solution_number(max_digits)
    if actual_solution != solution_number:
        print("Actual solution "+str(actual_solution)+"is not equal to "+str(solution_number))
    return(latex_math_expr )      
            


def question_Q_arithm_generator2(difficulty):
        hints = []
        ops = [minus_op,identity_op, negate_op, sqrt_op,plus_op,frac_op,mul_op,power_op,pythagorean_op,div_op ]
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
    full_problems = generate_exercises( question_Q_arithm_generator2,difficulty,number, title, advice, imperative,hint_renderer,solver)
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

#import random
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

def generate_Z_root_questions(difficulty, number):
    def question_Z_root_generator(difficulty):
        max_radicand = 10**(difficulty+1)
        max_loops = 10
        loops = 0
        found = False
        while loops < max_loops and not found :
            perfect_square = recurse_factors(1,max_radicand, even_powers=True)
            if (max_radicand/20 < perfect_square) and (perfect_square < max_radicand):
                root = str(PrefixUnaryWithCurlyBrackets(r'\sqrt', Number(perfect_square)))
                found = True
            loops += 1
        hints = []
        return([root,hints])

    title = r"Wortels vereenvoudigen in N"
    advice = r"""
    Splits het getal onder de wortel (het radicand) op in kleinere gelijke factoreren. Doe dit door het te factorizeren. Gebruik daarna de eigenschappen van wortels om de wortel te vereenvoudigen in wortels van priemgetallen. Bereken de wortels van priemgetallen met een rekenmachine  of gebruik deze getallen:
    \begin{itemize}
     \item $\sqrt{2} \approx 1,41 ...$
    \item $\sqrt{3} \approx 1,73 ...$
     \item $\sqrt{5} \approx 2,24 ...$
    
     \end{itemize}
    """
    imperative = "Bereken"
    hinter = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises(question_Z_root_generator,difficulty,number, title, advice, imperative,hinter,solver)
    return(full_problems)

def generate_Q_simplify_questions(difficulty, number):
    def question_Q_simplify_generator(difficulty):
        max_nominator = 10**difficulty
        max_loops = 10
        loops = 0
        found = False
        while loops < max_loops and not found:
            common_factor = random.randint(2,20)
            nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
            denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
            max_den_nom = max(nominator,denominator)
            fraction = PrefixBinaryWithCurlyBrackets(Number(nominator),r'\frac', Number(denominator))
            if (max_nominator/20 < max_den_nom) and ( max_den_nom < max_nominator):
                math = fraction
                found = True
            loops += 1
        hints = []
        return([str(math),hints])

    title = r"Vereenvoudigen in $\mathbb{Q}$"
    advice = r"""
    Ontbind de teller en noemer en schrap de gemeenschappelijke factoren. 
    """
    imperative = "Vereenvoudig"
    hinter = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises(question_Q_simplify_generator,difficulty,number, title, advice, imperative,hinter,solver)
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

generate_pdf_with_questions([generate_Q_arithm_questions(6,6), generate_Z_unknown_questions(3,4),generate_proportions(3,4)])


def generate_pdf_with_questions(latex_section_list):
    doc.append(NoEscape(r"\part{Vragen}"))
    for full_section in latex_section_list:
        add_exercises(full_section,False)
    # doc.append(NoEscape(r"""
    # \section{Omgekeerd of recht evenredig}

    # \begin{enumerate}
    # \item De bakker spuit slagroomtoefjes op de rand van de taart.  Hoe groter de taart, hoe \underline{\hspace{2cm}}  slagroomtoefjes. Omgekeerd of recht evenredig?
    # \item Ik ga de muur van mijn klaslokaal verven.  Hoe groter het lokaal, hoe \underline{\hspace{2cm}} verf ik nodig heb. Omgekeerd of recht evenredig?
    # \item Ik wil de muur van mijn badkamer betegelen.  Hoe groter de tegels die ik gebruik, hoe \underline{\hspace{2cm}} tegels ik nodig heb. Omgekeerd of recht evenredig?
    # \item We gaan op uitstap met de trein.  Hoe verder we gaan hoe \underline{\hspace{2cm}} een treinticket kost. Omgekeerd of recht evenredig?
    # \end{enumerate}
    # """))


    # doc.append(NoEscape(r"""
    # \section{Vraagstukken over evenredigheden}

    # \begin{enumerate}

    # \item Een huis, dat in werkelijkheid 12 m breed is, meet op een plan slechts 8 cm. Hoe breed is de straat in werkelijkheid als ze op het plan 4,2 cm breed is?
    # \vspace{3cm}

    # \item Als 7 identieke DVD-spelers 2240 EUR kosten, hoeveel kosten dan 17 van die DVD-spelers?
    # \vspace{3cm}

    # \item 36 leerlingen betaalden elk 27,30 EUR voor een studiereis naar Brussel. Als de bus volzet was geweest, had elke leerling 9,10 EUR minder moeten betalen? Hoeveel leerlingen konden mee in die bus?
    # \vspace{3cm}

    # \item In een fabriek wordt 40 uur per week gewerkt met 57 machines. Hoeveel machines moeten gebruikt worden als er slechts 38 uur per week wordt gewerkt en men de productie op hetzelfde peil wil houden?
    # \vspace{3cm}

    # \item Een tank kan door 8 pompen leeggepompt worden in 42 minuten. Nu zijn echter 2 pompen defect geraakt. Hoeveel tijd hebben de overblijvende pompen voor dit werk nodig?
    # \vspace{3cm}


    # \end{enumerate}

    # """))


    # doc.append(NoEscape(r"""
    # \section{Vraagstukken over percentages}

    # \begin{enumerate}

    # \item Bereken 75 \% van 400.
    # \vspace{2cm}

    # \item  100 \% van 60 is x. Wat is x? 
    # \vspace{2cm}
    # \item Wat is 50 \% van 800?
    # \vspace{2cm}
    # \item 20 \% van x is 40. Zoek x.
    # \vspace{2cm}

    # \item Per dag loggen 4.960.000 Belgen in op Facebook. In totaal zijn er 6.200.000 Belgen actief op Facebook. Hoeveel procent van de Belgen die op Facebook actief 
    # zijn loggen dagelijks in op Facebook? (Rond af op een heel procent.) Noteer je berekening.
    # \vspace{3cm}

    # \item Van de 91 minuten die de gemiddelde Belg dagelijks op internet surft, besteedt hij 20 minuten op 
    # Facebook. Hoeveel procent van de tijd surft een gemiddelde Belg naar Facebook, als hij op het 
    # internet zit? (Rond af op een heel procent.) Noteer je berekening.
    # \vspace{3cm}




    # \end{enumerate}

    # """))


    doc.append(NoEscape(r"\part{Antwoorden}"))
    for full_section in assignmentStructure:
        add_exercises(full_section,True)
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

    doc.generate_tex('assignment')
    doc.generate_pdf('assignment', silent=True)
