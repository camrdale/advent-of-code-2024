import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


REGISTER = re.compile(r'Register ([ABC]): ([0-9]*)')
PROGRAM = re.compile(r'Program: ([0-9,]*)')


@dataclass
class State:
    A: int
    B: int
    C: int
    instruction_pointer: int = field(default=0)
    out: list[int] = field(default_factory=list)

    def combo_operand(self, operand: int) -> int:
        assert(operand < 7)
        if operand <= 3:
            return operand
        elif operand == 4:
            return self.A
        elif operand == 5:
            return self.B
        return self.C


class Operation(ABC):
    @abstractmethod
    def execute(self, operand: int, state: State) -> None:
        pass


class adv(Operation):
    opcode = 0

    def execute(self, operand: int, state: State) -> None:
        state.A = state.A // (2**state.combo_operand(operand))
        state.instruction_pointer += 2


class bxl(Operation):
    opcode = 1

    def execute(self, operand: int, state: State) -> None:
        state.B = state.B ^ operand
        state.instruction_pointer += 2


class bst(Operation):
    opcode = 2

    def execute(self, operand: int, state: State) -> None:
        state.B = state.combo_operand(operand) % 8
        state.instruction_pointer += 2


class jnz(Operation):
    opcode = 3

    def execute(self, operand: int, state: State) -> None:
        if state.A == 0:
            state.instruction_pointer += 2
        else:
            state.instruction_pointer = operand


class bxc(Operation):
    opcode = 4

    def execute(self, operand: int, state: State) -> None:
        state.B = state.B ^ state.C
        state.instruction_pointer += 2


class out(Operation):
    opcode = 5

    def execute(self, operand: int, state: State) -> None:
        state.out.append(state.combo_operand(operand) % 8)
        state.instruction_pointer += 2


class bdv(Operation):
    opcode = 6

    def execute(self, operand: int, state: State) -> None:
        state.B = state.A // (2**state.combo_operand(operand))
        state.instruction_pointer += 2


class cdv(Operation):
    opcode = 7

    def execute(self, operand: int, state: State) -> None:
        state.C = state.A // (2**state.combo_operand(operand))
        state.instruction_pointer += 2


class Program:
    operations: dict[int, type[Operation]] = {
        adv.opcode: adv,
        bxl.opcode: bxl,
        bst.opcode: bst,
        jnz.opcode: jnz,
        bxc.opcode: bxc,
        out.opcode: out,
        bdv.opcode: bdv,
        cdv.opcode: cdv,
    }

    def __init__(self, program: str):
        self.instructions = list(map(int, program.split(',')))
    
    def execute(self, state: State) -> None:
        while state.instruction_pointer < len(self.instructions):
            operation = Program.operations[self.instructions[state.instruction_pointer]]()
            operand = self.instructions[state.instruction_pointer + 1]
            operation.execute(operand, state)


def parse(input: Iterable[str]) -> tuple[State, Program]:
    registers: dict[str, Any] = {}
    program = None
    for line in input:
        if line.strip() == '':
            continue
        if match := REGISTER.match(line):
            registers[match.group(1)] = int(match.group(2))
        elif match := PROGRAM.match(line):
            program = Program(match.group(1))
        else:
            print('ERROR unmatched input line:', line)
    assert(program is not None)
    return State(**registers), program