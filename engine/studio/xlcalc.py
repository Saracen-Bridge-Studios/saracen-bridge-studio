"""A small Excel formula evaluator for Jon's Sales Valuation Engine workbook (1.0.5).

Written for the Studio rather than bundling a third-party engine: the one that handles this workbook (pycel) is GPL-3.0,
which would bind Jon's closed-source app (register S-66). It covers exactly what his workbook uses, checked by a scan
of all 21,759 formulas: the operators = <> < > <= >= + - * / & ^ and unary minus, cell and range references on any
sheet, and IF, IFERROR, INDEX, MATCH (exact), OR, AND, MAX, MIN, SUM, PRODUCT, COUNT, COUNTIF, COUNTIFS, AVERAGE,
MEDIAN, QUARTILE, LARGE, SUMPRODUCT (with array comparisons), YEAR, YEARFRAC (basis 0) and ROWS, with Excel's rules
for blanks, text, booleans and errors. Results are tested cell for cell against LibreOffice's recalculation of the
same filled workbook (tests/test_sales.py).
"""
from __future__ import annotations

import datetime as dt
import math
import re

from openpyxl.formula.tokenizer import Token, Tokenizer
from openpyxl.utils import column_index_from_string, get_column_letter

EPOCH = dt.datetime(1899, 12, 30)


class Err:
    __slots__ = ("code",)

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return self.code


NA, VALUE, DIV0, NUM, REF, NAME = (Err(c) for c in ("#N/A", "#VALUE!", "#DIV/0!", "#NUM!", "#REF!", "#NAME?"))
ERRS = {e.code: e for e in (NA, VALUE, DIV0, NUM, REF, NAME)}


class Rng:
    """A rectangular block of cells on one sheet, read lazily (values evaluated on first use)."""
    __slots__ = ("book", "sheet", "r1", "c1", "r2", "c2", "_v")

    def __init__(self, book, sheet, r1, c1, r2, c2):
        self.book, self.sheet, self.r1, self.c1, self.r2, self.c2, self._v = book, sheet, r1, c1, r2, c2, None

    @property
    def rows(self):
        return self.r2 - self.r1 + 1

    @property
    def cols(self):
        return self.c2 - self.c1 + 1

    def values(self):
        if self._v is None:
            self._v = self.book.block(self.sheet, self.r1, self.c1, self.r2, self.c2)
        return self._v


def _grid(x):
    """A range or array as a list of rows; anything else as None."""
    if isinstance(x, Rng):
        return x.values()
    if isinstance(x, list):
        return x
    return None


def _flat(x):
    g = _grid(x)
    if g is None:
        return [x]
    return [v for row in g for v in row]


# ------------------------------------------------------------------------------------------------ coercion
def _num(v):
    """A value used in arithmetic: blank 0, TRUE 1, numeric text its number, other text #VALUE!."""
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, Err):
        return v
    if isinstance(v, str):
        try:
            return float(v.strip()) if v.strip() else VALUE
        except ValueError:
            return VALUE
    return VALUE


