import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
from dotenv import load_dotenv
import os

class MultiAssistant:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = os.getenv("MODEL")

    def process_request(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True,
            )

            result = st.empty()
            collected_chunks = []

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    collected_chunks.append(chunk.choices[0].delta.content)
                    result.markdown("".join(collected_chunks))

            return "".join(collected_chunks)

        except Exception as e:
            return f"Error: {str(e)}"


class ResearchAssistant:
    def __init__(self) -> None:
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = os.getenv("MODEL")

    def extract_text(self, uploaded_file):
        text = ""
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = str(uploaded_file.read(), "utf-8")
        return text

    def analyze_content(self, text, query):
        prompt = f"""Analyze this text and answer the following query:
            Text: {text[:2000]}...
            Query: {query}
            
            Provide:
            1. Direct answer to the query
            2. Supporting evidence
            3. Key findings
            4. Limitations of the analysis
            """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant skilled in analyzing academic and technical documents.",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )

            result = st.empty()
            collected_chunks = []

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    collected_chunks.append(chunk.choices[0].delta.content)
                    result.markdown("".join(collected_chunks))

            return "".join(collected_chunks)

        except Exception as e:
            return f"Error: {str(e)}"


def get_system_prompts():
    return {
        # Code Assistant Prompts
        "Code Generation": """You are an expert Python programmer who writes clean, efficient, and well-documented code.
Follow these guidelines:
1. Start with a brief comment explaining the code's purpose
2. Include docstrings for functions
3. Use clear variable names
4. Add inline comments for complex logic
5. Follow PEP 8 style guidelines
6. Include example usage
7. Handle common edge cases""",
        "Code Explanation": """You are a patient and knowledgeable coding tutor.
Analyze the code and explain:
1. Overall purpose and functionality
2. Break down of each major component
3. Key programming concepts used
4. Flow of execution
5. Important variables and functions
6. Any clever techniques or patterns
7. Potential learning points for students""",
        "Code Review": """You are a senior code reviewer with expertise in Python best practices.
Review the code for:
1. Logical errors or bugs
2. Performance optimization opportunities
3. Security vulnerabilities
4. Code style and PEP 8 compliance
5. Error handling improvements
6. Documentation completeness
7. Code modularity and reusability
8. Memory efficiency""",
        # Language Tutor Prompts
        "Grammar Check": """You are an expert English language teacher.
Review the text for:
1. Grammar errors
2. Punctuation mistakes
3. Sentence structure
4. Word choice improvements
5. Style consistency
Provide clear explanations and corrections.""",
        "Vocabulary Enhancement": """You are a vocabulary expert.
Analyze the text and:
1. Suggest more sophisticated alternatives
2. Explain idioms and phrases
3. Provide context for word usage
4. Suggest synonyms and antonyms
5. Explain connotations""",
        # Document Generator Prompts
        "Business Proposal": """You are a professional business writer.
Generate a proposal that includes:
1. Executive summary
2. Problem statement
3. Proposed solution
4. Timeline and milestones
5. Budget breakdown
6. Risk assessment
7. Expected outcomes""",
        "Professional Email": """You are an expert in business communication.
Create an email that:
1. Has a clear subject line
2. Maintains professional tone
3. Is concise and focused
4. Includes call to action
5. Has appropriate closing
6. Follows email etiquette""",
        # Research Assistant Prompt
        "Document Analysis": """You are a research assistant skilled in analyzing academic and technical documents.
Analyze the text and answer the query.
Provide:
1. Direct answer to the query
2. Supporting evidence
3. Key findings
4. Limitations of the analysis""",
    }


