from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = None
retriever = None

class Chat:
    def __init__(self, llm, retriever, 
                 prompt ="Bạn là trợ lý giúp trả lời câu hỏi về Y tế."):
        
        self.llm = llm
        self.retriever = retriever
        self.prompt = prompt   
        self.hisroty = []

        prompt_search_query = ChatPromptTemplate.from_messages([
            ("system", "Bạn là trợ lý giúp tạo truy vấn tìm kiếm dựa trên lịch sử trò chuyện."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "Dựa trên lịch sử trò chuyện ở trên và câu hỏi mới của tôi: {input}, tạo một câu hỏi độc lập nắm bắt được bản chất của những gì tôi đang hỏi, để có thể sử dụng câu hỏi đó để thu thập thông tin từ cơ sở kiến ​​thức của chúng tôi.")
        ])

        # Tạo retriever nhận biết lịch sử
        history_aware_retriever = create_history_aware_retriever(llm, retriever, prompt_search_query)  # Tạo chuỗi nhận biết lịch sử

        # Định nghĩa prompt cuối cùng để kết hợp tài liệu
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt + "Bạn có quyền truy cập vào một số ngữ cảnh từ cơ sở kiến thức của chúng tôi: {context}."),
            MessagesPlaceholder(variable_name="chat_history"),  # Chèn lịch sử trò chuyện
            ("user", "{input}"),  # Thêm câu hỏi hiện tại
        ])

        # Tạo chuỗi kết hợp tài liệu
        combine_docs_chain = create_stuff_documents_chain(llm, final_prompt, document_variable_name="context")  # Kết hợp tài liệu vào prompt

        # Tạo chuỗi truy xuất toàn diện
        self.qa_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)  # Kết hợp retriever và chuỗi kết hợp
    
    def answer(self, question):
        # Thêm câu hỏi hiện tại vào lịch sử
        self.hisroty.append(("user", question))
        # Gọi qa_chain với câu hỏi và lịch sử hiện tại
        result = self.qa_chain.invoke({"input": question, "chat_history": self.hisroty})
        # Lấy câu trả lời
        answer = result['answer']
        # Thêm câu trả lời vào lịch sử
        self.hisroty.append(("assistant", answer))
        return answer

    def start_conversation(self):
        while True:
            question = input("Câu hỏi: ")
            if question == "exit":
                break
            answer = self.answer(question)
            print(f"Trả lời: {answer}\n")