import os
import fitz  # PyMuPDF
from PIL import Image
import frontmatter
import pytesseract
import io
import base64
import re

# 配置参数
INPUT_DIR = r'C:\Users\sunmoon\Desktop\PDF'           # PDF输入目录
OUTPUT_DIR = r'C:\Users\sunmoon\Desktop\MD'      # Obsidian库输出目录
ASSETS_SUBDIR = 'assets'              # 图片存储子目录
ENABLE_OCR = False                    # 是否启用OCR
KEEP_FORMULA = True                   # 是否保留数学公式（简单保留LaTeX块）
PARSE_TOC = False                     # 是否解析目录结构
CONVERT_LINKS = False                 # 是否转换内部链接

def extract_metadata(doc):
    meta = doc.metadata
    return {
        'title': meta.get('title') or '',
        'author': meta.get('author') or '',
        'date': meta.get('creationDate') or '',
    }

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

def remove_empty_tables(md_text):
    # 匹配典型空表格（仅表头和分隔符，无内容）
    pattern = r"\|.*\|\n\|[-\s|:]+\|\n(\n|$)"
    return re.sub(pattern, '', md_text)

def save_image(img, img_dir, base_name, idx):
    img_path = os.path.join(img_dir, f"{base_name}_img{idx}.png")
    img.save(img_path)
    return img_path

def process_table(table):
    """处理表格，确保保持原始矩阵结构"""
    if not table or len(table) == 0:
        return []
    
    # 获取最大列数
    max_cols = max(len(row) for row in table)
    md_table = []
    
    # 处理每一行，保持表格结构
    for row_idx, row in enumerate(table):
        # 补齐空单元格，确保矩阵结构完整
        normalized_row = row + [''] * (max_cols - len(row))
        # 处理单元格内容，保留原始格式
        cells = []
        for cell in normalized_row:
            # 保留单元格原始内容，仅处理特殊字符
            clean_cell = str(cell).strip().replace('|', '\\|')
            if '\n' in clean_cell:
                # 处理多行内容，保持格式
                clean_cell = clean_cell.replace('\n', '<br>')
            cells.append(clean_cell or ' ')  # 空格代替空单元格
        
        # 构建markdown表格行
        md_row = f"| {' | '.join(cells)} |"
        md_table.append(md_row)
        
        # 在第一行后添加分隔行
        if row_idx == 0:
            # 使用冒号标记对齐方式
            separator = f"| {' | '.join(['---'] * max_cols)} |"
            md_table.append(separator)
    
    return md_table

def is_math_formula(text):
    """判断文本是否可能是数学公式"""
    math_symbols = ['\\', '∑', '∫', '√', '±', '∞', '≠', '≤', '≥', '∏', '∆', '∇', '∂', '∈', '∉', '∩', '∪']
    return any(symbol in text for symbol in math_symbols) or \
           (text.count('(') + text.count('{') > 1 and any(c.isdigit() for c in text))

def extract_formula_image(page, span):
    """将公式span区域转换为图片"""
    try:
        bbox = span["bbox"]
        pix = page.get_pixmap(clip=bbox)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    except Exception as e:
        print(f"公式截图失败: {e}")
        return None

def process_math_formula(page, span):
    """处理数学公式为图片"""
    img = extract_formula_image(page, span)
    if img:
        return image_to_base64(img)
    return None

def pdf_to_markdown(pdf_path, output_dir, assets_dir):
    doc = fitz.open(pdf_path)
    meta = extract_metadata(doc)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    md_lines = []
    img_idx = 1

    # Frontmatter
    post = frontmatter.Post('')
    post['title'] = meta['title'] or base_name
    post['author'] = meta['author']
    post['date'] = meta['date']

    for page_num, page in enumerate(doc, 1):
        md_lines.append(f"\n---\n## 第{page_num}页\n")

        try:
            # 使用blocks模式提取文本结构
            blocks = page.get_text("dict")["blocks"]
            current_table = []
            
            for block in blocks:
                # 检查是否为表格块
                if block.get("lines"):
                    text = ""
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            span_text = span.get("text", "").strip()
                            if span_text:
                                # 检查是否是数学公式
                                if is_math_formula(span_text):
                                    if text:  # 先处理之前的普通文本
                                        md_lines.append(text)
                                        text = ""
                                    # 直接用LaTeX语法包裹公式
                                    if len(span_text.split('\n')) == 1:
                                        md_lines.append(f"${span_text}$")
                                    else:
                                        md_lines.append(f"\n$$\n{span_text}\n$$\n")
                                else:
                                    text += span_text + " "
                    
                    if text.strip():  # 处理剩余的普通文本
                        md_lines.append(text.strip())
                        
                    # 表格处理部分保持不变
                    table_data = []
                    current_row = []
                    last_y = None
                    
                    for line in block["lines"]:
                        y = line["bbox"][1]  # y坐标
                        spans = line.get("spans", [])
                        
                        # 新行判断
                        if last_y is not None and abs(y - last_y) > 5:
                            if current_row:
                                table_data.append(current_row)
                                current_row = []
                        
                        # 收集当前行的文本
                        row_text = []
                        for span in spans:
                            if span.get("text"):
                                row_text.append(span["text"])
                        
                        if row_text:
                            current_row.extend(row_text)
                        last_y = y
                    
                    # 添加最后一行
                    if current_row:
                        table_data.append(current_row)
                    
                    # 检查是否为表格（至少2行，每行至少2个单元格）
                    if len(table_data) >= 2 and all(len(row) >= 2 for row in table_data):
                        md_table = process_table(table_data)
                        md_lines.extend(md_table)
                        md_lines.append("")  # 表格后空行
                    else:
                        # 不是表格，作为普通文本处理
                        text = " ".join(" ".join(row) for row in table_data)
                        if text.strip():
                            md_lines.append(text.strip())
                            md_lines.append("")
            
        except Exception as e:
            print(f"处理内容时出错: {e}")
            # 使用普通文本模式作为后备
            text = page.get_text("text")
            md_lines.append(text.strip())

        # 图片提取并嵌入Base64
        for img in page.get_images(full=True):
            xref = img[0]
            base_img = doc.extract_image(xref)
            img_bytes = base_img["image"]
            img_pil = Image.open(io.BytesIO(img_bytes))
            b64_uri = image_to_base64(img_pil)
            md_lines.append(f"![{base_name}_img{img_idx}]({b64_uri})")
            img_idx += 1

    # 合并文本并去除空表格
    md_content = '\n'.join(md_lines)
    md_content = remove_empty_tables(md_content)
    post.content = md_content

    # 写入md文件
    md_path = os.path.join(output_dir, f"{base_name}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))

def batch_convert(input_dir, output_dir, assets_subdir):
    os.makedirs(output_dir, exist_ok=True)
    assets_dir = os.path.join(output_dir, assets_subdir)
    os.makedirs(assets_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, file)
            pdf_to_markdown(pdf_path, output_dir, assets_dir)
            print(f"已转换: {file}")

if __name__ == "__main__":
    batch_convert(INPUT_DIR, OUTPUT_DIR, ASSETS_SUBDIR)