"""Day 0: Cold Boot.

Every visitor gets their own boot program. It is a small register machine
that computes ``K * n * (n + 1) / 2 + M`` the slow way, where ``n`` is ``N``
for part one and ``N + X`` once the turbo switch puts a 1 in register c.
Part one runs fine in a naive interpreter; part two takes a while, unless
you read the program instead of running it.
"""
import random
import secrets
from dataclasses import dataclass

SESSION_KEY = 'puzzle_seed'


@dataclass(frozen=True)
class Params:
    n: int
    k: int
    x: int
    m: int


def seed_for(request):
    seed = request.session.get(SESSION_KEY)
    if not isinstance(seed, int):
        seed = secrets.randbits(32)
        request.session[SESSION_KEY] = seed
    return seed


def params(seed):
    rng = random.Random(seed)
    return Params(
        n=rng.randint(250, 400),
        k=rng.randint(3, 9),
        x=rng.randint(900, 1400),
        m=rng.randint(10, 99),
    )


def program(p):
    return [
        f'mov {p.n} b',
        'jnz c 2',
        'jnz 1 5',
        f'mov {p.x} d',
        'inc b',
        'dec d',
        'jnz d -2',
        'mov b c',
        f'mov {p.k} d',
        'inc a',
        'dec d',
        'jnz d -2',
        'dec c',
        'jnz c -5',
        'dec b',
        'jnz b -8',
        f'mov {p.m} d',
        'inc a',
        'dec d',
        'jnz d -2',
    ]


def answer(p, part):
    n = p.n if part == 1 else p.n + p.x
    return p.k * n * (n + 1) // 2 + p.m


def run(lines, c=0, limit=None):
    """A straightforward interpreter, the one the puzzle invites you to write."""
    regs = {'a': 0, 'b': 0, 'c': c, 'd': 0}
    code = [line.split() for line in lines]
    val = lambda arg: regs[arg] if arg in regs else int(arg)
    pc = steps = 0
    while 0 <= pc < len(code):
        op, *args = code[pc]
        if op == 'mov':
            regs[args[1]] = val(args[0])
        elif op == 'inc':
            regs[args[0]] += 1
        elif op == 'dec':
            regs[args[0]] -= 1
        elif op == 'jnz' and val(args[0]) != 0:
            pc += val(args[1])
            continue
        pc += 1
        steps += 1
        if limit and steps > limit:
            raise RuntimeError('step limit exceeded')
    return regs['a']
