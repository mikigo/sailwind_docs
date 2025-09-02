import os
import re
from pathlib import Path


def remove_markdown_links(content):
    pattern = r'!?\[(.*?)\]\([^)]*\)'
    return re.sub(pattern, r'\1', content)


def process_markdown_files(directory):
    directory = Path(directory)
    if not directory.exists():
        print(f"错误：目录不存在 {directory}")
        return

    for file_path in directory.rglob('*.md'):
        print(f"处理文件: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 移除链接
            new_content = remove_markdown_links(content)

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")


if __name__ == "__main__":
    target_directory = r"D:\sailwind_docs\docs"
    process_markdown_files(target_directory)
    print("处理完成！所有Markdown链接已移除。")