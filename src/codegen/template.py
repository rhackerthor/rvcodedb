from pathlib import Path

from src.models.profile import Profile, Decoder
from src.codegen.templates.ctrl_enum import (
    CTRL_ENUM_TEMPLATE,
    GROUP_VAL_TEMPLATE,
    GROUP_DEF_TEMPLATE,
    INSTR_LINE_TEMPLATE,
    MAP_ENTRY_TEMPLATE,
    DECODER_FIELDS_TEMPLATE,
)
from src.codegen.insts_scala import generate_insts_scala_from_chisel


def generate_decoder_code(profile: Profile, decoder: Decoder) -> str:
    groups_vals_parts = []
    groups_defs_parts = []
    map_entries_parts = []

    for group in decoder.groups:
        groups_vals_parts.append(
            GROUP_VAL_TEMPLATE.replace("%GROUP_NAME%", group.name)
        )

        instr_lines = []
        for instr in group.instructions:
            instr_lines.append(
                INSTR_LINE_TEMPLATE.replace("%INSTR%", instr)
            )
        groups_defs_parts.append(
            GROUP_DEF_TEMPLATE.replace("%GROUP_NAME%", group.name).replace(
                "%INSTRUCTIONS%", "\n".join(instr_lines)
            )
        )

        map_entries_parts.append(
            MAP_ENTRY_TEMPLATE.replace("%NAME%", decoder.name).replace(
                "%GROUP_NAME%", group.name
            )
        )

    code = CTRL_ENUM_TEMPLATE.replace("%PACKAGE%", profile.package_name)
    code = code.replace("%NAME%", decoder.name)
    code = code.replace("%MODE%", decoder.ctrl_enum_mode)
    code = code.replace("%GROUPS_VALS%", "\n".join(groups_vals_parts))
    code = code.replace("%GROUPS_DEFS%", "\n".join(groups_defs_parts))
    code = code.replace("%MAP_ENTRIES%", "\n".join(map_entries_parts))

    return code


def generate_decoder_aggregator_code(profile: Profile) -> str:
    field_names = []
    for decoder in profile.decoders:
        field_names.append(f"      {decoder.name}Field,")

    field_list = "\n".join(field_names) if field_names else "      "

    code = DECODER_FIELDS_TEMPLATE.replace("%PACKAGE%", profile.package_name)
    code = code.replace("%FIELD_LIST%", field_list)
    return code


def generate_all_code(profile: Profile) -> dict[str, str]:
    results = {}
    for decoder in profile.decoders:
        filename = f"{decoder.name}Ctrl.scala"
        code = generate_decoder_code(profile, decoder)
        results[filename] = code
    if profile.decoders:
        results["DecodeFields.scala"] = generate_decoder_aggregator_code(profile)
    return results


def export_to_files(
    profile: Profile,
    overwrite: bool = False,
    chisel_path: Path | None = None,
) -> list[str]:
    output_dir = Path(profile.output_path)
    written = []
    generated = generate_all_code(profile)
    for filename, code in generated.items():
        out_path = output_dir / filename
        if not overwrite and out_path.exists():
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        written.append(str(out_path))

    if chisel_path is not None and chisel_path.exists():
        insts_code = generate_insts_scala_from_chisel(chisel_path, profile.package_name)
        insts_path = output_dir / "Instructions.scala"
        if overwrite or not insts_path.exists():
            insts_path.parent.mkdir(parents=True, exist_ok=True)
            with open(insts_path, "w", encoding="utf-8") as f:
                f.write(insts_code)
            written.append(str(insts_path))

    return written
