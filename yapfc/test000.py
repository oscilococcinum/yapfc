from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from uuid import uuid4, UUID
import re
from sympy.parsing.sympy_parser import parse_expr, auto_symbol
from sympy import solve #type: ignore
from time import time

type SymPyExpr = Any
type SymPySymbol = Any

def spParseExpr(expr: str, local_dict: dict[str, SymPyExpr] | None = None) -> SymPyExpr:
    return parse_expr(expr, local_dict=local_dict)

def spSolve(spExpre: SymPyExpr, arg: SymPySymbol | None = None) -> list[float]:
    if arg:
        result: list[float] = solve(spExpre, arg) #type: ignore
    else:
        result: list[float] = solve(spExpre) #type: ignore
    return [float(i) for i in result] #type: ignore

class ExpressionType(Enum):
    Assigment = auto()
    Equality = auto()
    Compute = auto()
    Undefined = auto()


@dataclass
class Expression:
    solver: "Solver"
    _inStream: str
    varName: str = ""
    exStream: str = ""
    evalType: ExpressionType = ExpressionType.Undefined
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.defineExprType()
        if self.evalType == ExpressionType.Assigment:
            self.defineVarName()
        else:
            self.varName = ""
        self.updateSelfInVarDict()
        self.evaluateExStream()
        self.updateSelfInVarDict(extSource=True) #Update vardict with extVaules

    def defineExprType(self) -> None:
        split1 = re.split(r':=', self.inStream)
        split2 = re.split(r'=', self.inStream)
        if len(split1) == 2:
            self.evalType = ExpressionType.Assigment
        elif len(split2) == 2:
            self.evalType = ExpressionType.Equality
        elif len(split2) == 1:
            self.evalType = ExpressionType.Compute
        else:
            self.evalType = ExpressionType.Undefined

    def defineVarName(self) -> list[str]:
        split2 = re.split(r':=', self.inStream)
        self.varName = split2[0]
        return split2

    def evaluateExStream(self) -> None:
        match self.evalType:
            case ExpressionType.Assigment:
                stream  = re.split(r':=', self.inStream)[1]
                self.exStream = str(spParseExpr(stream, self.solver.varDict))
            case ExpressionType.Equality:
                lh, rh = re.split(r'=', self.inStream)
                oneSideStream = f'{rh}-({lh})'
                oneSideParsed = spParseExpr(oneSideStream, self.solver.varDict)
                #lhParsed = spParseExpr(lh, self.solver.varDict)
                #rhParsed = spParseExpr(rh, self.solver.varDict)
                self.exStream = str(spSolve(oneSideParsed))
            case ExpressionType.Compute:
                stream = self.inStream
                self.exStream = str(spParseExpr(stream, self.solver.varDict))
            case _:
                return

    def updateSelfInVarDict(self, extSource: bool = False) -> None:
        try:
            self.solver.varDict.pop(self.varName)
        except Exception as e:
            print(e)
        if self.evalType == ExpressionType.Assigment:
            if not extSource:
                split = re.split(r':=', self.inStream)
                self.solver.varDict[split[0]] = spParseExpr(split[1])
            else:
                self.solver.varDict[self.varName] = spParseExpr(self.exStream)

    @property
    def inStream(self) -> str:
        return self._inStream

    @inStream.setter
    def inStream(self, exprStr: str) -> None:
        self._inStream = exprStr
        self.__post_init__()


@dataclass
class Solver:
    expressions: list[Expression]
    varDict: dict[str, SymPyExpr]

    def newExpr(self, expr: str) -> Expression:
        ex = Expression(self, expr)
        self.expressions.append(ex)
        return ex

    def popExpr(self, id: UUID) -> None:
        i = 0
        while i < len(self.expressions):
            if self.expressions[i].id == id:
                self.varDict.pop(self.expressions[i].varName)
                self.expressions.pop(i)
                return None
            else:
                i += 1
        return None

    def getExprById(self, id: UUID) -> Expression | None:
        i = 0
        while i < len(self.expressions):
            if self.expressions[i].id == id:
                return self.expressions[i]
            else:
                i += 1
        return None

    def showAll(self) -> None:
        for i in self.expressions:
            print(i.varName, i.inStream, i.exStream, i.evalType, i.id)

if __name__ == "__main__":
    slv = Solver([], {})
    start = time()
    slv.newExpr("x:=9")
    slv.newExpr("a:=2*x+1")
    slv.newExpr("b:=2*a+1")
    slv.newExpr("q=2*q+8+b")
    slv.newExpr("∫2*q+8+b|0_5")
    slv.showAll()
    end = time()
    print(end - start)