def get_example_prompts():
    return {
        # Code Assistant Examples
        "Code Generation": {
            "placeholder": "使用tkinter 来制作一个图形化的贪吃蛇游戏",
            "default": "",
        },
        "Code Explanation": {
            "placeholder": "请给我代码,我来帮你解释",
            "default": "",
        },
        "Code Review": {"placeholder": "请给我代码，我来帮你审查", "default": ""},
        # Language Tutor Examples
        "Grammar Check": {"placeholder": "请输入需要进行语法检查的文本", "default": ""},
        "Vocabulary Enhancement": {
            "placeholder": "请输入需要进行更专业表达的文本",
            "default": "",
        },
        # Document Generator Examples
        "Business Proposal": {
            "placeholder": "请描述你的商业需求",
            "default": "",
        },
        "Professional Email": {
            "placeholder": "请输入email的需求和目标",
            "default": "",
        },
        # Research Assistant Example
        "Document Analysis": {
            "placeholder": "输入您对文档的查询问题，例如：主要发现是什么？",
            "default": "",
        },
    }


def main():
    st.set_page_config(page_title="智能助手小锐", page_icon="🤖", layout="wide")
    st.title("🤖 多功能AI")

    # 工具分类配置
    tool_categories = {
        "Code Assistant": ["Code Generation", "Code Explanation", "Code Review"],
        "Language Tutor": ["Grammar Check", "Vocabulary Enhancement"],
        "Document Generator": ["Business Proposal", "Professional Email"],
        "Research Assistant": ["Document Analysis"],
    }

    # 侧边栏
    st.sidebar.title("工具选择")
    category = st.sidebar.selectbox("工具类目", list(tool_categories.keys()))
    mode = st.sidebar.selectbox("工具", tool_categories[category])

    # 系统提示词和示例
    system_prompts = get_system_prompts()
    example_prompts = get_example_prompts()

    # 侧边栏说明
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**当前工具**: {mode}")
    st.sidebar.markdown("**工具描述:**")
    st.sidebar.markdown(system_prompts[mode].replace("\n", "\n\n"))

    # 主内容区布局
    col1, col2 = st.columns([2, 3])

    # 左侧输入区域
    with col1:
        st.markdown(f"### {mode}输入")

        if category == "Research Assistant":
            uploaded_files = st.file_uploader(
                "📁 上传研究文档（支持PDF/DOCX/TXT）",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
            )
            user_prompt = st.text_area(
                "❓ 输入查询问题",
                height=150,
                placeholder=example_prompts[mode]["placeholder"],
            )
        else:
            user_prompt = st.text_area(
                "📝 输入内容",
                height=300,
                placeholder=example_prompts[mode]["placeholder"],
                value=example_prompts[mode]["default"],
            )

        process_button = st.button(
            "🚀 执行处理", type="primary", use_container_width=True
        )

    # 右侧输出区域
    with col2:
        st.markdown("### 输出结果")
        output_container = st.container()

    # 处理按钮逻辑
    if process_button:
        if category == "Research Assistant":
            if not uploaded_files:
                st.warning("请先上传文档文件！")
            else:
                with st.spinner("正在分析文档..."):
                    assistant = ResearchAssistant()
                    with output_container:
                        for file in uploaded_files:
                            with st.expander(f"📄 文档分析报告 - {file.name}"):
                                text = assistant.extract_text(file)

                                tab1, tab2, tab3 = st.tabs(
                                    ["深度分析", "关键摘录", "全文摘要"]
                                )
                                with tab1:
                                    assistant.analyze_content(text, user_prompt)
                                with tab2:
                                    assistant.analyze_content(
                                        text, "提取关键点和核心论据"
                                    )
                                with tab3:
                                    assistant.analyze_content(text, "生成结构化摘要")

                        if len(uploaded_files) > 1:
                            st.subheader("📊 跨文档分析结论")
                            st.info("多文档交叉比对功能开发中，敬请期待！")

        else:  # 原有处理逻辑
            if user_prompt:
                with st.spinner("处理中..."):
                    assistant = MultiAssistant()
                    with output_container:
                        assistant.process_request(system_prompts[mode], user_prompt)
            else:
                st.warning("⚠️ 请输入有效内容！")

    # 页脚
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center">Made with ❤️ using DeepSeek R1 and Ollama</div>',
        unsafe_allow_html=True,
    )



if __name__ == "__main__":
    main()
