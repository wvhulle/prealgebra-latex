import random,pandas,sympy
from functools import reduce
from math import sqrt,ceil,log, log2, log10
from sympy import N
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import standard_transformations,implicit_multiplication_application
from pylatex import Command,Document, Package, NoEscape, Section
from pylatex.utils import italic, escape_latex
from random import random, randint, choice
import re

doc = Document()
#doc = Document('Oefeningen', geometry_options = {"head": "2cm","margin": "2cm","bottom": "3cm"})

doc.documentclass = Command(
        'documentclass',
        options=['12pt', 'a4paper', 'twoside'],
        arguments=['article'],
    )

doc.packages.append(Package('xcolor'))
doc.packages.append(Package('amsmath'))
doc.packages.append(Package('multicol'))
doc.packages.append(Package('array'))
doc.packages.append(Package('amssymb'))# voor mathbold Z
doc.packages.append(Package('xlop')) # french long division


# on ubuntu sudo apt-cache search lastpage
# sudo apt install texlive-late-extra texlive-lang-european

doc.preamble.append(NoEscape(r"""
% start at new uneven page after part (so solutions are print seperately)
\usepackage{etoolbox}
\pretocmd{\part}{\cleardoublepage}{}{}


% this is the space a student needs to write one digit
\newcommand*{\mystrut}{\phantom{\rule[-0.05\baselineskip]{1.5mm}{1.5\baselineskip}}}
%\newcommand*{\mybox}[1]\textcolor{black!40{\framebox{#1}}
\newcommand*{\mybox}[1]{\textcolor{black!40}{\framebox{\textcolor{black!100}{#1}}}}
\newcommand{\placeholder}[1]{\mystrut}% Print -- regardless of the input
\newcommand{\gobble}[1]{}% Print <nothing> regardless of the input
\DeclareMathOperator{\lcm}{lcm}

\newcommand{\derivblank}[1]{%
    \noindent
    \begin{align*}
    \xderivblank{#1}%
&=  \hspace{0.2cm}  \mybox{\underline{ \mystrut  \hspace{0.5 \linewidth }}  $\approx$ \underline{ \hspace{0.2\linewidth}}}
    \end{align*}
}
\newcommand\xderivblank[1]{%
\ifnum#1=0 \else
        &= \hspace{0.2cm}\underline{\mystrut\hspace{0.8 \linewidth}}  \\
\xderivblank{\numexpr#1-1}\fi}


\newcommand{\derivblanksolution}[2]{%
    \noindent
    \begin{align*}
&=  \hspace{0.2cm}  \mybox{ #1 \hspace{0.05 \linewidth}  $\approx$ #2 \hspace{0.05 \linewidth}}
    \end{align*}
}


\newcommand{\emptyrows}[2]{%
    \noindent
    \begin{center}
    \begin{tabular}{ c|c } 
        &  \mystrut  \\
        #2 &  \mystrut \\\cline{1-1}
        \xemptyrows{#1}%
        &  \mystrut  \\\\
    \end{tabular}
    \mybox{$#2 = $ \underline{\hspace{0.2 \linewidth}}}
    \end{center}
}
\newcommand\xemptyrows[1]{%
\ifnum#1=0 \else
         &  \mystrut  \\
\xemptyrows{\numexpr#1-1}\fi}


\makeatletter
\@addtoreset{section}{part}
\def\@part[#1]#2{%
    \ifnum \c@secnumdepth >\m@ne
      \refstepcounter{part}%
      \addcontentsline{toc}{part}{\thepart\hspace{1em}#1}%
    \else
      \addcontentsline{toc}{part}{#1}%
    \fi
    {\parindent \z@ \raggedright
     \interlinepenalty \@M
     \normalfont\centering
     \ifnum \c@secnumdepth >\m@ne
       \LARGE\bfseries \partname\nobreakspace\thepart
       \par\nobreak
     \fi
     \huge \bfseries #2%
     \markboth{}{}\par}%
    \nobreak
    \vskip 3ex
    \@afterheading}
\renewcommand\partname{Topic}
\makeatother

\usepackage[dutch]{babel}


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




def latex_string_to_sympy(rand_expr):
    # compute slightly simplified question with sympy from latex
    stripped_expr = re.sub(r'\\left', ' ', rand_expr)
    # stripped_expr = stripped_expr.replace('\\left','')
    # stripped_expr = stripped_expr.replace('\\right','')

    stripped_expr = re.sub(r'\\right', ' ', stripped_expr) # bug in sympy
    stripped_expr = re.sub(r'\\cdot', r'*', stripped_expr)
    stripped_expr = stripped_expr.replace(':','/')

    stripped_expr = re.sub(r'\\kgv', r'\\lcm', stripped_expr)
    clean_latex = "frac" in stripped_expr
    if clean_latex:
        sympy_expr = parse_latex(stripped_expr)
    else:
        stripped_expr = stripped_expr.replace('$','')
        stripped_expr = stripped_expr.replace('\\','')

        stripped_expr = stripped_expr.replace(':','/')
        stripped_expr = stripped_expr.replace('{','(')
        stripped_expr = stripped_expr.replace('}',')')
        stripped_expr = stripped_expr.replace('^','**')
        print('Parsing unlatexified ',stripped_expr)
        sympy_expr = parse_expr(stripped_expr, evaluate=False)
    return(sympy_expr)



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
        latex_question_full = r'\item ' + latex_question_natural_question + latex_question_math + r'\derivblank{' + str(latex_question_difficulty) +'}'
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
    a = choice([*range(-7,-1,1)]+[*range(1,7,1)])
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

def add_factorize_exercises(max_digits, number_of_exercises):
    max_total_product = 10**max_digits
    products_expr =  []
    while len(products_expr) < number_of_exercises:
        product = recurse_factors(1, max_total_product, even_powers=False)
        product_expr = '$'+ str(Number(product))+'$'
        #print(fraction)
        if (max_total_product/20 < product) and ( product < max_total_product) and not (product_expr in products_expr):
            products_expr.append(product_expr)



    punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
    section_title_string = r'Getallen ontbinden in $\mathbb{N}$ ('+ '*' * max(1,ceil(log10(max_total_product)-2)) +')' + punten_telling 
    doc.append(Section(NoEscape(section_title_string)))
    doc.append(NoEscape(r"""
    Priemgetallen zijn getallen die alleen zichzelf en 1 als deler hebben. Bijvoorbeeld $2,3,5,7,13$ zijn allemaal priemgetallen. Bij het ontbinden in factoren zoeken we naar de priemgetallen waar een getal uit opgebouwd is. 
    
    
    Ontbind de volgende getallen in factoren, startende bij het kleinste priemgetal. Groepeer gelijke factoren met machten. Bijvoorbeeld $8 = 2^3$ en niet $8 = 2 . 2 .2$.
    \begin{multicols}{2}
    \begin{enumerate}
    """))

    for product in products_expr:
       doc.append(NoEscape(r'\item Ontbind het product '+ product + ' in factoren:'+ '\\emptyrows{' + str(max(1,max_digits)) + '}{'+str(product)+'}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


def generate_simplify_root_exercises(difficulty, number_of_exercises):
    max_radicand = 10**(difficulty+1)
    # generate another exponential might fit in the next step
    difficulties = []
    numeric_roots = []
    symbolic_roots = []
    perfect_squares = []


    perfect_square = 1
    while len(perfect_squares) < number_of_exercises:
        perfect_square = recurse_factors(1,max_radicand, even_powers=True)
        if (max_radicand/20 < perfect_square) and (perfect_square < max_radicand) and not (perfect_square in perfect_squares):
            perfect_squares.append('$' + str(UnaryExpression(r'\sqrt', Number(perfect_square))) )
            difficulties.append(ceil(log10(perfect_square)))

            rand_e = re.sub(r'\\left', ' ', str(perfect_square))
            rand_e = re.sub(r'\\right', ' ', rand_e) # bug in sympy
            rand_e = re.sub(r'\\cdot', r'*', rand_e)
            latex_question_math_parsed = parse_latex(rand_e) # todo: deal with negative radicands
            latex_answer_question_math = '$' + sympy.latex(latex_question_math_parsed.simplify()) + '$'
            latex_answer_question_math_eval = '$' + sympy.latex(N(latex_question_math_parsed.simplify(),3)) + '$'
            symbolic_roots.append(latex_answer_question_math )
            numeric_roots.append(latex_answer_question_math_eval)
    return([difficulties,perfect_squares,symbolic_roots,numeric_roots ])

def add_simplify_root_exercises(questions_with_answers,show_answer):
    difficulties = questions_with_answers[0]
    perfect_squares = questions_with_answers[1]
    symbolic_roots =questions_with_answers[2]
    numeric_roots = questions_with_answers[3]
    number_of_exercises = len(perfect_squares)
    if not show_answer:
        punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
        section_title_string = r'Wortels vereenvoudigen in $\mathbb{N}$ ('+ '*' * max(difficulties) +')' + punten_telling 
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(r"""
        Vereenvoudig de volgende wortels. Doe dit in de volgende stappen: (1) ontbind het radicand in factoren, (2) gebruik $\sqrt{ab}=\sqrt{a}\sqrt{b}$, (3) vervang in het product $\sqrt{a^{2b}}$ door $a^b$.
        \begin{multicols}{2}
        \begin{enumerate}
        """))
    else: 
        punten_telling = r'\hfill' + str(number_of_exercises)+"/"+str(number_of_exercises)
        section_title_string = r'Wortels vereenvoudigen in $\mathbb{N}$ ('+ '*' * max(difficulties) +')' + punten_telling 
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(r"""

        \begin{multicols}{2}
        \begin{enumerate}
        """))

    for i in range(0 , number_of_exercises):
        if not show_answer:
            doc.append(NoEscape(r'\item Vereenvoudig de vierkantswortel '+ perfect_squares[i] + r'\derivblanksolution{'+ str(difficulties[i])+ '}'))
            doc.append(NoEscape(r"""
            \end{enumerate}
            \end{multicols}
            """))
        else: 
            doc.append(NoEscape(r'\item '+ perfect_squares[i] + r'\derivblanksolution{'+ symbolic_roots[i] +'}{' + numeric_roots[i] +'}'))
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
       doc.append(NoEscape(r'\item Vereenvoudig '+'$' + str(fraction)+ '$:'+ r'\derivblank{' + str(max(0,digits -2))  + '}'))

    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))


# def add_lcm_exercises(max_digits, number_of_exercises):
#     max_total_product = 10**max_digits
#     products_expr =  []
#     products1 = []
#     products2 = []
 
#     while len(products_expr) < number_of_exercises:
#         product1 = recurse_factors(1, max_total_product, even_powers=False)
#         product2 = recurse_factors(1, max_total_product, even_powers=False)
#         product = product1 * product2
#         product_expr = MixfixBinaryExpression(Number(product1),r', ',Number(product2))
#         #print(fraction)
#         if (max_total_product/20 < product) and ( product < max_total_product) and not (product_expr in products_expr):
#             products1.append(product1)
#             products2.append(product2)
#             products_expr.append(product_expr)

#     punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
#     section_title_string = r'Kleinst gemeenschappelijk veelvoud in $\mathbb{N}$ ('+ '*' * max(1,ceil(log10(max_total_product)-2)) +')' + punten_telling 
#     doc.append(Section(NoEscape(section_title_string)))
#     doc.append(NoEscape(r"""
#     Bereken het kleinst gemeenschappelijke veelvoud van volgende getallen.
#     \begin{multicols}{2}
#     \begin{enumerate}
#     """))

#     for i in range(1,number_of_exercises):

#         p1 = products1[i]
#         p2 = products2[i]
#         doc.append(NoEscape(r'\item Ontbind eerst '+'$' + str(p1)+ ', '+ str(p2) + '$ in factoren:'))
#         doc.append(NoEscape(r'\emptyrows{' + str(max(1,max_digits)) + '}{'+str(p1)+'}'))
#         doc.append(NoEscape(r'\emptyrows{' + str(max(1,max_digits)) + '}{'+str(p2)+'}'))

#         doc.append(NoEscape(r'Bereken nu '+r'$\text{kgv}(' + str(product)+ r'):$ '+ r'\derivblank{' + str(max(0,max_digits -2))  + '}'))

#     doc.append(NoEscape(r"""
#     \end{enumerate}
#     \end{multicols}
#     """))




# def add_add_fractions_exercises(digits, number_of_exercises):
#     max_nominator = 10**digits
#     fractions =  []
#     while len(fractions) < number_of_exercises:
#         r1 = randint(2,10)
#         r2 = randint(2,10)
#         nominator = recurse_factors(r1, max_nominator, even_powers=False)
#         denominator = recurse_factors(r2, max_nominator, even_powers=False)
#         fraction_sum = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
#         terms = randint(2,3)
#         #print('Number of terms: ', terms)
#         for i in range(1,terms):
#             not_found = True
#             while not_found:
#                 # generate first fraction
#                 common_factor = randint(2,5)
#                 #print('Common factor: ', common_factor)
#                 nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
#                 #print('Random product: ', nominator)
#                 denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
#                 fraction = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
#                 #print('Potential extra term: ',fraction)
#                 if nominator != denominator:
#                     fraction_sum = MixfixBinaryExpression(fraction_sum,'+', fraction)
#                     not_found = False
#                     #print('Updated fraction sum: ',fraction_sum)
#         fractions.append(fraction_sum)

#     punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
#     section_title_string = r'Breuken optellen in $\mathbb{Q}$ ('+ '*' * (ceil(log10(max_nominator)+1)) +')' + punten_telling 
#     doc.append(Section(NoEscape(section_title_string)))
#     doc.append(NoEscape(r"""
#     Tel de volgende breuken op na vereenvoudiging en op gelijke noemers zetten. 
#     \begin{multicols}{2}
#     \begin{enumerate}
#     """))

#     for fraction in fractions:
#        # print(fraction)
#        doc.append(NoEscape(r'\item Tel '+'$' + str(fraction)+ '$ op:'+ r'\derivblank{' + str(max(1,digits -1))  + '}'))

#     doc.append(NoEscape(r"""
#     \end{enumerate}
#     \end{multicols}
#     """))

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
        return str(self.left) + self.op + str(self.right) 


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
        return r"\left(" + str(self.exp) + r'\right)'

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
        #return self.op + r'(' + str(self.exp) + r')'


def randomExpression(prob,maxdepth,previous_was_par=False, in_exp=False, fractions=False):
    # Throw a dice for choosing whether this is going to be number
    p = random()
    next_p = prob + 0.05*(1-prob) # step-wise increase in number probability on each level
    if p <= prob or maxdepth <= 0:
        if in_exp == True: # use smaller numbers
            n_small = randint(0,4) # no negative numbers for easy exponents
            if n_small < 0:
                return ParenthesizedExpression(Number(n_small))
            else:
                return Number(n_small)
        else:
            n_big = randint(-10,30)
            if n_big < 0:
                return ParenthesizedExpression(Number(n_big))
            else:
                return Number(n_big)
    else: 
        # Throw a dice for choosing an operation
        b = random()
        if b < 0.05 and previous_was_par == False:
            return ParenthesizedExpression(randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
        elif b < 0.10 and ((not in_exp)): 
            unop = choice([r"\sqrt"])
            return UnaryExpression(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
        elif b < 0.20:
            # do the difficult binary operations
            left = randomExpression(next_p ,maxdepth-1,False, True, fractions)
            op = choice(["^"])
            right = randomExpression(next_p ,maxdepth-1, False, True, fractions)
            return MixfixBinaryExpression(left, op, right)
        elif b < 0.3 and not in_exp:  # negation not in exponent
            unop = choice(["-"]) # other functions such a sin could be added here
            return UnaryFunctionExpression(unop,randomExpression(next_p , maxdepth-1, False, in_exp, fractions))
        elif b < 0.8:
            # easier binary operations
            left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions)
            right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions)
            if not in_exp:
                mixop = choice(["+", "-", r"\cdot"])
            else:
                mixop = choice(["+", r"\cdot"]) # no fractional or negative exponents
            return MixfixBinaryExpression(left, mixop, right)
            
        elif b < 0.9 and fractions and (not in_exp): 
            left = randomExpression(next_p ,maxdepth-1,False,in_exp, fractions)
            preop = choice([r'\frac'])
            right = randomExpression(prob * 1.2,maxdepth-1, False, in_exp, fractions)
            return PrefixBinaryExpression(left, preop, right)
        else: 
            return Number(randint(0,3))

# generator gives a question math string (without $$) in LaTeX
def generate_latex_question_with_answer(question_generator,difficulty, solver):
    loop = 0
    max_loop = 20
    found = False
    while not found and loop < max_loop:
        generated_question = question_generator(difficulty)
        rand_expr = generated_question [0]
        #print(rand_expr)
        hints = generated_question [1]
        latex_question_math = '$' + rand_expr + '$'
        mean_ideal_string_length = 4*(difficulty)+2
        latex_question_math_parsed = latex_string_to_sympy(rand_expr)
        print('The generated question ', str(latex_question_math_parsed), ' has length ', len(str(latex_question_math_parsed)), ' but i expected more like ', mean_ideal_string_length)
        if   abs(len(str(latex_question_math_parsed)) - mean_ideal_string_length) < 8:
            found = True
            latex_question_difficulty = min(max(difficulty-1,1),4) 
            latex_answer_question_math = '$' + sympy.latex(solver(latex_question_math_parsed)) + '$'
            #print(latex_answer_question_math)
            latex_answer_question_math_eval = '$' + sympy.latex(N(latex_question_math_parsed.simplify(),3)) + '$'

        loop += 1

    if not loop < max_loop:
        print('Generated too many long or short questions.')
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
        punten_telling = r'\hfill' + ".../"+ n
        section_title_string = title + ' ('+ '*' * (qas[0])[0]  +') '  + punten_telling 
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(advice_for_exercises))
        doc.append(NoEscape(r"""
        \begin{multicols}{2}
        \begin{enumerate}
        """))
    else: 
        punten_telling = r'\hfill' +  n + "/"+ n
        section_title_string = title + r' (oplossing)' + ' ('+ '*' * (qas[0])[0] +')'  + punten_telling   
        
        doc.append(Section(NoEscape(section_title_string)))
        doc.append(NoEscape(r"""
        \begin{multicols}{2}
        \begin{enumerate}
        """))

    for qa in qas:
        stars = str(min(3,max(1,qa[0])))
        initial_question = qa[1][0]
        print('The initial questions is ', initial_question)
        hints = qa[1][1]
        #print('outputting question ', initial_question, ' with hints ', hints)
        doc.append(NoEscape(r'\item ' + imperative + r': '))
        doc.append(NoEscape(initial_question + r'. '))
        if not with_answers:
            for hint in hints:
                rendered_hint = hint_renderer(hint)
                #print('The hint '+ str(hint) + ' will be rendered as ', rendered_hint)
                doc.append(NoEscape(rendered_hint))
            doc.append(NoEscape(r'\derivblank{' + stars +'}'))
        else:
            doc.append(NoEscape(r'\derivblanksolution{' + qa[2] + '}{' + qa[3] + '}'))
    
    doc.append(NoEscape(r"""
    \end{enumerate}
    \end{multicols}
    """))

# TODO: question types: simplify, factorize/expand

def generate_Z_arithm_questions(difficulty, number):
    def question_Z_arithm_generator(difficulty):
        fractions = False
        hints = []
        main_question = str(randomExpression(0.05,difficulty, True, False, fractions))
        #print(main_question)
        return([main_question,hints])

    title = r"Volgorde van de bewerkingen"
    advice = r"""
    Vereenvoudig de volgende uitdrukkingen zoveel mogelijk in deze volgorde: (1) haakjes, (2) machten en wortels, (3) vermenigvuldiging en deling en (4) optelling en aftrekking.
    \begin{itemize}
    \item Bereken alle wortels exact of benader met gekende wortels. Bijvoorbeeld $\sqrt{5} \approx 2,24 ...$.
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
            nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
            denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
            fraction = PrefixBinaryExpression(Number(nominator),r'\frac', Number(denominator))
            if i == 0:
                fraction_sum = fraction
            else : 
                fraction_sum = MixfixBinaryExpression(fraction_sum,'+', fraction)
        hints = []
        if terms > 2:
            hints.append('\\ (zet eerst alle breuken op dezelfde noemer')
        return([str(fraction_sum),hints])

    title = r"Optellen in $\mathbb{Q}$"
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
        # found = False 
        # max_loop = 10
        # loop = 0
        # while not found and loop < max_loop:
        product1 = recurse_factors(1, max_total_product, even_powers=False)
        product2 = recurse_factors(1, max_total_product, even_powers=False)
        #product = product1 * product2
        lcm_expr = UnaryFunctionExpression('\lcm', MixfixBinaryExpression(Number(product1),r', ',Number(product2)))
        #print(lcm_expr)
            # print('Checking whether this is a good product for lcm)     
            # if (max_total_product/20 < product) and ( product < max_total_product):
        subquestion1 = str(Number(product1))
        subquestion2 = str(Number(product2))
        output = [r''+str(lcm_expr), [subquestion1, subquestion2]]
        #print(output)
        # found = True
            # loop += 1
        return output
    def render_factorize_hint(product):
        rows = ceil(log2(len(product)))
        return(r'\emptyrows{' + str(rows) + '}{'+str(product)+'}')
    title = r"Kleinst gemeen veelvoud in $\mathbb{N}$"
    advice = r"""
    Factorizeer beide getallen en bepaal kleinst gemeenschappelijk veelvoud.
    """
    imperative = "Bereken"
    def solver(expr): 
        return(sympy.simplify(expr))
    full_problems = generate_exercises(generate_lcm_question,difficulty,number, title, advice, imperative, render_factorize_hint,solver)
    return(full_problems)

#def add_lcm_exercises(max_digits, number_of_exercises):
#     
#     products_expr =  []
#     products1 = []
#     products2 = []
 
#     while len(products_expr) < number_of_exercises:
#         product1 = recurse_factors(1, max_total_product, even_powers=False)
#         product2 = recurse_factors(1, max_total_product, even_powers=False)
#         product = product1 * product2
#         product_expr = MixfixBinaryExpression(Number(product1),r', ',Number(product2))
#         #print(fraction)
#         if (max_total_product/20 < product) and ( product < max_total_product) and not (product_expr in products_expr):
#             products1.append(product1)
#             products2.append(product2)
#             products_expr.append(product_expr)

#     punten_telling = r'\hfill' + ".../"+str(number_of_exercises)
#     section_title_string = r'Kleinst gemeenschappelijk veelvoud in $\mathbb{N}$ ('+ '*' * max(1,ceil(log10(max_total_product)-2)) +')' + punten_telling 
#     doc.append(Section(NoEscape(section_title_string)))
#     doc.append(NoEscape(r"""
#     Bereken het kleinst gemeenschappelijke veelvoud van volgende getallen.
#     \begin{multicols}{2}
#     \begin{enumerate}
#     """))

#     for i in range(1,number_of_exercises):

#         p1 = products1[i]
#         p2 = products2[i]
#         doc.append(NoEscape(r'\item Ontbind eerst '+'$' + str(p1)+ ', '+ str(p2) + '$ in factoren:'))
#         doc.append(NoEscape(r'\emptyrows{' + str(max(1,max_digits)) + '}{'+str(p1)+'}'))
#         doc.append(NoEscape(r'\emptyrows{' + str(max(1,max_digits)) + '}{'+str(p2)+'}'))

#         doc.append(NoEscape(r'Bereken nu '+r'$\text{kgv}(' + str(product)+ r'):$ '+ r'\derivblank{' + str(max(0,max_digits -2))  + '}'))

#     doc.append(NoEscape(r"""
#     \end{enumerate}
#     \end{multicols}
#     """))




#add_exercises_knowledge(4,10)
#add_simple_arithmetic_exercises(4,10)


#add_factorize_exercises(4,4)
#add_simplify_root_exercises(2,10)
#add_simplify_root_exercises(3,10)
#add_simplify_root_exercises(4,4)
#s(max_depth,max_number_of_exercises,fractions, hard_exponents)

# Generate all the questions with answers
full_sections_with_answers = []
full_sections_with_answers.append(generate_lcm_questions(2,10))
full_sections_with_answers.append(generate_Z_arithm_questions(3,10))
full_sections_with_answers.append(generate_Q_sum_questions(3,4))


#root_questions_with_answers = generate_simplify_root_exercises(2,4)
#add_simplify_root_exercises(root_questions_with_answers, False)


doc.append(NoEscape(r"\part{Vragen}"))
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

doc.generate_tex('auto_generated_prealgebra_exam')
doc.generate_pdf('auto_generated_prealgebra_exam')
