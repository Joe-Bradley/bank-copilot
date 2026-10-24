from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).resolve().parent / "knowledge" / "products.md"

#加载产品知识内容，返回一个字符串列表，每个字符串是一个产品知识内容的段落
def load_product_sections() -> list[str]:
    text = KNOWLEDGE_PATH.read_text(encoding="utf-8")

    return [section.strip() for section in text.split("## ")[1:]]

#输入问题和历史对话，返回匹配的产品知识内容，如果没有匹配的内容，返回None
#question是用户输入的问题，history是用户和助手的历史对话，history是一个字典列表，每个字典有两个键，role和content，分别对应ChatMessage对象的role和content属性
def retrieve_product_context(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str | None:
    search_texts = [question]

    #如果history不为空，把history里role为"user"的content按时间倒序加入search_texts，假设history是按时间顺序排列的，reversed(history)就是按时间倒序排列的
    if history:
        search_texts.extend(
            item["content"] for item in reversed(history) if item["role"] == "user"
        )

    #search_texts里面第一条是用户当前输入的问题，后面是用户历史对话中role为"user"的content，按时间倒序排列
    for search_text in search_texts:
        matched_sections = []

        #遍历产品知识内容的段落，找到标题行中包含search_text的段落，加入matched_sections
        for section in load_product_sections():

            # title_line长这样：星河成长账户 | 星河账户 | 成长账户，
            title_line = section.splitlines()[0]

            #把title_line按"|"分割，去掉首尾空格，得到产品名称列表，长这样：["星河成长账户", "星河账户", "成长账户"]
            product_names = [name.strip() for name in title_line.split("|")]

            #如果任意产品名称出现在search_text中，就把该段落加入matched_sections
            if any(name in search_text for name in product_names):
                matched_sections.append(f"## {section}")

        if matched_sections:
            return "\n\n".join(matched_sections)

    return None
