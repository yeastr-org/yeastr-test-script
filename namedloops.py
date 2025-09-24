from yeastr.bootstrapped import Break
from yeastr.as_decorator import with_namedloops

# -------------------- EXAMPLE 1
# from textwrap (stdlib)
#def _fix_sentence_endings(self, chunks):
#    """_fix_sentence_endings(chunks : [string])
#
#    Correct for sentence endings buried in 'chunks'.  Eg. when the
#    original text contains "... foo.\\nBar ...", munge_whitespace()
#    and split() will convert that to [..., "foo.", " ", "Bar", ...]
#    which has one too few spaces; this method simply changes the one
#    space to two.
#    """
#    i = 0
#    patsearch = self.sentence_end_re.search
#    while i < len(chunks)-1:
#        if chunks[i+1] == " " and patsearch(chunks[i]):
#            chunks[i+1] = "  "
#            i += 2
#        else:
#            i += 1

@with_namedloops(debug=True)
def _fix_sentence_endings(self, chunks):
    # recompute_end=False, since we would get IndexError
    # before we could change the chunks size, the end is thus len-1
    with For(chunks, indexed=True, recompute_end=False, end='len(chunks) - 1') as loop:
        if loop.iter[loop.i + 1] == " ": # and patsearch(loop.it):  # patsearch irrelevant to this test
            loop.iter[loop.i + 1] = "  "
            loop.i += 1

the_chunks = [..., "foo.", " ", "Bar", ...]
_fix_sentence_endings(None, the_chunks)
assert the_chunks[2] == '  ', "didn't work"

# still looks bad, let's improve:
#@with_namedloops(debug=True)
#def _fix_sentence_endings(self, chunks):
#    patsearch = self.sentence_end_re.search
#    with For(chunks, indexed=True, recompute_end=False) as loop:
#        if loop.next and loop.next == " " and patsearch(loop.it):
#            loop.next = "  "
#            loop.i += 1
# uhmmm, i'm not sure .next with None is a good idea.
# feels like handling the IndexError here would be also bad
# stick with the previous implementation until we see how to improve
# until then, this last example transpiles into non-working code
# as loop.next isn't special yet, something you can use for your own use
# maybe just implement .next that may raise and keep the -1?


print()
# -------------------- EXAMPLE 2
# Autistic Spectrum Demo
@with_namedloops(debug=True)
def asd():
    with For(range(10)) as outer:
        if outer.i == 0:
            print('continuiing, not to trigger inner.orelse the first time')
            outer.Continue
        with For(range(outer.it)) as inner:
            print(outer.i, outer.it, inner.i, inner.it)
            if inner.item == 2:
                print('breaking out of outer loop')
                outer.Break
        with inner.orelse:
            print(f'{outer.i} inner didn\'t break at all {list(range(outer.it))}')
    with outer.orelse:
        print('outer didn\'t break at all')
    print('so we have', outer.index, outer.item, inner.i, inner.it)

asd()

print()
# -------------------- EXAMPLE 3
# You can raise a Break to jump
# (and try-else to run unless jumped)
# Now you need to disable strict on the loops that should allow it
@with_namedloops(debug=True)
def jump_allowed():
    with For([True, False]) as what:
        try:
            with While(True, strict=False) as infinite:
                with While(True) as infinite2:
                    if what.it:
                        infinite.Break
                    else:
                        raise Break('jump')
        except Break as exc:
            if exc.n == 'jump':
                print('yep u jumped here')
        else:
            print('infinite loop stopped')
        print('then...')
jump_allowed()


print()
# -------------------- EXAMPLE 4
# You can forbid jumps
@with_namedloops(debug=True)
def jump_disallow_wrong_attempt():
    with For(range(3)) as loop:
        raise Break('jump')
try:
    jump_disallow_wrong_attempt()
except Break:
    print('this is impossible to catch, as there is no handler')

@with_namedloops(debug=True)
def jump_disallowed():
    try:
        with For(range(3)) as loop:
            if False:
                loop.Break
            raise Break('jump')
    except TransformError:  # aaand, that's at runtime
        print('you disallowed it')

jump_disallowed()

# -------------------- EXAMPLE 5
# actually a test for a bug...
@with_namedloops(debug=True)
def test_break_without_if():
    with While(True) as again:
        again.Break
test_break_without_if()


# -------------------- EXAMPLE 6
# You can bind names in the usual way
@with_namedloops(debug=True)
def name_bind():
    with For(chunk in ['asd', 'qwe']) as chunkloop:
        with For(ch in chunk) as charloop:
            if ch == 'w':
                chunkloop.Break
    print(f'stopped at {chunkloop.i} with "{chunk}"[{charloop.i}] = {ch}')
name_bind()

# -------------------- EXAMPLE 7
# Properly explain the name binding behaviour with indexed=True
@with_namedloops(debug=True)
def name_bind_indexed():
    #from time import perf_counter
    perf_times = 5
    chunks = ['asd', 'qwe']
    with For(chunk in chunks, indexed=True) as chunkloop:
        with For(ch in chunk) as charloop:
            if ch == 'w':
                print(f'chunk is {chunk}')
                chunkloop.item = 'rty'
                print(f'chunk is still {chunk}')
                print(f'but see {chunkloop.it} and {chunks}?')
                #_t = perf_counter()
                for _ in range(perf_times):
                    chunk
                #print(f'accessing chunk took {perf_counter() - _t}')
                #_t = perf_counter()
                for _ in range(perf_times):
                    chunkloop.it
                #print(f'accessing chunkloop.it took {perf_counter() - _t}')
                chunkloop.Break
name_bind_indexed()


# -------------------- EXAMPLE 8
# For should not enumerate unless needed
@with_namedloops(debug=True)
def non_enumerating():
    with For(c in 'asd') as chloop:  # do enumerate
        print(c.upper())
    print(chloop.i)  # makes enumerate needed
    with For('asd') as chloop2:  # do not enumerate
        print(chloop2.it.upper())
non_enumerating()

# -------------------- EXAMPLE 9
@with_namedloops(debug=True)
def also_unpack():
    with For((x, y) in [(0, 0), (1, 0), (2, 1)]) as pointsloop:
        print(x, y)
also_unpack()

# -------------------- EXAMPLE 10
# we have orempty :D
@with_namedloops(debug=True)
def orempty():
    with For(range(10)) as full:
        ...
    with full.orempty:
        assert False, 'FAILED'

    with For(range(0)) as nonfull:
        ...
    with nonfull.orempty:
        print('EMPTY')
orempty()
