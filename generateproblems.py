import random,pandas,sympy
from functools import reduce
from math import sqrt,ceil,log, log2, log10
from sympy.parsing.sympy_parser import parse_expr
from sympy import *
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import standard_transformations,implicit_multiplication_application
from pylatex import Command,Document, Package, NoEscape, Section
from pylatex.utils import italic, escape_latex
from random import random, randint, choice
import re

# pip install  antlr4-python3-runtime 

#doc = Document()
doc = Document('Test', geometry_options = {"head": "2cm","margin": "2cm","bottom": "3cm"})

doc.documentclass = Command(
        'documentclass',
        options=['12pt', 'portrait', 'a4'],
        arguments=['article'],
    )

doc.packages.append(Package('xcolor'))
doc.packages.append(Package('amsmath'))
doc.packages.append(Package('multicol'))
doc.packages.append(Package('array'))
doc.packages.append(Package('amssymb'))# voor mathbold Z
doc.packages.append(Package('xlop')) # french long division


doc.preamble.append(NoEscape(r"""
% this is the space a student needs to write one digit
\newcommand*{\mystrut}{\phantom{\rule[-0.05\baselineskip]{1.5mm}{1.5\baselineskip}}}
\newcommand*{\mybox}[1]{\framebox{\mystrut #1}}
\newcommand{\placeholder}[1]{\mystrut}% Print -- regardless of the input
\newcommand{\gobble}[1]{}% Print <nothing> regardless of the input


\newcommand{\derivblank}[1]{%
    \noindent
    \begin{align*}
    \xderivblank{#1}%
&=  \hspace{0.2cm}  \mybox{\underline{ \hspace{0.5 \linewidth}}  $\approx$ \underline{\hspace{0.2 \linewidth}}}
    \end{align*}
}
\newcommand\xderivblank[1]{%
\ifnum#1=0 \else
        &= \hspace{0.2cm}\underline{\mystrut\hspace{0.8 \linewidth}}  \\
\xderivblank{\numexpr#1-1}\fi}


\newcommand{\emptyrows}[2]{%
    \noindent
    \begin{center}
    \begin{tabular}{ c|c } 
        #2 &  \mystrut \\\cline{1-1}
        \xemptyrows{#1}%
    \end{tabular}
    \mybox{$#2 = $ \underline{\hspace{0.2 \linewidth}}}
    \end{center}
    
}
\newcommand\xemptyrows[1]{%
\ifnum#1=0 \else
         &  \mystrut  \\
\xemptyrows{\numexpr#1-1}\fi}


\title{Extra oefeningen \\ CVO Heverlee: TKO - AAV}
\author{Leerkracht: Willem Vanhulle \\ Klas: \texttt{LEUT20sBpostWiskBaMaDi}  (2020-2021)}
\date{\today}
                    """))



# \maketitle
doc.append(NoEscape(r"""

\maketitle

%Signature \underline{\hspace{3cm}}
	\vspace{3em}
\textbf{Naam student:} \hrulefill\\


Dit is een automatisch gegenereerde toets. Een rekenmachine is niet nodig. De moeilijkheidsgraad van elke oefening is aangegeven met een aantal ``*''-en. Schrijf berekeningen op als volgt:
\noindent
    \begin{align*}
        &= \hspace{0.2cm}\underline{\mystrut \text{Voorlaatste stap in symbolische berekening}  }  \\
        &=  \hspace{0.2cm}  \mybox{\underline{\text{Kortst mogelijke symbolisch antwoord} }  $\approx$ \underline{ \text{Decimale benadering tot 3 cijfers} }}
    \end{align*}
"""))




class Expression:
    pass

class Number(Expression):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return str(self.num)

