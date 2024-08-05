import sys
import os
import gradio as gr
import pdfplumber

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, LOG
from translator import PDFTranslator, TranslationConfig

def get_pdf_page_count(file_path):
    with pdfplumber.open(file_path) as pdf:
        return len(pdf.pages)


def translation(input_file, source_language, target_language, translation_style, page_limit):
    LOG.debug(f"[翻译任务]\n源文件: {input_file.name}\n源语言: {source_language}\n目标语言: {target_language}\n翻译风格: {translation_style}\n页数限制: {page_limit}")
    
    total_pages = get_pdf_page_count(input_file.name)
    LOG.debug(f"总页数: {total_pages}")
    if page_limit is None or page_limit == "" or page_limit <= 0 or int(page_limit) > total_pages:
        pages_to_translate = None
        LOG.debug(f"将翻译全部 {total_pages} 页")
    else:
        pages_to_translate = int(page_limit)
        LOG.debug(f"将翻译前: {pages_to_translate} 页")

    output_file_path = Translator.translate_pdf(
        input_file.name, 
        source_language=source_language, 
        target_language=target_language,
        translation_style=translation_style,
        pages=pages_to_translate
    )

    return output_file_path

def launch_gradio(args):
    translation_styles = ["标准", "小说", "新闻稿", "学术", "诗歌", "幽默", "搞笑", "科幻"]

    iface = gr.Interface(
        fn=translation,
        title="OpenAI-Translator v3.0(PDF 电子书风格化翻译工具)",
        inputs=[
            gr.File(label="上传PDF文件"),
            gr.Textbox(label="源语言（默认：英文）", placeholder="English", value="English"),
            gr.Textbox(label="目标语言（默认：中文）", placeholder="Chinese", value="Chinese"),
            gr.Dropdown(label="翻译风格", choices=translation_styles, value="标准"),
            gr.Number(label="翻译页数限制（留空或输入0表示翻译全部）", precision=0)
        ],
        outputs=[
            gr.File(label="下载翻译文件")
        ],
        allow_flagging="never"
    )

    iface.launch(share=True, server_name="0.0.0.0")

def initialize_translator():
    # 解析命令行
    argument_parser = ArgumentParser()
    # 添加 --reload 参数
    
    args = argument_parser.parse_arguments()

    LOG.debug(f"解析的命令行参数: {args}")

    # 初始化配置单例
    config = TranslationConfig()
    config.initialize(args)    
    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    global Translator
    Translator = PDFTranslator(config.model_name)

    return args

if __name__ == "__main__":
    # 初始化 translator
    args = initialize_translator()
    # 启动 Gradio 服务
    launch_gradio(args)
