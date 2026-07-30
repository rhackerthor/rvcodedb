import json
import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Instruction:
    name: str
    encoding: str
    match: str
    mask: str
    extension: list[str] = field(default_factory=list)
    variable_fields: list[str] = field(default_factory=list)


def _resolve_opcodes_path(config_path: str, project_root: Path) -> Path:
    p = Path(config_path)
    if p.is_absolute():
        return p
    return (project_root / p).resolve()


def get_resolved_opcodes_path(config_path: str, project_root: Path | None = None) -> Path:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent
    return _resolve_opcodes_path(config_path, project_root)


def load_instructions(opcodes_path_config: str, project_root: Path | None = None) -> list[Instruction]:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent

    opcodes_dir = _resolve_opcodes_path(opcodes_path_config, project_root)
    dict_path = opcodes_dir / "instr_dict.json"

    if not dict_path.exists():
        return []

    with open(dict_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    instructions = []
    for name, data in raw.items():
        ext = data.get("extension", [])
        if isinstance(ext, str):
            ext = [ext]
        instructions.append(Instruction(
            name=name.upper(),
            encoding=data.get("encoding", ""),
            match=data.get("match", ""),
            mask=data.get("mask", ""),
            extension=ext,
            variable_fields=data.get("variable_fields", []),
        ))

    instructions.sort(key=lambda i: i.name)
    return instructions


def get_available_extensions(instructions: list[Instruction]) -> list[str]:
    exts: set[str] = set()
    for instr in instructions:
        for e in instr.extension:
            exts.add(e)
    return sorted(exts)


def get_available_variable_fields(instructions: list[Instruction]) -> list[str]:
    fields: set[str] = set()
    for instr in instructions:
        for f in instr.variable_fields:
            fields.add(f)
    return sorted(fields)


def filter_instructions_by_fields(
    instructions: list[Instruction], selected_fields: list[str]
) -> list[Instruction]:
    if not selected_fields:
        return list(instructions)
    sel = set(selected_fields)
    return [i for i in instructions if sel.intersection(i.variable_fields)]


def get_instructions_by_extensions(
    instructions: list[Instruction], selected_extensions: list[str]
) -> list[Instruction]:
    if not selected_extensions:
        return []
    sel = set(selected_extensions)
    return [i for i in instructions if sel.intersection(i.extension)]