class MixfixBinaryExpression(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return "{"+ str(self.left) + "}" + self.op + "{"  + str(self.right) + "}"

class PrefixBinaryExpression(Expression):
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
        return "\left(" + str(self.exp) + r'\right)'

class UnaryExpression(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
        

    def __str__(self):
        return self.op + "{" + str(self.exp) + "}"

class UnaryFunctionExpression(Expression):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp
    def __str__(self):
        return self.op + r'\left(' + str(self.exp) + r'\right)'

def randomExpression(prob,maxdepth,previous_was_par=False, in_exp=False, fractions=False, hard_exponents = False):
    # Throw a dice for choosing whether this is going to be number
    p = random()
    next_p = prob + 0.05*(1-prob) # step-wise increase in number probability on each level
    if p <= prob or maxdepth <= 0:
        if in_exp == True: # use smaller numbers
            if hard_exponents:
                n_small = randint(-4,4)
            else:
                n_small = randint(0,4) # no negative in easy exponents
            if n_small < 0:
                return ParenthesizedExpression(Number(n_small))
            else:
                return Number(n_small)
        else:
            n_big = randint(-30,30)
            if n_big < 0:
                return ParenthesizedExpression(Number(n_big))
            else:
                return Number(n_big)
    else: 
        # Throw a dice for choosing an operation
        b = random()
        if b < 0.05 and previous_was_par == False:
            return ParenthesizedExpression(randomExpression(next_p , maxdepth-1, False, in_exp, fractions, hard_exponents))
        elif b < 0.10 and ((not in_exp) or (hard_exponents)): 
            unop = choice(["\sqrt"])
            return UnaryExpression(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions, hard_exponents))
        elif b < 0.20:
            # do the difficult binary operations
            left = randomExpression(next_p ,maxdepth-1,False, True, fractions, hard_exponents)
            op = choice(["^"])
            right = randomExpression(next_p ,maxdepth-1, False, True, fractions, hard_exponents)
            return MixfixBinaryExpression(left, op, right)
        elif b < 0.3 and not in_exp or hard_exponents:  # negation not in exponent
            unop = choice(["-"]) # other functions such a sin could be added here
            return UnaryFunctionExpression(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions, hard_exponents))
        elif b < 0.8:
            # easier binary operations
            left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions, hard_exponents)
            right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions, hard_exponents)
            if not in_exp or hard_exponents:
                mixop = choice(["+", "-", "\cdot", ":"])
            else:
                mixop = choice(["+", "\cdot"]) # no fractional or negative exponents
            
            return MixfixBinaryExpression(left, mixop, right)
        elif b < 0.9 and fractions and (not in_exp) or hard_exponents: 
            left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions, hard_exponents)
            preop = choice([r'\frac'])
            right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions, hard_exponents)
            return PrefixBinaryExpression(left, preop, right)
        else: 
            return Number(randint(0,3))