def _text(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        if v.is_integer() and abs(v) < 1e15:
            return str(int(v))
        return repr(float(f"{v:.15g}"))
    if isinstance(v, int):
        return str(v)
    return str(v)


def _bool(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, Err):
        return v
    if isinstance(v, str):
        if v.upper() == "TRUE":
            return True
        if v.upper() == "FALSE":
            return False
    return VALUE


def _r15(x: float) -> float:
    """Excel compares numbers to 15 significant digits (0.1 + 0.2 = 0.3 is TRUE)."""
    return float(f"{x:.15g}")


def _rank(v):
    return 0 if isinstance(v, (int, float)) and not isinstance(v, bool) else 1 if isinstance(v, str) else 2


def _compare(a, b, op):
    if isinstance(a, Err):
        return a
    if isinstance(b, Err):
        return b
    if a is None:
        a = "" if isinstance(b, str) else False if isinstance(b, bool) else 0.0
    if b is None:
        b = "" if isinstance(a, str) else False if isinstance(a, bool) else 0.0
    ra, rb = _rank(a), _rank(b)
    if ra != rb:
        c = (ra > rb) - (ra < rb)
    elif ra == 1:
        x, y = a.lower(), b.lower()
        c = (x > y) - (x < y)
    else:
        x, y = _r15(float(a)), _r15(float(b))
        c = (x > y) - (x < y)
    return {"=": c == 0, "<>": c != 0, "<": c < 0, ">": c > 0, "<=": c <= 0, ">=": c >= 0}[op]


def _arith(a, b, op):
    if op == "&":
        if isinstance(a, Err):
            return a
        if isinstance(b, Err):
            return b
        return _text(a) + _text(b)
    if op in ("=", "<>", "<", ">", "<=", ">="):
        return _compare(a, b, op)
    x, y = _num(a), _num(b)
    if isinstance(x, Err):
        return x
    if isinstance(y, Err):
        return y
    if op == "+":
        return x + y
    if op == "-":
        return x - y
    if op == "*":
        return x * y
    if op == "/":
        return DIV0 if y == 0 else x / y
    if op == "^":
        try:
            return float(x ** y)
        except (OverflowError, ZeroDivisionError, ValueError):
            return NUM
    return VALUE


def _broadcast(a, b, f):
    ga, gb = _grid(a), _grid(b)
    if ga is None and gb is None:
        return f(a, b)
    if ga is None:
        return [[f(a, y) for y in row] for row in gb]
    if gb is None:
        return [[f(x, b) for x in row] for row in ga]
    if len(ga) != len(gb) or len(ga[0]) != len(gb[0]):
        rows, cols = max(len(ga), len(gb)), max(len(ga[0]), len(gb[0]))
        pick = lambda g, r, c: g[r][c] if r < len(g) and c < len(g[0]) else NA
        return [[f(pick(ga, r, c), pick(gb, r, c)) for c in range(cols)] for r in range(rows)]
    return [[f(x, y) for x, y in zip(ra, rb)] for ra, rb in zip(ga, gb)]


# ------------------------------------------------------------------------------------------------ functions
def _numbers(args, *, refs_like_ranges=True):
    """Numbers from function arguments, Excel style: inside ranges only numbers count; typed values are coerced."""
    out = []
    for a in args:
        g = _grid(a)
        if g is not None:
            for row in g:
                for v in row:
                    if isinstance(v, Err):
                        return v
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        out.append(float(v))
        else:
            if isinstance(a, Err):
                return a
            if a is None:
                continue
            n = _num(a)
            if isinstance(n, Err):
                return n
            out.append(n)
    return out


def _quartile(arr, q):
    data = _numbers([arr])
    if isinstance(data, Err):
        return data
    q = _num(q)
    if isinstance(q, Err):
        return q
    q = int(q)
    if not data or q < 0 or q > 4:
        return NUM
    s = sorted(data)
    pos = (len(s) - 1) * q / 4
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def _criteria(c):
    """COUNTIF criteria: '=x', '<>x', '<x' ... or a bare value; * and ? wildcards in text equality."""
    if isinstance(c, (int, float)) and not isinstance(c, bool):
        cv = _r15(float(c))
        return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and _r15(float(v)) == cv
    if isinstance(c, bool):
        return lambda v: v is c
    s = _text(c)
    m = re.match(r"^(<>|<=|>=|=|<|>)?(.*)$", s, re.S)
    op, val = m.group(1) or "=", m.group(2)
    try:
        nv = float(val) if val.strip() else None
    except ValueError:
        nv = None
    if op in ("=", "<>"):
        if val == "":
            empty = lambda v: v is None or v == ""
            return empty if op == "=" else (lambda v: not empty(v))
        if nv is not None:
            eq = lambda v: (isinstance(v, (int, float)) and not isinstance(v, bool) and _r15(float(v)) == _r15(nv)) or (isinstance(v, str) and v.strip() == val.strip())
        elif "*" in val or "?" in val:
            rx = re.compile("^" + re.escape(val).replace(r"\*", ".*").replace(r"\?", ".").replace("~.*", r"\*").replace("~.", r"\?") + "$", re.I | re.S)
            eq = lambda v: isinstance(v, str) and bool(rx.match(v))
        else:
            low = val.lower()
            eq = lambda v: isinstance(v, str) and v.lower() == low
        return eq if op == "=" else (lambda v: not eq(v))
    if nv is not None:
        cmp = {"<": lambda x: x < nv, ">": lambda x: x > nv, "<=": lambda x: x <= nv, ">=": lambda x: x >= nv}[op]
        return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and cmp(_r15(float(v)))
    low = val.lower()
    cmp = {"<": lambda x: x < low, ">": lambda x: x > low, "<=": lambda x: x <= low, ">=": lambda x: x >= low}[op]
    return lambda v: isinstance(v, str) and cmp(v.lower())


def _countifs(*pairs):
    if len(pairs) % 2:
        return VALUE
    grids = [(_flat(pairs[i]), _criteria(pairs[i + 1])) for i in range(0, len(pairs), 2)]
    n = len(grids[0][0])
    if any(len(g) != n for g, _ in grids):
        return VALUE
    return float(sum(1 for k in range(n) if all(f(g[k]) for g, f in grids)))


def _index(rng, row, col=None):
    g = _grid(rng)
    if g is None:
        return rng if _num(row) in (0, 1) else REF
    r, c = _num(row), (1.0 if col is None else _num(col))
    for x in (r, c):
        if isinstance(x, Err):
            return x
    r, c = int(r), int(c)
    if len(g) == 1 and col is None:                     # a one-row range: INDEX(range, n) is the n-th column
        r, c = 1, r
    if r < 1 or c < 1 or r > len(g) or c > len(g[0]):
        return REF
    return g[r - 1][c - 1]


def _match(val, rng, kind=1.0):
    if isinstance(val, Err):
        return val
    kind = _num(kind)
    seq = _flat(rng)
    if kind == 0:
        if isinstance(val, str) and ("*" in val or "?" in val):
            f = _criteria(val)
            for i, v in enumerate(seq, 1):
                if f(v):
                    return float(i)
            return NA
        for i, v in enumerate(seq, 1):
            if v is None:
                continue
            if _rank(v) == _rank(val) and _compare(v, val, "=") is True:
                return float(i)
        return NA
    best = None
    for i, v in enumerate(seq, 1):                       # approximate match (sorted data); not used by Jon's workbook
        if v is None or _rank(v) != _rank(val):
            continue
        if (kind > 0 and _compare(v, val, "<=") is True) or (kind < 0 and _compare(v, val, ">=") is True):
            best = float(i)
    return best if best is not None else NA


def _date(serial):
    n = _num(serial)
    if isinstance(n, Err):
        return n
    return EPOCH + dt.timedelta(days=int(n))


def _yearfrac(start, end, basis=0.0):
    """Excel YEARFRAC, basis 0 (US 30/360, NASD) as Excel computes it; 1 actual/actual; 2 actual/360; 3 actual/365."""
    a, b = _date(start), _date(end)
    for x in (a, b):
        if isinstance(x, Err):
            return x
    basis = int(_num(basis))
    if a > b:
        a, b = b, a
    if basis == 0:
        d1, d2 = a.day, b.day
        last_feb = lambda d: d.month == 2 and (d + dt.timedelta(days=1)).month == 3
        if last_feb(a) and last_feb(b):
            d2 = 30
        if last_feb(a):
            d1 = 30
        if d2 == 31 and d1 >= 30:
            d2 = 30
        if d1 == 31:
            d1 = 30
        return ((b.year - a.year) * 360 + (b.month - a.month) * 30 + (d2 - d1)) / 360
    days = (b - a).days
    if basis == 2:
        return days / 360
    if basis == 3:
        return days / 365
    if basis == 1:
        if a.year == b.year:
            return days / (366 if a.year % 4 == 0 and (a.year % 100 != 0 or a.year % 400 == 0) else 365)
        years = range(a.year, b.year + 1)
        avg = sum(366 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 365 for y in years) / len(years)
        return days / avg
    return NUM


def _agg(name):
    def f(*args):
        data = _numbers(args)
        if isinstance(data, Err):
            return data
        if name == "SUM":
            return float(sum(data))
        if name == "MAX":
            return max(data) if data else 0.0
        if name == "MIN":
            return min(data) if data else 0.0
        if name == "AVERAGE":
            return sum(data) / len(data) if data else DIV0
        if name == "MEDIAN":
            if not data:
                return NUM
            s, n = sorted(data), len(data)
            return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
        if name == "PRODUCT":
            if not data:
                return 0.0
            p = 1.0
            for x in data:
                p *= x
            return p
        return VALUE
    return f


def _count(*args):
    n = 0
    for a in args:
        g = _grid(a)
        vals = [v for row in g for v in row] if g is not None else [a]
        n += sum(1 for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool))
    return float(n)


