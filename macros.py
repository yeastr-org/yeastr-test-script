from yeastr.bootstrapped import def_macro, with_macros


@def_macro(hygienic=False)
def m_hf(b):
    if a > 3:
        c = 3
    if b > 3:
        c = -3

@def_macro(hygienic=True)
def m_ht(b):
    if a > 3:
        c = 3
    if b > 3:
        c = -3

@with_macros()
def test_hygiene():
    for hyg in (True, False):
        a = 2
        # NOPE, u cannot (m_ht if hyg else m_hf)(4)
        if hyg: m_ht(4)
        else: m_hf(4)
        try:
            print(c)
        except NameError:
            print('why did u switch hygienic on?')
        try:
            print(b)
        except NameError:
            print('all right')
test_hygiene()

'''
# gotta fight with this
@def_macro(hygienic=False)
def acc(x):
    a += x

@with_macros
def test():
    a = 3
    print(a, acc(3), a)
'''


# Now we want to evaluate something during macro expansion
# we have a very limited mLang flag (please should be limited)

@def_macro(severity=-1, mLang=True)
def printout(msg):
    with mIf(severity > 0):
        print(msg)

@with_macros()
def letssee():
    printout('ciao', severity=1)
    printout('no', severity=0)
    printout('no')

letssee()

# Let's make sure you can nest macro definitions

@def_macro()
def inner():
    print('inner')

@def_macro()
def outer():
    inner()
    inner()

@with_macros()
def test_it_nested():
    outer()

test_it_nested()


# no, you can't use @def_macro without ()
# you can do so only if you preprocess at build
#@def_macro
#def my_m():
#    print('okay')
#my_m()


# so you want expression macros?
# mhh.. why?
# let's try shortening some code
import ast
@def_macro(expr=True, mLang=True)
def a_cmp(left, ops, comparators):
    """ast.Compare: usually you cmp just 2 objs"""
    with mIf(
        isinstance(ops, ast.List)
        and isinstance(comparators, ast.List)
    ):
        # keep the default behaviours
        ast.Compare(
            left=left,
            ops=ops,
            comparators=comparators,
        )
    with mIf(not isinstance(ops, ast.List)):
        # if ops is not a list, it means
        # comparators is not a list either
        ast.Compare(
            left=left,
            ops=[ops],
            comparators=[comparators],
        )

@with_macros()
def test_expr_macro():
    print(ast.dump(
        a_cmp(
            ast.Name('subj', ctx=ast.Load()),
            ast.Eq(),
            ast.Constant(3)
        )
    ))
test_expr_macro()
# Compare(left=Name(id='subj', ctx=ast.Load()), ops=[Eq()], comparators=[Constant(value=3)])
# awesome... ofc, this means after mLang, there must be only 1 expression left.
# as you can see, you can use positional arguments,
# and they can be whatever you want, won't get converted..
# TODO: check they actually don't get converted
# no new names are bound, just literal substitution.

# an expr macro without mLang raises a TransformError
# when more than one expression is used
# ... it's AssertionError...
try:
    @def_macro(expr=True)
    def wrong():
        exp1
        exp2
except AssertionError as exc:
    print(str(exc))

# I don't see a reason for bijection example for JIT