def add_exercises_knowledge( max_difficulty, max_number_of_exercises):
    punten_telling = r'\hfill' + ".../"+str(max_difficulty)
    section_title_string = r'Korte kennisvragen over $\mathbb{Z}$ of $\mathbb{Q}$ ('+ '*' * ceil(log(max_difficulty)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
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
    for _, row in problems_to_ask.iterrows():
        latex_question_math = '$'+row['question']+'$'
        latex_question_difficulty = row['difficulty']
        latex_question_natural_question = str(row['natural_question'])
        latex_question_full = r'\item ' + latex_question_natural_question + latex_question_math + '\derivblank{' + str(latex_question_difficulty) +'}'
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
    doc.append(NoEscape(r'Bereken het product '+'$'+str(dn) + '\cdot' + str(d)+'$'))
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
        f = choice([add_multiplication, add_long_division, add_substraction,add_addition])
        f(digits)
        doc.append(NoEscape(r"""
        \end{center}
        """))
    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def recurse_factors(previous_total_product,max_total_product, even_powers=False):
    p = random()
    a = randint(2,20)
    if even_powers: b = 2*randint(1,2)
    else: b = randint(1,4)
    new_product = max_total_product
    tries = 0
    while new_product > max_total_product/2 and tries < 5:
        a = randint(2,20)
        if even_powers: b = 2*randint(1,2)
        else: b = randint(1,4)
        new_power = a ** b
        new_product = previous_total_product *  new_power 
        tries +=1
    if new_product < max_total_product:
        return recurse_factors(new_product,max_total_product)
    else:
        return previous_total_product

def add_factorize_exercises(max_digits, number_of_exercises):
    max_total_product = 10**max_digits
    products =  []
    while len(products) < number_of_exercises:
        product = recurse_factors(1, max_total_product, even_powers=False)
        product_expr = Number(product)
        #print(fraction)
        if (max_total_product/20 < product) and ( product < max_total_product) and not (product_expr in products):
            products.append(product_expr)

    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Getallen ontbinden in $\mathbb{N}$ ('+ '*' * max(1,ceil(log10(max_total_product)-2)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Priemgetallen zijn getallen die alleen zichzelf en 1 als deler hebben. Bijvoorbeeld $2,3,5,7,13$ zijn allemaal priemgetallen. Bij het ontbinden in factoren zoeken we naar de priemgetallen waar een getal uit opgebouwd is. 
    
    
    Ontbind de volgende getallen in factoren, startende bij het kleinste priemgetal. Groepeer gelijke factoren met machten. Bijvoorbeeld $8 = 2^3$ en niet $8 = 2 . 2 .2$.
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for product in products:
       doc.append(NoEscape(r'\item Ontbind het product '+'$' + str(product)+ '$ in factoren:'+ '\\emptyrows{' + str(max(1,max_digits)) + '}{'+str(product)+'}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def add_simplify_root_exercises(digits, number_of_exercises):
    max_radicand = 10**digits
    # generate another exponential might fit in the next step
    perfect_square = 1
    perfect_squares = []
    while len(perfect_squares) < number_of_exercises:
        perfect_square = recurse_factors(1,max_radicand, even_powers=True)
        if (max_radicand/20 < perfect_square) and (perfect_square < max_radicand) and not (perfect_square in perfect_squares):
            perfect_squares.append(perfect_square)
        

    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Wortels vereenvoudigen in $\mathbb{N}$ ('+ '*' * digits +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Vereenvoudig de volgende wortels. Doe dit in de volgende stappen: (1) ontbind het radicand in factoren, (2) gebruik $\sqrt{ab}=\sqrt{a}\sqrt{b}$, (3) vervang in het product $\sqrt{a^{2b}}$ door $a^b$.
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for root in perfect_squares:
       doc.append(NoEscape(r'\item Vereenvoudig de vierkantswortel '+'$' + str(UnaryExpression('\sqrt', Number(root)))+ '$:'+ '\derivblank{' + str(max(0,digits -2)) + '}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))

def add_simplify_fractions_exercises(digits, number_of_exercises):
    max_nominator = 10**digits
    fractions =  []
    while len(fractions) < number_of_exercises:
        common_factor = randint(2,20)
        #print('Common factor: ', common_factor)
        nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
        #print('Random product: ', nominator)
        denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
        max_den_nom = max(nominator,denominator)
        fraction = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
        #print(fraction)
        if (max_nominator/20 < max_den_nom) and ( max_den_nom < max_nominator) and not (fraction in fractions):
            fractions.append(fraction)
        

    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Breuken vereenvoudigen in $\mathbb{Q}$ ('+ '*' * ceil(digits/2) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Vereenvoudig de volgende breuken door noemers en tellers te ontbinden in factoren. Schrap daarna de gemeenschappelijke factoren uit de teller en noemer.
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for fraction in fractions:
       doc.append(NoEscape(r'\item Vereenvoudig '+'$' + str(fraction)+ '$:'+ '\derivblank{' + str(max(0,digits -2))  + '}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def add_lcm_exercises(max_digits, number_of_exercises):
    max_total_product = 10**max_digits
    products =  []
    while len(products) < number_of_exercises:
        product = recurse_factors(1, max_total_product, even_powers=False)
        product2 = recurse_factors(1, max_total_product, even_powers=False)
        product_expr = MixfixBinaryExpression(Number(product),r', ',Number(product2))
        #print(fraction)
        if (max_total_product/20 < product) and ( product < max_total_product) and not (product_expr in products):
            products.append(product_expr)

    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Kleinst gemeenschappelijk veelvoud in $\mathbb{N}$ ('+ '*' * max(1,ceil(log10(max_total_product)-2)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Bereken het kleinst gemeenschappelijke veelvoud van volgende getallen.
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for product in products:
       doc.append(NoEscape(r'\item '+r'\mybox{$\text{kgv}(' + str(product)+ r') = $ '+
       r'\underline{\hspace{0.3 \linewidth}}}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))

def add_add_fractions_exercises(digits, number_of_exercises):
    max_nominator = 10**digits
    fractions =  []
    while len(fractions) < number_of_exercises:
        r1 = randint(2,10)
        r2 = randint(2,10)
        nominator = recurse_factors(r1, max_nominator, even_powers=False)
        denominator = recurse_factors(r2, max_nominator, even_powers=False)
        fraction_sum = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
        terms = randint(2,3)
        #print('Number of terms: ', terms)
        for i in range(1,terms):
            not_found = True
            while not_found:
                # generate first fraction
                common_factor = randint(2,5)
                #print('Common factor: ', common_factor)
                nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
                #print('Random product: ', nominator)
                denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
                fraction = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
                #print('Potential extra term: ',fraction)
                if nominator != denominator:
                    fraction_sum = MixfixBinaryExpression(fraction_sum,'+', fraction)
                    not_found = False
                    #print('Updated fraction sum: ',fraction_sum)
        fractions.append(fraction_sum)

    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Breuken optellen in $\mathbb{Q}$ ('+ '*' * (ceil(log10(max_nominator)+1)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Tel de volgende breuken op na vereenvoudiging en op gelijke noemers zetten. 
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for fraction in fractions:
       # print(fraction)
       doc.append(NoEscape(r'\item Tel '+'$' + str(fraction)+ '$ op:'+ '\derivblank{' + str(max(1,digits -1))  + '}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def add_exercise_order_operations(max_depth,max_number_of_exercises,fractions, hard_exponents):
    # Generate questions
    n=0 ; 
    max_n = max_number_of_exercises; # number of questions
    process_sympy = False # process generated expression with sympy 
    loop = 0
    max_loop = 200
    questions = []
    while n < max_n and loop < max_loop:
        
        depth = randint(ceil(max_depth/3),max_depth)
        rand_e = str(randomExpression(0.05,depth, True, False, fractions))
        latex_question_difficulty = min(max(depth-1,0),3)
        if process_sympy: 
            rand_e = re.sub(r'\\left', ' ', rand_e)
            rand_e = re.sub(r'\\right', ' ', rand_e) # bug in sympy
            latex_question_math_parsed = parse_latex(rand_e) # todo: deal with negative radicands
            latex_question_math = '$' + sympy.latex(latex_question_math_parsed) + '$'
        else: 
            latex_question_math = '$' + rand_e + '$'
        # test whether question is not very short or long
        mean_ideal_string_length = 8*(max_depth)+12 # exclude exponential or sublinear solutions
        if   abs(len(latex_question_math) - mean_ideal_string_length) < 10:
            #print(latex_question_math)
            #print('Original depth: '+str(depth))
            
            #print(latex_question_difficulty)
            latex_question_full = latex_question_math + '\derivblank{' + str(latex_question_difficulty) +'}'
            questions.append(latex_question_full)
            n= n +1
        #else:
            #print("This expression was too long or short: ", latex_question_math)
        loop = loop + 1

    # Generate LaTeX code
    if hard_exponents:
        exponenten_info = ' met moeilijke exponenten '
    else:
        exponenten_info = ''
    punten_telling = r'\hfill' + ".../"+str(n)
    if fractions:
        section_title_string = r'Volgorde bewerkingen op $\mathbb{Q}$ ' +exponenten_info + ' ('+ '*' * ceil(log(max_depth)) +')' + punten_telling 
    else:
        section_title_string = r'Volgorde bewerkingen op $\mathbb{Z}$ met kleine exponenten'+ ' ('+ '*' * ceil(log(max_depth)) +')'  + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Vereenvoudig de volgende uitdrukkingen zoveel mogelijk in deze volgorde: (1) haakjes, (2) machten en wortels, (3) vermenigvuldiging en deling en (4) optelling en aftrekking.
    Schrijf de symbolische uitkomst en een benadering daarvan in het hokje.
    \begin{itemize}
    \item Vereenvoudig elke deling ``$:$'' in een quotient plust rest ``:'' deler via Euclidische deling. Bijvoorbeeld $3 : 2 = 1 + 1:2$.
    \item Bereken alle wortels exact of benader met gekende wortels. Bijvoorbeeld $\sqrt{5} \approx 2,24 ...$.
    \item Exponenten groter dan $4$ hoeven niet berekend te worden. Schrijf dan bij de uitkomst gewoon onbekend of reken met het oneindig $\infty$ symbool als volgt: $1 : \infty = 0$, $1 \cdot \infty = \infty$. 	
    \end{itemize}

    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for question in questions:
    #print(latex_question_math)
            doc.append(NoEscape(r"""
            \item Bereken
            """))
            doc.append(NoEscape(question))



    doc.append(NoEscape(r"""
    \end{enumerate}

    \end{multicols}
    """))


#add_exercises_knowledge(4,10)
add_simple_arithmetic_exercises(4,20)
add_factorize_exercises(3,10)
add_factorize_exercises(4,4)
add_simplify_root_exercises(2,10)
add_simplify_root_exercises(3,10)
add_simplify_root_exercises(4,4)
add_exercise_order_operations(2,20, fractions = False, hard_exponents= False)
add_exercise_order_operations(6,20, fractions = False, hard_exponents = False)
add_simplify_fractions_exercises(3,10)
add_lcm_exercises(2,10)
add_add_fractions_exercises(1,10)
add_add_fractions_exercises(3,10)
add_exercise_order_operations(5,20, fractions = True, hard_exponents= False)
#add_exercise_order_operations(7,20, fractions = False, hard_exponents= False)

#doc.generate_tex('test_pylatex_latex')
doc.generate_pdf('auto_generated_prealgebra_exam')