def _large(arr, k):
    data = _numbers([arr])
    if isinstance(data, Err):
        return data
    k = _num(k)
    if isinstance(k, Err):
        return k
    k = int(math.ceil(k))
    if not data or k < 1 or k > len(data):
        return NUM
    return sorted(data, reverse=True)[k - 1]


def _sumproduct(*arrays):
    grids = [_grid(a) if _grid(a) is not None else [[a]] for a in arrays]
    shape = (len(grids[0]), len(grids[0][0]))
    if any((len(g), len(g[0])) != shape for g in grids):
        return VALUE
    total = 0.0
    for r in range(shape[0]):
        for c in range(shape[1]):
            p = 1.0
            for g in grids:
                v = g[r][c]
                if isinstance(v, Err):
                    return v
                p *= float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0
            total += p
    return total


def _logical(kind):
    def f(*args):
        vals = []
        for a in args:
            g = _grid(a)
            if g is not None:
                for row in g:
                    for v in row:
                        if isinstance(v, Err):
                            return v
                        if isinstance(v, bool) or (isinstance(v, (int, float))):
                            vals.append(bool(v))
            else:
                b = _bool(a)
                if isinstance(b, Err):
                    return b
                vals.append(b)
        if not vals:
            return VALUE
        return all(vals) if kind == "AND" else any(vals)
    return f


