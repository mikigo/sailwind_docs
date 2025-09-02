import os
import re
from collections import defaultdict
import concurrent.futures


def extract_headings(file_path):
    """提取文件中的一级到四级标题及其锚点ID"""
    headings = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配一级到四级标题（格式：# 标题 {#id}）
    pattern = r'^(#{1,4})\s+(.+?)\s*\\{#([\d\-]+)\}'
    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        anchor_id = match.group(3)
        headings.append((text, anchor_id, level))
    return headings


# def process_file(file_path, all_headings,target_files):
def process_file(file_path, all_headings,base_prefix):
    """处理单个文件，添加标题链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查当前文件是否需要处理
    # if file_path not in target_files:
    #     return content  # 不需要处理，直接返回原始内容

    skip_positions = []
    # 1. 跳过标题行本身，用正则表达式匹配任意等级的标题，无论是否存在换行符
    for match in re.finditer(r'^(#{1,4}[^\n]*)', content, re.MULTILINE):
        skip_positions.append((match.start(), match.end()))

    # 2. 跳过已有链接（避免重复添加）
    for match in re.finditer(r'\[.*?\]\(.*?\)', content):
        skip_positions.append((match.start(), match.end()))

    # 3. 跳过以":::"开头的文本块
    for match in re.finditer(r'^:::[^\n]*(\n[^\n]*)*', content, re.MULTILINE):
        skip_positions.append((match.start(), match.end()))

    # 按长度降序排序标题文本
    sorted_headings = sorted(
        [(text, anchor_id, file)
         for file, headings in all_headings.items()
         for text, anchor_id, _ in headings
         if len(text.strip()) >= 5], # 限制一下，超过四个字的标题就不做匹配了

        key=lambda x: len(x[0]),
        reverse=True
    )

    # 构建替换映射
    text_mapping = defaultdict(list)
    for text, anchor_id, file in sorted_headings:
        text_mapping[text].append((anchor_id, file))

    # 构建所有标题文本的正则表达式,降序排列，确保先匹配到最长的词汇，避免出现语义错误
    if not text_mapping:
        return content  # 没有标题，直接返回

    # 转义标题文本中的特殊字符
    escaped_texts = [re.escape(text) for text in text_mapping.keys()]
    # 按长度降序排序，这不比冒泡排序好用
    escaped_texts.sort(key=len, reverse=True)
    # 构建正则表达式模式
    pattern = re.compile('|'.join(escaped_texts))

    # 逐个替换匹配的文本
    new_content = []
    last_index = 0
    for match in pattern.finditer(content):
        start, end = match.start(), match.end()
        text = match.group(0)

        # 检查是否在标题行中
        in_heading = any(skip_start <= start < skip_end for skip_start, skip_end in skip_positions)
        if in_heading:
            continue

        # 查找匹配的标题
        if text in text_mapping:
            # 优先匹配当前文件的标题
            current_file_headings = [h for h in text_mapping[text] if h[1] == file_path]
            if current_file_headings:
                anchor_id, _ = current_file_headings[0]
                link = f'[{text}](#{anchor_id})'
            else:
                # def normalize_absolute_path(target_path):
                #     """规范化绝对路径，去除../和./"""
                #     # 获取绝对路径并规范化
                #     abs_path = os.path.abspath(target_path)
                #     # 分解路径并过滤掉.和..
                #     parts = []
                #     for part in abs_path.split(os.sep):
                #         if part == '..':
                #             if parts:
                #                 parts.pop()
                #         elif part != '.' and part:  # 忽略空部分和当前目录
                #             parts.append(part)
                #     # 重新组合路径并统一斜杠
                #     clean_path = '/' + '/'.join(parts)  # 添加根斜杠
                #     return clean_path
                #
                # anchor_id, target_file = text_mapping[text][0]
                # abs_path = normalize_absolute_path(target_file)  # 直接使用目标文件路径
                # link = f'[{text}]({abs_path}#{anchor_id})'
                def remove_base_prefix(path, base_prefix):
                    """移除特定的前缀，确保项目的跳转链接是从文件的对应根目录开始的"""
                    # 绝对路径
                    abs_path = os.path.abspath(path)
                    # 移除指定前缀
                    normalized_prefix = os.path.normpath(base_prefix)
                    if abs_path.startswith(normalized_prefix):
                        # 移除前缀并保留后续路径
                        rel_path = abs_path[len(normalized_prefix):]
                        # 处理路径分隔符并确保以/开头
                        clean_path = rel_path.replace(os.sep, '/').lstrip('/')
                        return f'/{clean_path}' if clean_path else '/'
                    return abs_path.replace(os.sep, '/')

                anchor_id, target_file = text_mapping[text][0]
                clean_path = remove_base_prefix(target_file, base_prefix)
                link = f'[{text}]({clean_path}#{anchor_id})'
            # 添加替换段
            new_content.append(content[last_index:start])
            new_content.append(link)
            last_index = end

    # 添加剩余内容
    new_content.append(content[last_index:])
    return ''.join(new_content)


# def main():
#     root_dir = r'D:\downloads\sailwind_docs\docs'
#     all_headings = defaultdict(list)  # 文件路径 -> 标题列表
#
#     # 收集所有标题
#     for root, _, files in os.walk(root_dir):
#         for file in files:
#             if file.endswith('zh.md'):
#                 file_path = os.path.join(root, file)
#                 headings = extract_headings(file_path)
#                 if headings:
#                     all_headings[file_path] = headings
#
#     # 并行处理文件
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
#         for file_path in all_headings.keys():
#             futures.append(executor.submit(process_file, file_path, all_headings))
#
#         # 保存修改后的文件
#         for future, file_path in zip(concurrent.futures.as_completed(futures), all_headings.keys()):
#             new_content = future.result()
#             with open(file_path, 'w', encoding='utf-8') as f:
#                 f.write(new_content)
#             print(f'Processed: {file_path}')
def main(root_dir,base_prefix):
    all_headings = defaultdict(list)  # 文件路径 -> 标题列表

    # 收集所有标题
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('zh.md'):
                file_path = os.path.join(root, file)
                headings = extract_headings(file_path)
                if headings:
                    all_headings[file_path] = headings

        # 定义需要添加锚点的目标文件
    target_files = [
        r'D:\downloads\sailwind_docs\docs\layout\guide\2_zh.md',
        r'D:\downloads\sailwind_docs\docs\router\guide\6_zh.md',
        # 添加更多需要处理的文件路径...
    ]

    # # 处理指定文件，需要在 process_file()多传入一个参数target_file
    # for file_path in all_headings.keys():
    #     new_content = process_file(file_path, all_headings, target_files)
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         f.write(new_content)
    #     if file_path in target_files:
    #         print(f'已添加锚点: {file_path}')
    #     else:
    #         print(f'跳过处理: {file_path}')

    # 顺序处理每个文件
    for file_path in all_headings.keys():
        new_content = process_file(file_path, all_headings,base_prefix)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'正在处理: {file_path}')


if __name__ == '__main__':
    root_dir = r'D:\sailwind_docs\docs'
    base_prefix = root_dir

    # 定义需要单独处理的子文件夹列表
    sub_dirs = ['router', 'layout', 'logic', 'lpcreator']
    # main(root_dir, base_prefix)  # 不需要整个目录的处理

    # 分别处理每个子目录
    for sub_dir in sub_dirs:
        sub_dir_path = os.path.join(root_dir, sub_dir)
        if os.path.exists(sub_dir_path):
            print(f"\n{'=' * 50}\nProcessing subdirectory: {sub_dir}\n{'=' * 50}")
            main(sub_dir_path, base_prefix)
        else:
            print(f"未找到该目录: {sub_dir_path}")