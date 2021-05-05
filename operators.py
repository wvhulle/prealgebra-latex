import random
from sympy.ntheory import factorint
import sympy
from numpy import prod
from math import sqrt,ceil,log, log2, log10, floor, ceil, log


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
        self.likelihood_number_is_output = li # probability as function of parent number in tree
        self.order_of_application = pr # precedence
        self.inverse_map = sp # function of parent number to generate leaves or operand numbers
        self.layout_function = ex # function of leaves expressions to format full operator
        self.is_associative = ass # in case of n-ary operators, visually separates arguments?
    def __str__(self):
        return "precedence: " + str(self.order_of_application) + ", weight: " + str(self.likelihood_number_is_output)


function_precedence = 5

identity_op = MathOp("id", lambda n : 1/10, function_precedence, lambda n : [n], lambda le : PrefixUnaryWithoutCurlyBrackets("", le[0]),"none")


def li_neg(n):
    if n > 0:
        l = 1/8
    else:
        l = 1/12
    return(l)

neg_print = lambda le : PrefixUnaryWithoutCurlyBrackets("-",le[0])
negate_op = MathOp("neg", li_neg, 3,lambda n : [-n] , neg_print ,True)

def li_root(current_integer): 
    li = 2/(5*(len(str(current_integer))*(current_integer<=20)+1))
    return(li)

sqrt_op = MathOp("sqrt", li_root, function_precedence, lambda x : [x**2], lambda le : PrefixUnaryWithCurlyBrackets(r'\sqrt',le[0]),"none")


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
        return([current_integer,1,0,0])

def print_pythagorean(le):
    expr = MixfixWithoutCurlyBrackets(MixfixWithCurlyBrackets(le[0], '^', le[1]), "+", MixfixWithCurlyBrackets(le[2], '^', le[3]))
    return(expr)

pythagorean_op= MathOp("pyth", li_pythagorean, function_precedence,decompose_pythagorean, print_pythagorean, "none")



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

power_op = MathOp("power", li_power, 2, decompose_power, lambda le : (MixfixWithCurlyBrackets(le[0], r'^', le[1]) ), "right")

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


minus_op = MathOp("minus", likelihood_minus, 4, minus_decompose, lambda le  : MixfixWithoutCurlyBrackets(le[0], "-", le[1]), "left")


def plus_decompose(current_integer):
    m = abs(int(current_integer))
    term1_num = random.randint(-m,m)
    term2_num = floor(current_integer - term1_num)
    return([term1_num,term2_num])

plus_op = MathOp("plus", lambda n : (1/4)*len(str(n)), 4, plus_decompose, lambda le  : MixfixWithoutCurlyBrackets(le[0], "+", le[1]), "none")




def frac_decompose(current_integer):
    extra_factor = random.randint(2,10)    
    multiple = extra_factor*current_integer
    if multiple/extra_factor != current_integer:
        print("Fraction problem.")
    return([multiple,extra_factor])

frac_op = MathOp("fraction", lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: PrefixBinaryWithCurlyBrackets(le[0], r'\frac',le[1]),"none")

div_op = MathOp("division", lambda n : 1/(len(str(n))), 3, frac_decompose, lambda le: MixfixWithoutCurlyBrackets(le[0], r':',le[1]), "left")

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

mul_op=MathOp("mult",mul_likelihood, 3, mul_decompose, lambda le : MixfixWithoutCurlyBrackets(le[0], r' \cdot ', le[1]),"none")

linear_op = MathOp("unknown x", lambda n : (2/len(str(n))), 3, lambda n : [n], lambda le :  PrefixUnaryWithoutCurlyBrackets(r' x\cdot  ', le[0]), "none")


parenthesis_op = MathOp("brackets", lambda n : 1, 0, lambda n : [n], lambda le : PrefixUnaryWithCurvyBrackets("",le[0]), "none")

#parenthesis_op = MathOp("brackets", lambda n : 1, 0, lambda n : [n], lambda le : PrefixUnaryWithoutCurlyBrackets("",le[0]), True)


def is_binary_op(op):
    return(len(op.inverse_map(10))>1)