FUNCS = {"SUM": _agg("SUM"), "MAX": _agg("MAX"), "MIN": _agg("MIN"), "AVERAGE": _agg("AVERAGE"), "MEDIAN": _agg("MEDIAN"),
         "PRODUCT": _agg("PRODUCT"), "COUNT": _count, "COUNTIF": lambda r, c: _countifs(r, c), "COUNTIFS": _countifs,
         "QUARTILE": _quartile, "LARGE": _large, "SUMPRODUCT": _sumproduct, "INDEX": _index, "MATCH": _match,
         "YEAR": lambda s: (lambda d: d if isinstance(d, Err) else float(d.year))(_date(s)), "YEARFRAC": _yearfrac,
         "ROWS": lambda r: float(r.rows) if isinstance(r, Rng) else float(len(r)) if isinstance(r, list) else 1.0,
         "AND": _logical("AND"), "OR": _logical("OR")}
RANGE_ARGS = {"SUM", "MAX", "MIN", "AVERAGE", "MEDIAN", "PRODUCT", "COUNT", "QUARTILE", "LARGE", "SUMPRODUCT", "AND", "OR"}


def _range_arg(name: str, i: int) -> bool:
    """Whether argument i of a function takes a range (a cell reference there is a one-cell range)."""
    return (name in RANGE_ARGS or (name == "INDEX" and i == 0) or (name == "MATCH" and i == 1) or (name == "ROWS" and i == 0)
            or (name in ("COUNTIF", "COUNTIFS") and i % 2 == 0))


# ------------------------------------------------------------------------------------------------ parser
PREC = {"=": 1, "<>": 1, "<": 1, ">": 1, "<=": 1, ">=": 1, "&": 2, "+": 3, "-": 3, "*": 4, "/": 4, "^": 5}
REF_RX = re.compile(r"^(?:(?P<sheet>[^!]+)!)?\$?(?P<c1>[A-Z]{1,3})\$?(?P<r1>\d+)(?::\$?(?P<c2>[A-Z]{1,3})\$?(?P<r2>\d+))?$")


