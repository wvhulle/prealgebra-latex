def add_exercises_knowledge(doc, max_difficulty, max_number_of_exercises):
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
    doc.append(NoEscape(r"""
     Bereken de deling: \\
    \opdiv[resultstyle=\gobble,remainderstyle=\gobble,maxdivstep=5,dividendbridge]
    """))
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

def add_substraction(doc,length):
    doc.append(NoEscape(r"""
     Bereken de aftrekking: \\
    \opsub[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))


def add_addition(doc,length):
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r"""
     Bereken de optelling: \\
    \opadd[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholder]
    """))
    
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

def add_multiplication(doc,length):
    dn = abs(random.randint(10**(length-2),10**length))
    d = abs(random.randint(10**(length-3),10**(length-2)))
    doc.append(NoEscape(r'Bereken het product '+'$'+str(dn) + r'\cdot' + str(d)+'$'))
    doc.append(NoEscape(r"""   
    \opmul[resultstyle=\gobble,intermediarystyle=\placeholder,carrystyle=\placeholde]
    """))
    
    doc.append(NoEscape(r'{' + str(dn) + r'}' +r'{'+ str(d) + r'}'))

def add_simple_arithmetic_exercises(doc,digits,max_number_of_exercises):
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


#### Questions that make use of factoring numbers

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

# def generate_Z_root_questions(difficulty, number):
#     def question_Z_root_generator(difficulty):
#         max_radicand = 10**(difficulty+1)
#         max_loops = 10
#         loops = 0
#         found = False
#         while loops < max_loops and not found :
#             perfect_square = recurse_factors(1,max_radicand, even_powers=True)
#             if (max_radicand/20 < perfect_square) and (perfect_square < max_radicand):
#                 root = str(PrefixUnaryWithCurlyBrackets(r'\sqrt', Number(perfect_square)))
#                 found = True
#             loops += 1
#         hints = []
#         return([root,hints])

#     title = r"Wortels vereenvoudigen in N"
#     advice = r"""
#     Splits het getal onder de wortel (het radicand) op in kleinere gelijke factoreren. Doe dit door het te factorizeren. Gebruik daarna de eigenschappen van wortels om de wortel te vereenvoudigen in wortels van priemgetallen. Bereken de wortels van priemgetallen met een rekenmachine  of gebruik deze getallen:
#     \begin{itemize}
#      \item $\sqrt{2} \approx 1,41 ...$
#     \item $\sqrt{3} \approx 1,73 ...$
#      \item $\sqrt{5} \approx 2,24 ...$
    
#      \end{itemize}
#     """
#     imperative = "Bereken"
#     hinter = lambda x : x
#     solver = sympy.simplify
#     full_problems = generate_exercises(question_Z_root_generator,difficulty,number, title, advice, imperative,hinter,solver)
#     return(full_problems)

# def generate_Q_simplify_questions(difficulty, number):
#     def question_Q_simplify_generator(difficulty):
#         max_nominator = 10**difficulty
#         max_loops = 10
#         loops = 0
#         found = False
#         while loops < max_loops and not found:
#             common_factor = random.randint(2,20)
#             nominator = recurse_factors(common_factor, max_nominator, even_powers=False)
#             denominator = recurse_factors(common_factor, max_nominator, even_powers=False)
#             max_den_nom = max(nominator,denominator)
#             fraction = PrefixBinaryWithCurlyBrackets(Number(nominator),r'\frac', Number(denominator))
#             if (max_nominator/20 < max_den_nom) and ( max_den_nom < max_nominator):
#                 math = fraction
#                 found = True
#             loops += 1
#         hints = []
#         return([str(math),hints])

#     title = r"Vereenvoudigen in $\mathbb{Q}$"
#     advice = r"""
#     Ontbind de teller en noemer en schrap de gemeenschappelijke factoren. 
#     """
#     imperative = "Vereenvoudig"
#     hinter = lambda x : x
#     solver = sympy.simplify
#     full_problems = generate_exercises(question_Q_simplify_generator,difficulty,number, title, advice, imperative,hinter,solver)
#     return(full_problems)