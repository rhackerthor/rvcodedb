#!/usr/bin/env python3
"""
将RISC-V指令JSON转换为空格分隔的CSV文件（无表头）

JSON格式示例：
{
  "add": {
    "encoding": "0000000----------000-----0110011",
    "variable_fields": ["rd", "rs1", "rs2"],
    "extension": ["rv_i"],
    "match": "0x33",
    "mask": "0xfe00707f"
  }
}

输出格式（空格分隔，无表头）：
指令名 extension 编码 variable_fields
add rv_i 0000000??????????000?????0110011 rd rs1 rs2
"""

import json
import sys
import re
import argparse
from typing import Dict, List, Any, Set
from pathlib import Path

def convert_encoding_to_question_marks(encoding: str) -> str:
    """
    将编码字符串中的空格和连字符转换为问号
    
    规则:
    1. 将空格和连字符(-)替换为问号(?)
    2. 保持0和1不变
    """
    # 将空格和连字符替换为问号
    result = []
    for char in encoding:
        if char in '01':
            result.append(char)
        else:
            result.append('?')
    return ''.join(result)

def parse_riscv_json(json_file: str) -> List[Dict[str, str]]:
    """
    解析RISC-V指令JSON文件
    
    返回: 指令列表，每个指令是一个字典
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 输入文件不存在: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式不正确: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        sys.exit(1)
    
    instructions = []
    
    if not isinstance(data, dict):
        print("错误: JSON格式不正确，应为字典格式")
        sys.exit(1)
    
    for instr_name, instr_data in data.items():
        if not isinstance(instr_data, dict):
            # 静默跳过格式不正确的指令
            continue
        
        # 提取字段
        encoding = instr_data.get('encoding', '')
        variable_fields = instr_data.get('variable_fields', [])
        extensions = instr_data.get('extension', [])
        
        # 跳过没有编码的指令
        if not encoding:
            continue
        
        # 处理扩展列表，转换为空格分隔的字符串
        if isinstance(extensions, list):
            # 将扩展名列表转换为空格分隔的字符串
            # 注意：一个指令可能属于多个扩展
            extension_str = ' '.join(extensions)
        else:
            extension_str = str(extensions)
        
        # 转换编码格式
        converted_encoding = convert_encoding_to_question_marks(encoding)
        
        # 处理变量字段列表
        if isinstance(variable_fields, list):
            var_fields_str = ' '.join(variable_fields)
        else:
            var_fields_str = str(variable_fields)
        
        # 添加到指令列表
        instructions.append({
            'name': instr_name,
            'extension': extension_str,
            'encoding': converted_encoding,
            'variable_fields': var_fields_str,
        })
    
    return instructions

def filter_by_extensions(instructions: List[Dict[str, str]], extensions_filter: Set[str]) -> List[Dict[str, str]]:
    """
    按扩展名过滤指令
    
    Args:
        instructions: 指令列表
        extensions_filter: 要保留的扩展名集合
    
    Returns:
        过滤后的指令列表
    """
    if not extensions_filter:
        return instructions
    
    filtered = []
    for instr in instructions:
        # 获取指令的所有扩展名（可能有多个）
        instr_extensions = set(instr['extension'].split())
        # 如果指令的扩展名集合与过滤集合有交集，则保留该指令
        if instr_extensions & extensions_filter:
            filtered.append(instr)
    
    return filtered

def get_all_extensions(instructions: List[Dict[str, str]]) -> Set[str]:
    """
    获取所有唯一的扩展名
    
    Returns:
        所有扩展名的集合
    """
    all_extensions = set()
    for instr in instructions:
        if instr['extension']:
            # 指令可能有多个扩展名，用空格分隔
            for ext in instr['extension'].split():
                all_extensions.add(ext.strip())
    return all_extensions

def generate_space_separated_csv(instructions: List[Dict[str, str]], output_file: str) -> bool:
    """
    生成空格分隔的CSV文件（无表头）
    
    格式:
    指令名 extension 编码 variable_fields
    
    Returns:
        True表示成功，False表示失败
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for instr in instructions:
                # 使用空格分隔四个字段
                line = f"{instr['name']} {instr['extension']} {instr['encoding']} {instr['variable_fields']}\n"
                f.write(line)
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False

