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
