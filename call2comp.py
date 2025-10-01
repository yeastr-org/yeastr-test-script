# ye pls do star import of yeastr
from yeastr.as_decorator import with_call2comp, TransformError, random_string
from sys import version_info

@with_call2comp(debug=True)
def something():
    print(emap(lambda x: x + 1, range(10)))
    print(efilter(lambda x: x > 4, range(10)))

something()

@with_call2comp(debug=True)
def something_more():
    d = {'a': 'A', 'b': 'B'}
    print(emap(lambda k, v: k + v, d.items()))
    print(efilter(lambda k, v: v == 'B', d.items()))
    print(emapd(lambda k, v: (k*2, v*2), d.items()))
    if version_info >= (3, 11):
        print(efilterd(
            lambda k, v: k.startswith('b'),
            (d | emapd(lambda k, v: (k*2, v*2), d.items())).items()
        ))
    print(emapd(lambda k: (k, k*2), d.keys()))
    print(efilters(lambda v: v > 2, [0, 1, 2, 3, 4]))
    print(efiltermap(lambda v: v > 2, lambda v: v + 3, [0, 2, 3, 4, 5, 6, 7]))
    print(efiltermaps(lambda v: v > 2, lambda v: v + 3, [5, 5, 5, 5, 6, 7]))
    print(efiltermapd(
        lambda k, v: k.startswith('a'),
        lambda k, v: (k * 3, v * 3),
        {'aa': 'AA', 'bb': 'BB', 'aaa': 'AAA'}.items()
    ))

something_more()

@with_call2comp(debug=True)
def something_exaustive():
    d = {'a': 'A', 'b': 'B'}
    try:
        print(emap((bound := lambda k, v: k + v), d.items()))
    except TypeError:
        print('well, that\'s unfixable?')
    print(emap((bound := lambda k: k + k), d.items()))
    print('well, that is expected, right? (just name it kv)')
something_exaustive()

try:
    @with_call2comp(debug=True)
    def something_tricky():
        try:
            print(emapd((bound := lambda k, v: {k*2: v*2}), d.items()))
        except TransformError:
            print('we have some limit')
except TransformError as exc:
    print(str(exc))
    print('you should never need to expect a TransformError')


@with_call2comp(debug=True)
def some_filtering():
    d = {'a': 'A', 'b': 'B'}
    print(efilter((bound := lambda kv: kv[0].startswith('a')), d.items()))
    print(efilterd((bound := lambda k, v: k.startswith('a')), d.items()))
    print(efiltermap((fil := lambda kv: kv[0] == 'a'), lambda kv: (kv[0]*2, kv[1]*2), d.items()))
    print(efiltermap(lambda kv: kv[0] == 'a', (_map := lambda kv: (kv[0]*2, kv[1]*2)), d.items()))
    print(efiltermapd((fil := lambda k, v: k == 'a'), lambda k, v: (k*2, v*2), d.items()))
some_filtering()

try:
    @with_call2comp(debug=True)
    def some_filtering():
        d = {'a': 'A', 'b': 'B'}
        print(efiltermapd(lambda k, v: k == 'a', (_map := lambda k, v: (k*2, v*2)), d.items()))
except TransformError as exc:
    print(str(exc))
    print('you should never need to expect a TransformError')

@with_call2comp(debug=True)
def some_filtering():
    d = {'a': 'A', 'b': 'B'}
    def _map(k, v): return (k*2, v*2)
    print(efiltermapd(lambda k, v: k == 'a', _map, d.items(),
                      performance_required=False))
    print(efiltermapd(lambda n: n % 2 == 0, lambda n: (n, n ** 2), range(10),
                      performance_required=False))
some_filtering()

@with_call2comp(debug=True)
def fix_unfixable():
    d = {'a': 'A', 'b': 'B'}
    print(emap((bound := lambda k, v: k + v), d.items(),
               performance_required=False))
    print(emapd((bound := lambda k, v: (k*2, v*2)), d.items(),
               performance_required=False))
fix_unfixable()