def validate_instructions(instructions: List[Dict[str, str]]) -> List[str]:
    """验证指令数据，返回问题列表"""
    issues = []
    
    for i, instr in enumerate(instructions):
        # 检查编码长度（RISC-V指令是32位）
        encoding_len = len(instr['encoding'])
        if encoding_len != 32:
            issues.append(f"指令 '{instr['name']}' 编码长度不是32位: {encoding_len}")
        
        # 检查编码字符是否合法
        if not re.match(r'^[01?]+$', instr['encoding']):
            issues.append(f"指令 '{instr['name']}' 编码包含非法字符: {instr['encoding']}")
    
    return issues

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将RISC-V指令JSON转换为空格分隔的CSV文件（无表头）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i riscv_instructions.json -o output.csv
  %(prog)s -i riscv_instructions.json -o output.csv -e rv_i,rv64_i
  %(prog)s -i riscv_instructions.json -e rv_i,rv64_i,rv32_i
  %(prog)s -i riscv_instructions.json -e "rv_i, rv64_i, rv32_i"
        """
    )
    
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径（必需）')
    parser.add_argument('--output', '-o', default='riscv_instructions.csv', 
                       help='输出CSV文件路径（默认: riscv_instructions.csv）')
    parser.add_argument('--extensions', '-e', 
                       help='按扩展名过滤指令（多个扩展名用逗号分隔，例如：rv_i,rv64_i,rv32_i）')
    parser.add_argument('--list-extensions', '-l', action='store_true',
                       help='列出所有可用的扩展名')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='验证指令数据')
    
    # 如果没有提供任何参数，打印帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # 解析JSON
    instructions = parse_riscv_json(args.input)
    
    if not instructions:
        print("错误: 未找到任何有效指令")
        sys.exit(1)
    
    # 列出所有扩展名（如果指定）
    if args.list_extensions:
        all_extensions = get_all_extensions(instructions)
        if all_extensions:
            print("可用的扩展名:")
            for ext in sorted(all_extensions):
                print(f"  {ext}")
            print(f"总计: {len(all_extensions)} 个扩展名")
        else:
            print("没有找到扩展名")
        sys.exit(0)
    
    # 按扩展名过滤（如果指定）
    original_count = len(instructions)
    if args.extensions:
        try:
            # 解析扩展名参数：去除空格，分割逗号，过滤空字符串
            extensions_list = [ext.strip() for ext in args.extensions.split(',') if ext.strip()]
            if not extensions_list:
                print("错误: 未提供有效的扩展名")
                sys.exit(1)
            
            extensions_set = set(extensions_list)
            
            # 检查扩展名是否存在
            all_extensions = get_all_extensions(instructions)
            invalid_extensions = extensions_set - all_extensions
            if invalid_extensions:
                print(f"警告: 以下扩展名不存在，将被忽略: {', '.join(sorted(invalid_extensions))}")
                # 移除不存在的扩展名
                extensions_set = extensions_set & all_extensions
                if not extensions_set:
                    print(f"错误: 没有有效的扩展名")
                    print(f"可用的扩展名: {', '.join(sorted(all_extensions))}")
                    sys.exit(1)
            
            # 过滤指令
            instructions = filter_by_extensions(instructions, extensions_set)
            
            if not instructions:
                print(f"错误: 过滤后没有找到任何指令")
                print(f"可用的扩展名: {', '.join(sorted(all_extensions))}")
                sys.exit(1)
            
            # 统计信息
            filtered_count = len(instructions)
            print(f"已过滤扩展名: {', '.join(sorted(extensions_set))}")
            print(f"过滤前: {original_count} 条指令")
            print(f"过滤后: {filtered_count} 条指令 (过滤掉 {original_count - filtered_count} 条)")
            
        except Exception as e:
            print(f"扩展名过滤失败: {e}")
            sys.exit(1)
    else:
        print(f"找到 {original_count} 条指令（未过滤）")
    
    # 验证（如果指定）
    if args.validate:
        issues = validate_instructions(instructions)
        if issues:
            print(f"验证发现 {len(issues)} 个问题:")
            for issue in issues[:5]:  # 只显示前5个问题
                print(f"  - {issue}")
            if len(issues) > 5:
                print(f"  ... 还有 {len(issues) - 5} 个问题未显示")
            sys.exit(1)
    
    # 生成空格分隔的CSV
    if generate_space_separated_csv(instructions, args.output):
        print(f"已生成: {args.output}")
        print(f"包含 {len(instructions)} 条指令")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