def parse(formula: str, sheet: str):
    items = [t for t in Tokenizer(formula).items if t.type != Token.WSPACE]
    pos = [0]

    def peek():
        return items[pos[0]] if pos[0] < len(items) else None

    def take():
        t = items[pos[0]]
        pos[0] += 1
        return t

    def primary():
        t = take()
        if t.type == "OPERATOR-PREFIX":
            node = primary()
            return ("neg", node) if t.value == "-" else node
        if t.type == "PAREN" and t.subtype == "OPEN":
            node = expr(0)
            take()                                       # ")"
            return node
        if t.type == "FUNC" and t.subtype == "OPEN":
            name, args = t.value[:-1].upper(), []
            if peek() and peek().type == "FUNC" and peek().subtype == "CLOSE":
                take()
                return ("func", name, args)
            while True:
                if peek() and peek().type == "SEP":
                    args.append(("blank",))
                else:
                    args.append(expr(0))
                nt = take()
                if nt.type == "FUNC" and nt.subtype == "CLOSE":
                    break
            return ("func", name, args)
        if t.type == "OPERAND":
            if t.subtype == "NUMBER":
                return ("lit", float(t.value))
            if t.subtype == "TEXT":
                return ("lit", t.value[1:-1].replace('""', '"'))
            if t.subtype == "LOGICAL":
                return ("lit", t.value.upper() == "TRUE")
            if t.subtype == "ERROR":
                return ("lit", ERRS.get(t.value, VALUE))
            m = REF_RX.match(t.value)
            if not m:
                return ("lit", NAME)
            sh = (m.group("sheet") or sheet).strip("'")
            c1, r1 = column_index_from_string(m.group("c1")), int(m.group("r1"))
            if m.group("c2"):
                c2, r2 = column_index_from_string(m.group("c2")), int(m.group("r2"))
                return ("rng", sh, min(r1, r2), min(c1, c2), max(r1, r2), max(c1, c2))
            return ("ref", sh, r1, c1)
        raise ValueError(f"unexpected token {t.value!r} in {formula}")

    def postfix(node):
        while peek() is not None and peek().type == "OPERATOR-POSTFIX":
            take()
            node = ("pct", node)
        return node

    def expr(min_prec):
        left = postfix(primary())
        while True:
            t = peek()
            if t is None or t.type != "OPERATOR-INFIX" or PREC.get(t.value, 0) < min_prec:
                return left
            op = take().value
            right = expr(PREC[op] + 1)
            left = ("bin", op, left, right)

    return expr(0)


