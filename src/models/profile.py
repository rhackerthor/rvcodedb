from dataclasses import dataclass, field


@dataclass
class Group:
    name: str
    instructions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "instructions": self.instructions}

    @classmethod
    def from_dict(cls, d: dict) -> "Group":
        return cls(name=d["name"], instructions=d.get("instructions", []))


@dataclass
class Decoder:
    name: str
    ctrl_enum_mode: str = "OneHot"
    groups: list[Group] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ctrl_enum_mode": self.ctrl_enum_mode,
            "groups": [g.to_dict() for g in self.groups],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Decoder":
        return cls(
            name=d["name"],
            ctrl_enum_mode=d.get("ctrl_enum_mode", "OneHot"),
            groups=[Group.from_dict(g) for g in d.get("groups", [])],
        )

    def find_group_for_instruction(self, instr_name: str) -> Group | None:
        for g in self.groups:
            if instr_name in g.instructions:
                return g
        return None

    def assign_instruction(self, instr_name: str, group_name: str | None) -> None:
        old_group = self.find_group_for_instruction(instr_name)
        if old_group:
            old_group.instructions.remove(instr_name)
        if group_name:
            for g in self.groups:
                if g.name == group_name:
                    g.instructions.append(instr_name)
                    break

    def validate_no_duplicates(self) -> list[str]:
        seen: dict[str, str] = {}
        conflicts = []
        for g in self.groups:
            for instr in g.instructions:
                if instr in seen:
                    conflicts.append(f"'{instr}' in both '{seen[instr]}' and '{g.name}'")
                seen[instr] = g.name
        return conflicts

    def get_unassigned_instructions(self, all_instr_names: list[str]) -> list[str]:
        assigned = set()
        for g in self.groups:
            assigned.update(g.instructions)
        return [n for n in all_instr_names if n not in assigned]

    def reorder_group(self, from_idx: int, to_idx: int) -> None:
        if 0 <= from_idx < len(self.groups) and 0 <= to_idx < len(self.groups):
            g = self.groups.pop(from_idx)
            self.groups.insert(to_idx, g)


@dataclass
class Profile:
    name: str
    output_path: str = ""
    package_name: str = "mq.util.decoder"
    selected_extensions: list[str] = field(default_factory=list)
    decoders: list[Decoder] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "output_path": self.output_path,
            "package_name": self.package_name,
            "selected_extensions": self.selected_extensions,
            "decoders": [d.to_dict() for d in self.decoders],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Profile":
        return cls(
            name=d["name"],
            output_path=d.get("output_path", ""),
            package_name=d.get("package_name", "mq.util.decoder"),
            selected_extensions=d.get("selected_extensions", []),
            decoders=[Decoder.from_dict(dd) for dd in d.get("decoders", [])],
        )
