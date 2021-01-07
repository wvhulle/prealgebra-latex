import random,pandas,sympy
from functools import reduce
from math import sqrt,ceil,log, log2, log10, floor, ceil, log
from sympy import N
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import standard_transformations,implicit_multiplication_application
from pylatex import Command,Document, Package, NoEscape, Section
from pylatex.utils import italic, escape_latex
from random import random, randint, choices,choice
from sympy.ntheory import factorint

from numpy import prod
import collections
import regex

doc = Document()
doc.documentclass = Command(
        'documentclass',
        options=['dutch','course','headersection','theoremsection','cleardoublepage','twoside'],
        arguments=['lecture'],
    )


# on ubuntu sudo apt-cache search lastpage
# 

doc.preamble.append(NoEscape(r"""



\title{Herhalingsoefeningen}
\subtitle{Oefeningen over basiswiskunde}
\shorttitle{BASIS}
\author{Willem Vanhulle}
\email{willemvanhulle [at] gmail.com}
\date{16}{11}{2020}
\dateend{12}{01}{2021} 
\conference{Lessenreeks aan CVO Volt}
\place{Leuven, Belgi\"e}
\flag{Geschreven op \today}
\attn{Opdrachten en testen voor studenten.}
 """))


doc.append(NoEscape(r"""

%\maketitle

%Signature \underline{\hspace{3cm}}
	\vspace{3em}
\textbf{Naam student:} \hrulefill\\

%De moeilijkheidsgraad van elke oefening is aangegeven met een aantal ``*''-en. Schrijf berekeningen op als volgt:
%\noindent
%    \begin{align*}
   %     &= \hspace{0.2cm}\underline{\mystrut \text{Voorlaatste stap in berekening}  }  \\
     %   &=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %symbolisch antwoord} }  $\approx$ \underline{ \text{Decimale %benadering tot 3 cijfers} }}
      %&=  \hspace{0.2cm}  \mybox{\underline{\text{Simpelst mogelijke %antwoord} } }
    %\end{align*}
"""))




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
        print("Stripping fraction from: ", stripped_expr)
        stripped_expr
        stripped_expr = regex.sub(r'\\frac\{((?>[^{}]+|\{(?1)\})*)\}\{((?>[^{}]+|\{(?1)\})*)\}', r'(\1)/(\2)', stripped_expr)
    
    stripped_expr = stripped_expr.replace('$','')
    stripped_expr = stripped_expr.replace('\\','')

    stripped_expr = stripped_expr.replace(':','/')
    stripped_expr = stripped_expr.replace('{','(')
    stripped_expr = stripped_expr.replace('}',')')
    stripped_expr = stripped_expr.replace('^','**')
    print('Parsing unlatexified:    ', stripped_expr)
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
    dn = abs(randint(10**(length-2),10**length))
    d = abs(randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

def add_substraction(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    doc.append(NoEscape(r"""
     Bereken de aftrekking: \\
    \opsub[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    dn = abs(randint(10**(length-2),10**length))
    d = abs(randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))


def add_addition(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    dn = abs(randint(10**(length-2),10**length))
    d = abs(randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r"""
     Bereken de optelling: \\
    \opadd[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

# add_long_division(4)

def add_multiplication(length):
    # \opdiv[decimalsepsymbol={,},displayintermediary=all,resultstyle=\placeholder,carrystyle=\color{white},voperation=top]
    dn = abs(randint(10**(length-2),10**length))
    d = abs(randint(10**(length-3),10**(length-2)))
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
        #f = choice([add_multiplication, add_long_division, add_substraction,add_addition])
        f = choice([add_multiplication, add_long_division, add_substraction])

        f(digits)
        doc.append(NoEscape(r"""
        \end{center}
        """))
    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def recurse_factors(previous_total_product,max_total_product, even_powers=False):
    a = choice([-5,-4,-3,-2,-1,1,2,3,4,5])
    if even_powers: b = 2*randint(1,2)
    else: b = randint(1,4)
    new_product = max_total_product
    tries = 0
    while abs(new_product) > max_total_product/2 and tries < 5:
        a = randint(2,20)
        if even_powers: b = 2*randint(1,2)
        else: b = randint(1,4)
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
        latex_question_math = '$' + rand_expr + '$'
        latex_question_math_parsed = latex_string_to_sympy(rand_expr)
        sympy_string = str(latex_question_math_parsed)
        reduced_latex_question = sympy.latex(latex_question_math_parsed)
        solutions = solver(latex_question_math_parsed)
        latex_solution = str(sympy.latex(solutions))
        
        ## check length to exclude weird questions
        
        
        if len(sympy_string)>2*difficulty and len(sympy_string) < 7 *difficulty:
            
            # question might fit on a line and is not just a number
            reduce_ratio = len(latex_solution) / len(reduced_latex_question)
            ideal_ratio = 0.5 #* (1/(difficulty-1))
            
           
            if abs(reduce_ratio  - ideal_ratio) < 1:
                found = True
                latex_question_difficulty = min(max(difficulty-1,1),4) 
                latex_answer_question_math = '$' + latex_solution + '$'
                #print(latex_answer_question_math)
                if len(solutions) == 1:
                   latex_answer_question_math_eval = '$' + sympy.latex(N(solutions[0],3)) + '$'
                else:
                    latex_answer_question_math_eval = "$" + str(solutions) +"$"
            else:
                 print('Reduction ratio skewed: ', str(reduce_ratio), 'with ideal ', str(ideal_ratio))
        else: 
            print('Parsing failed: Raw ',  rand_expr, '-> Sympy ', sympy_string, ' ->  Sympy Latex ' , reduced_latex_question, ' -> Solved Latex ',  latex_solution)



    #         mean_ideal_string_length = 5*(difficulty) +2
    #         if abs(len(str(latex_question_math_parsed))- mean_ideal_string_length) < 10:
    #             print('The generated question ',str(latex_question_math_parsed), ' has length ', len(str(latex_question_math_parsed)), ' at difficulty ', str(difficulty), ' but i expected more ', mean_ideal_string_length)
    #             mean_ideal_solution_length = 5
    #             if  abs(len(latex_solution)-mean_ideal_solution_length) < 20:
    # #print('The generated question ', str(latex_question_math_parsed), ' has length ', len(str(latex_question_math_parsed)), ' but i expected more like ', mean_ideal_string_length)
    # #if  abs(len(str(latex_question_math_parsed)) - mean_ideal_string_length) < 3*difficulty:
    #                 found = True
    #                 latex_question_difficulty = min(max(difficulty-1,1),4) 
    #                 latex_answer_question_math = '$' + latex_solution + '$'
    #                 #print(latex_answer_question_math)
    #                 latex_answer_question_math_eval = '$' + sympy.latex(N(latex_question_math_parsed.simplify(),3)) + '$'

        loop += 1

    if not loop < max_loop:
        print('Generated too many long or short questions with generator ',  str(question_generator))
    return([latex_question_difficulty, [latex_question_math, hints],latex_answer_question_math, latex_answer_question_math_eval])




def generate_exercises(question_generator,max_depth,max_number_of_exercises, title, advice, imperative,render_factorize_hint,solver):
    # Generate questions
    qas = []
    for i in range(max_number_of_exercises):
        difficulty = randint(ceil(max_depth/2),max_depth)
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
        doc.append(NoEscape(r'\item ' + imperative + r': '))
        doc.append(NoEscape(initial_question + r'. '))
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
            doc.append(NoEscape(r'\derivblank{' + str(stars -1) +'}{'+derivsep+'}'))
        else:
            doc.append(NoEscape(r'\derivblanksolution{' + qa[2] + '}{' + qa[3] + '}'))
    if with_answers:
        doc.append(NoEscape(r"""
        \end{enumerate}
        """))
        doc.append(NoEscape(r'\end{multicols}'))
    else: 
        doc.append(NoEscape(r"""
        \end{enumerate}
        """))

# TODO: question types: simplify, factorize/expand

def generate_Z_arithm_questions(difficulty, number):
    def question_Z_arithm_generator(difficulty):
        hints = []
        ops = [negate_op, sqrt_op,plus_op,mul_op,power_op,pythagorean_op, div_op]
        main_question = str(randomExpression2(difficulty,ops,[]))
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
        terms = randint(2,3)
        for i in range(0,terms):
            # this is such that there is always a common factor in at least one of the terms so that students have to learn to simplify first (no minus signs yet)
            common_factor = choice([*range(1,5)])
            signnom = choice([-1,1])
            nominator = signnom*recurse_factors(common_factor, max_nominator, even_powers=False)
            signden = choice([-1,1])
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
        lcm_expr = UnaryWithCurvyBrackets(r'\lcm', MixfixWithoutCurlyBrackets(Number(product1),r', ',Number(product2)))
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

class UnaryExpression(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + "{" + str(self.exp) + "}"

class UnaryWithoutCurlyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + str(self.exp)

class UnaryWithCurvyBrackets(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + r'\left(' + str(self.exp) + r'\right)'
        #return self.op + r'(' + str(self.exp) + r')'

class MathOp:
    def __init__(self,li,pr,sp,ex,ass):
        self.li = li # probability as function of parent number in tree
        self.pr = pr # precedence
        self.sp = sp # function of parent number to generate leaves or operand numbers
        self.ex = ex # function of leaves expressions to format full operator
        self.ass = ass # associative relative to parent
    def __str__(self):
        return "precedence: " + str(self.pr) + ", weight: " + str(self.li)

identity_op = MathOp(lambda n : 0, 5, lambda n : [n], lambda le : UnaryWithoutCurlyBrackets("", next(le)),True)


def li_neg(n):
    if n > 0:
        l = 1/3
    else:
        l = 1/8
    return(l)


negate_op = MathOp(li_neg, 0,lambda n : [-n] , lambda le : UnaryWithoutCurlyBrackets("-",next(le)),True)

def li_root(current_integer): 
    factorization = factorint(int(current_integer))
    n = len(str(current_integer))
   # print(factorization.values())
    if all(power % 2 == 0 for power in factorization.values()):
        powers_even = True
    else:
        powers_even = False
    li = 4*int(powers_even)*1/(n)
    #print("Sqrt prob is ", str(li))
    return(li)

sqrt_op = MathOp(li_root, 2, lambda x : [int(sqrt(x)),2], lambda le : UnaryExpression(r'\sqrt',MixfixWithCurlyBrackets(next(le), r"^",next(le))),False)


def li_pythagorean(current_integer):
    factorization = factorint(int(current_integer))
    primes = list(factorization.keys())
    hypotenuses = [5, 13, 61, 181, 421]
    if len(primes) == 1 and all(power == 2 for power in factorization.values()) and  primes[0] in hypotenuses:
        pythagorean = True
    else:
        pythagorean  = False
    li = int(pythagorean )
    #print("Sqrt prob is ", str(li))
    return(li*10)

def decompose_pythagorean(current_integer):
    if current_integer == 5**2:
        return([3,2,4,2])
    elif current_integer == 13 ** 2:
        return([5,2,12,2])
    elif current_integer == 61**2:
        return([11,2,60,2])
    else: 
        return([0,0,0,0])

def print_pythagorean(leaves):
    expr = MixfixWithoutCurlyBrackets(MixfixWithCurlyBrackets(next(leaves), '^', next(leaves)), "+", MixfixWithCurlyBrackets(next(leaves), '^', next(leaves)))
    return(expr)

pythagorean_op= MathOp(li_pythagorean, 1,decompose_pythagorean, print_pythagorean, False)

def li_power(current_integer):
    factorization = factorint(int(current_integer))
    unique_factors = list(set(list(factorization.keys())))
    if len(unique_factors) == 1 and list(factorization.values())[0] > 1:
        perfect_power = True
    else:
        perfect_power = False
    n = len(str(current_integer))
    return(10*int(perfect_power))

def decompose_power(current_integer):
    factorization = factorint(int(current_integer))
    base = list(factorization.keys())[0]
    power = factorization[base]
    return([base, power])
    # (MixfixWithCurlyBrackets(base, operator, power))

power_op = MathOp(li_power, 2, decompose_power, lambda le : (MixfixWithCurlyBrackets(next(le), r'^', next(le)) ), False)

def smooth_number(max_digits):
    max10 = 10**(max_digits-1)
    p2 = 2**randint(0,int(log(max10, 2)))
    p3 = 3**randint(0,int(log(max10, 3)))
    p5 = 5**randint(0,int(log(max10, 5)))
    p7 = 7**randint(0,int(log(max10, 7)))
    return(p2*p3*p5*p7)


def minus_decompose(current_integer):
     term1_num = smooth_number(int(log10(floor(abs(current_integer)+1))+1))
     term2_num = floor(current_integer - term1_num)
     return([term1_num,term2_num])


minus_op = MathOp(lambda n : (1/5)*len(str(n)), 4, minus_decompose, lambda le  : MixfixWithoutCurlyBrackets(next(le), "+", next(le)), True)

def plus_decompose(current_integer):
    m = abs(int(current_integer))
    term1_num = randint(-m,m)
    term2_num = floor(current_integer - term1_num)
    return([term1_num,term2_num])

plus_op = MathOp(lambda n : (1/6)*len(str(n)), 4, plus_decompose, lambda le  : MixfixWithoutCurlyBrackets(next(le), "-", next(le)), True)




def frac_decompose(current_integer):
    extra_factor = randint(2,10)    
    multiple = extra_factor*current_integer
    return([multiple,extra_factor])

frac_op = MathOp(lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: PrefixBinaryWithCurlyBrackets(next(le), r'\frac',next(le)),False)

div_op = MathOp(lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: MixfixWithoutCurlyBrackets(next(le), r':',next(le)), False)

def mul_decompose(current_integer):
    factorization = factorint(int(current_integer))
    factors = list(factorization.keys())
    n_factors = ceil(len(factors)/2)
    factor1_num = prod(choices(population=factors,k=n_factors))
    factor2_num = floor(current_integer / factor1_num   )
    return([factor1_num,factor2_num])

mul_op=MathOp(lambda n : (2/5)*len(str(n)), 3, mul_decompose, lambda le : MixfixWithoutCurlyBrackets(next(le), r'\cdot', next(le)),True)

linear_op = MathOp(lambda n : (1/len(str(n))), 2, lambda n : [n], lambda le :  UnaryWithoutCurlyBrackets(r' x \cdot', next(le)), True)

def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]


def randomExpression2(max_digits, operators,disposable_operators):
   # max10 = 10**(max_digits-1)
   # smooth_n = smooth_number(max_digits)
    #solution_number = smooth_number(max_digits)
    solution_number =  smooth_number(max_digits)
    max_height = max_digits
 ##   disposable_mask  = [1] * len(disposable_operators)

    def randomExpression2_rec(current_integer, height,parent_op,mask):
     # print("Current integer: ", str(current_integer))
#print(mask)
        #rem_disp = find_indices(mask, lambda e : e > 0)
        if (height == 0 or abs(current_integer) < 5):
            e = Number(current_integer)
            return(e)
        #elif len(rem_disp) > 0 and : 
        #    new_mask =  [5*b for b in mask]
        #    return(randomExpression2_rec(current_integer, height,parent_op,new_mask))
        else:
            weights = list(map(lambda op : op.li(current_integer),operators))
            disposable_weights = list(map(lambda op : op.li(current_integer),disposable_operators))
            #print("disposable weights" + str(disposable_weights))
            remaining_weights = [a*b for a,b in zip(disposable_weights,mask)]
            #print("remaining weights" + str(remaining_weights))
            op=choices(population=(operators + disposable_operators),weights=weights+remaining_weights,k=1)[0]
            if op in disposable_operators:
                # decrease weight 
                i = disposable_operators.index(op)
                mask[i] = 0
            leaves = map(lambda leaf : randomExpression2_rec(leaf, height-1,op,mask), op.sp(current_integer))
            parenthesis_hints = False
            if parent_op.pr < op.pr:
                # adding brackets so that steps are respected
                return(ParenthesizedExpression(op.ex(leaves)))
            elif (parent_op.pr == op.pr and (not op.ass)) and parenthesis_hints:
                return(ParenthesizedExpression(op.ex(leaves)))
            else:
                return(op.ex(leaves))
            
            return 
    return(randomExpression2_rec(solution_number,max_height, identity_op,[10] * len(disposable_operators)))      
            
    #         #print(factorization)
    #         
    #         #print(unique_factors)
    #         

            
    #         #print("the number ", str(current_integer)," is a  perfect power: ", perfect_power)
    #         #print("the number ", str(current_integer)," has even exponents ", powers_even)
    #         likelihood_plus = 1/2*n
    #         likelihood_div = 1/(n)
    #         likelihood_mul = sqrt(n)
    #         likelihood_fraction = likelihood_div*2
    #         likelihood_power = 3*int(perfect_power)*log2(n)
            


            
    #         operators = ["+",r'\cdot',r'\frac',":",r"^",r"\sqrt"]
    #         weights = [likelihood_plus, likelihood_mul, likelihood_fraction, likelihood_div, likelihood_power, likelihood_root]
    #         print("likelihoods are ", str(weights))
    #         operator = choices(population=operators,weights=weights,k=1)[0]
    #         print("splitting ", current_integer, " up with ", str(operator))
    #         if operator == "+":
    #             term1_num = randint(0,abs(int(current_integer)))
    #             term2_num = floor(current_integer - term1_num)
    #             print("adding ", str(term1_num), " and ", str(term2_num))
    #             term1 = randomExpression2(term1_num, height-1)
    #             term2 = randomExpression2(term2_num, height-1)

    #             return(ParenthesizedExpression(MixfixWithoutCurlyBrackets(term1, operator, term2)))
    #         elif operator == r'\cdot':
    #             factors = list(factorization.keys())
    #             #print("factors of ", str(current_integer), " are ", str(factors))
    #             n_factors = ceil(len(factors)/2)
    #             factor1_num = prod(choices(population=factors,k=n_factors))
    #             factor2_num = floor(current_integer / factor1_num   )
    #             #print("multiplying ", str(factor1_num), " and ", str(factor2_num))
    #             factor1 = randomExpression2(factor1_num, height -1)     
    #             factor2 = randomExpression2(factor2_num, height - 1)
    #             return(ParenthesizedExpression(MixfixWithoutCurlyBrackets(factor1, operator, factor2)))
    #         elif operator == r"\frac":
    #             extra_factor = randint(2,10)
    #             multiple = extra_factor*current_integer
    #             #print("dividing ", str(multiple), " by ", str(extra_factor))
    #             dividend = randomExpression2(multiple, height -1)
    #             divisor = randomExpression2(extra_factor, height - 1)
    #             return(ParenthesizedExpression(PrefixBinaryWithCurlyBrackets(dividend, operator, divisor)))
    #         elif operator == r":":
    #             extra_factor = randint(2,10)
    #             multiple = extra_factor*current_integer
    #             print("dividing ", str(multiple), " by ", str(extra_factor))
    #             dividend = randomExpression2(multiple, height -1)
    #             divisor = randomExpression2(extra_factor, height - 1)
    #             return(ParenthesizedExpression(MixfixWithoutCurlyBrackets(dividend, operator, divisor)))
    #         elif operator == r"^":
    #            
    #         elif operator == r"\sqrt":
    #             print("taking sqrt of ", str(current_integer))
    #             return(UnaryExpression(operator, MixfixWithCurlyBrackets(randomExpression2(int(sqrt(current_integer)),height-1), "^", randomExpression2(2,height-1))))
    
# def randomExpression(prob,maxdepth,previous_was_par=False, in_exp=False, fractions=False):
#     # Throw a dice for choosing whether this is going to be number
#     p = random()
#     next_p = prob + 0.05*(1-prob) # step-wise increase in number probability on each level
#     if p <= prob or maxdepth <= 0:
#         if in_exp == True: # use smaller numbers
#             n_small = randint(0,4) # no negative numbers for easy exponents
#             if n_small < 0:
#                 return ParenthesizedExpression(Number(n_small))
#             else:
#                 return Number(n_small)
#         else:
#             n_big = randint(-10,30)
#             if n_big < 0:
#                 return ParenthesizedExpression(Number(n_big))
#             else:
#                 return Number(n_big)
#     else: 
#         # Throw a dice for choosing an operation
#         b = random()
#         if b < 0.05 and previous_was_par == False:
#             return ParenthesizedExpression(randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
#         elif b < 0.10 and ((not in_exp)): 
#             unop = choice([r"\sqrt"])
#             return UnaryExpression(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
#         elif b < 0.20:
#             # do the difficult binary operations
#             left = randomExpression(next_p ,maxdepth-1,False, True, fractions)
#             op = choice(["^"])
#             right = randomExpression(next_p ,maxdepth-1, False, True, fractions)
#             return MixfixWithCurlyBrackets(left, op, right)
#         elif b < 0.3 and not in_exp:  # negation not in exponent
#             unop = choice(["-"]) # other functions such a sin could be added here
#             return UnaryWithCurvyBrackets(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
#         elif b < 0.8:
#             # easier binary operations
#             left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions)
#             right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions)
#             if not in_exp:
#                 mixop = choice(["+", "-", r"\cdot"])
#             else:
#                 mixop = choice(["+", r"\cdot"]) # no fractional or negative exponents
#             return MixfixWithoutCurlyBrackets(left, mixop, right)
            
#         elif b < 0.99 and fractions and (not in_exp): 
#             left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions)
#             preop = choice([r'\frac'])
#             right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions)
#             return PrefixBinaryWithCurlyBrackets(left, preop, right)
#         else: 
#             return Number(randint(0,3))

def generate_Q_arithm_questions(difficulty, number):
    # def question_Q_arithm_generator(difficulty):
    #     fractions = True
    #     hints = []
    #     main_question = str(randomExpression(0.05,difficulty, True, False, fractions))
    #     #print(main_question)
    #     return([main_question,hints])

    def question_Q_arithm_generator2(difficulty):
        hints = []
        #solution = randint(-(10**(difficulty-2)),10**(difficulty-2))
        #print("=========\nSolution has to be ", solution,":\n   derivation: ...")
        ops = [identity_op, negate_op, sqrt_op,plus_op,frac_op,mul_op,power_op,pythagorean_op,div_op ]
        main_question = str(randomExpression2(difficulty,ops,[]))
        #print(main_question)
        return([main_question,hints])


    title = r"Volgorde van de bewerkingen in Q"
    advice = r"""
    Vereenvoudig de volgende uitdrukkingen zoveel mogelijk in deze volgorde: (1) haakjes, (2) machten en wortels, (3) vermenigvuldiging en deling en (4) optelling en aftrekking.
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    solver = sympy.simplify
    full_problems = generate_exercises( question_Q_arithm_generator2,difficulty+2,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)


def generate_Z_unknown_questions(difficulty, number):
    # def question_Q_arithm_generator(difficulty):
    #     fractions = True
    #     hints = []
    #     main_question = str(randomExpression(0.05,difficulty, True, False, fractions))
    #     #print(main_question)
    #     return([main_question,hints])

    def question_Z_unknown_generator(difficulty):
        hints = []
        #solution = randint(-(10**(difficulty-2)),10**(difficulty-2))
        #print("=========\nSolution has to be ", solution,":\n   derivation: ...")
        ops = [minus_op,identity_op, negate_op,sqrt_op,plus_op,mul_op,div_op,power_op,pythagorean_op ]
        left_eq = str(randomExpression2(2,ops,[]))
        right_eq = str(randomExpression2(2,ops,[linear_op]))
        main_question = left_eq + r'='+right_eq
                #main_question = left_eq + r'='+right_eq
        #print(main_question)
        return([main_question,hints])
    title = r"Vergelijkingen in Z"
    advice = r"""
    Breng alle onbekenden naar het linkerlid
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    def solver(eq):
        return(sympy.solve(eq,sympy.Symbol('x')))
        
    full_problems = generate_exercises( question_Z_unknown_generator,difficulty+2,number, title, advice, imperative,hint_renderer,solver)
    return(full_problems)


def generate_proportions(difficulty, number):
    def question_proportions_generator(difficulty):
        hints = []
        #solution = randint(-(10**(difficulty-2)),10**(difficulty-2))
        #print("=========\nSolution has to be ", solution,":\n   derivation: ...")
        ops = [minus_op,identity_op, negate_op,plus_op,mul_op]
        left_eq = str(randomExpression2(2,ops,[frac_op,linear_op]))
        right_eq = str(randomExpression2(2,ops,[frac_op]))
        main_question = left_eq + r'='+right_eq
                #main_question = left_eq + r'='+right_eq
        #print(main_question)
        return([main_question,hints])
    title = r"Evenredigheden in Z"
    advice = r"""
    Gebruik de hoofdeigenschap van evenredigheden (de kruisregel) en los op naar de onbekende.
    """
    imperative = "Los op"
    hint_renderer = lambda x : x
    def solver(eq):
        return(sympy.solve(eq,sympy.Symbol('x')))
        
    full_problems = generate_exercises( question_proportions_generator,difficulty+2,number, title, advice, imperative,hint_renderer,solver)
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
                root = str(UnaryExpression(r'\sqrt', Number(perfect_square)))
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
            common_factor = randint(2,20)
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
        dn = abs(randint(10**(difficulty),10**difficulty+1))
        d = abs(randint(10**(difficulty-1),10**(difficulty)))
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



# Generate all the questions with answers
full_sections_with_answers = []
#full_sections_with_answers.append(generate_N_division_questions(3,10))
#full_sections_with_answers.append(generate_lcm_questions(2,4))
#full_sections_with_answers.append(generate_Z_root_questions(3,10))
#full_sections_with_answers.append(generate_Z_arithm_questions(3,10))
#full_sections_with_answers.append(generate_Z_arithm_questions(5,4))
#full_sections_with_answers.append(generate_Q_simplify_questions(3,4))
#full_sections_with_answers.append(generate_Q_sum_questions(3,10))
#full_sections_with_answers.append(generate_Z_arithm_questions(3,4))
#full_sections_with_answers.append(generate_Q_arithm_questions(3,4))
#full_sections_with_answers.append(generate_Q_arithm_questions(5,4))

full_sections_with_answers.append(generate_Z_unknown_questions(3,10))
full_sections_with_answers.append(generate_proportions(3,10))


doc.append(NoEscape(r"\part{Vragen}"))

# Not yet automated
#add_simple_arithmetic_exercises(4,10)
#add_simplify_fractions_exercises(3, 10)
#root_questions_with_answers = generate_simplify_root_exercises(2,4)
#add_simplify_root_exercises(root_questions_with_answers, False)


#generate_simplify_root_exercises(4,10)
for full_section in full_sections_with_answers:
    add_exercises(full_section,False)
doc.append(NoEscape(r"\part{Antwoorden}"))
for full_section in full_sections_with_answers:
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
doc.generate_pdf('assignment', silent=False)