# ------------------------------------------------------------------------------------------------ workbook
class Book:
    """Jon's workbook in memory: values and formulas by sheet and cell, evaluated on demand with a per-run cache."""

    def __init__(self, wb):
        self.cells: dict = {}
        for ws in wb.worksheets:
            d = {}
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if v is None:
                        continue
                    if isinstance(v, dt.datetime):
                        v = (v - EPOCH).total_seconds() / 86400
                    elif isinstance(v, dt.date):
                        v = float((dt.datetime(v.year, v.month, v.day) - EPOCH).days)
                    elif isinstance(v, int) and not isinstance(v, bool):
                        v = float(v)
                    d[(c.row, c.column)] = v
            self.cells[ws.title] = d
        self.compiled: dict = {}
        self.cache: dict = {}
        self.blocks: dict = {}

    def set(self, sheet: str, coord: str, value):
        m = REF_RX.match(coord)
        r, c = int(m.group("r1")), column_index_from_string(m.group("c1"))
        if isinstance(value, dt.datetime):
            value = (value - EPOCH).total_seconds() / 86400
        elif isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if value is None:
            self.cells[sheet].pop((r, c), None)
        else:
            self.cells[sheet][(r, c)] = value
        self.compiled.pop((sheet, r, c), None)
        self.cache.clear()
        self.blocks.clear()

    def raw(self, sheet, coord):
        m = REF_RX.match(coord)
        return self.cells[sheet].get((int(m.group("r1")), column_index_from_string(m.group("c1"))))

    def value(self, sheet: str, r: int, c: int):
        key = (sheet, r, c)
        if key in self.cache:
            return self.cache[key]
        v = self.cells.get(sheet, {}).get((r, c))
        if isinstance(v, str) and v.startswith("="):
            node = self.compiled.get(key)
            if node is None:
                node = self.compiled[key] = parse(v, sheet)
            self.cache[key] = None                        # a circular reference reads as blank rather than looping
            v = self.ev(node, sheet)
            if isinstance(v, list):                       # an array result in a single cell: its top-left value
                v = v[0][0] if v and v[0] else None
            elif isinstance(v, Rng):
                v = v.values()[0][0] if v.rows and v.cols else None
            if v is None:                                 # a formula that lands on a blank cell shows 0, as in Excel
                v = 0.0
        self.cache[key] = v
        return v

    def block(self, sheet, r1, c1, r2, c2):
        key = (sheet, r1, c1, r2, c2)
        if key not in self.blocks:
            self.blocks[key] = [[self.value(sheet, r, c) for c in range(c1, c2 + 1)] for r in range(r1, r2 + 1)]
        return self.blocks[key]

    def evaluate(self, address: str):
        sheet, coord = address.split("!")
        m = REF_RX.match(coord)
        return self.value(sheet, int(m.group("r1")), column_index_from_string(m.group("c1")))

    def ev(self, node, sheet):
        kind = node[0]
        if kind == "lit":
            return node[1]
        if kind == "ref":
            return self.value(node[1], node[2], node[3])
        if kind == "rng":
            return Rng(self, *node[1:])
        if kind == "blank":
            return None
        if kind == "neg":
            v = self.ev(node[1], sheet)
            return _broadcast(v, None, lambda x, _: (lambda n: n if isinstance(n, Err) else -n)(_num(x)))
        if kind == "pct":
            v = self.ev(node[1], sheet)
            return _broadcast(v, None, lambda x, _: (lambda n: n if isinstance(n, Err) else n / 100)(_num(x)))
        if kind == "bin":
            a, b = self.ev(node[2], sheet), self.ev(node[3], sheet)
            if isinstance(a, Rng) and a.rows == a.cols == 1:
                a = a.values()[0][0]
            if isinstance(b, Rng) and b.rows == b.cols == 1:
                b = b.values()[0][0]
            return _broadcast(a, b, lambda x, y: _arith(x, y, node[1]))
        if kind == "func":
            name, args = node[1], node[2]
            if name == "IF":
                cond = self.ev(args[0], sheet)
                cond = cond.values()[0][0] if isinstance(cond, Rng) else cond
                b = _bool(cond)
                if isinstance(b, Err):
                    return b
                if b:
                    return self.ev(args[1], sheet) if len(args) > 1 else True
                return self.ev(args[2], sheet) if len(args) > 2 else False
            if name == "IFERROR":
                v = self.ev(args[0], sheet)
                if isinstance(v, Rng) and v.rows == v.cols == 1:
                    v = v.values()[0][0]
                return self.ev(args[1], sheet) if isinstance(v, Err) else v
            f = FUNCS.get(name)
            if f is None:
                return NAME
            vals = []
            for i, a in enumerate(args):
                ranged = _range_arg(name, i)
                if a[0] == "ref" and ranged:                 # a cell reference counts like a one-cell range
                    vals.append(Rng(self, a[1], a[2], a[3], a[2], a[3]))
                    continue
                v = self.ev(a, sheet)
                if isinstance(v, Rng) and not ranged and v.rows == v.cols == 1:
                    v = v.values()[0][0]
                vals.append(v)
            try:
                return f(*vals)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                return VALUE
        return VALUE


def address(sheet: str, r: int, c: int) -> str:
    return f"{sheet}!{get_column_letter(c)}{r}"
