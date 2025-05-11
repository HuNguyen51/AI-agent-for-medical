from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class Chat:
    def __init__(self, llm, retriever, prompt):
        """
        Khởi tạo đối tượng Chat, bao gồm mô hình ngôn ngữ, retriever và câu prompt

        Args:
            llm (BaseLanguageModel): Mô hình ngôn ngữ dùng để xử lý truy vấn.
            retriever (BaseRetriever): Retriever dùng để truy hồi những tài liệu liên quan.
            prompt (ChatPromptTemplate): Câu prompt dùng để tìm tài liệu (câu hỏi từ người dùng).
        """
        self.llm = llm
        self.retriever = retriever
        self.prompt = prompt   
        self.history = []

        # Khởi tạo các chuỗi xử lý
        self._initialize_chains()

    def _initialize_chains(self):
        # Prompt để tạo truy vấn tìm kiếm
        prompt_search_query = ChatPromptTemplate.from_messages([
            ("system", "Bạn là trợ lý giúp tạo truy vấn tìm kiếm dựa trên lịch sử trò chuyện."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "Dựa trên lịch sử trò chuyện và câu hỏi này của tôi: {input}, tạo một câu hỏi mới độc lập nắm bắt được bản chất của những gì tôi đang hỏi, để có thể sử dụng câu hỏi đó để thu thập thông tin từ cơ sở kiến thức của chúng tôi.")
        ])
        # Tạo retriever nhận biết lịch sử
        history_aware_retriever = create_history_aware_retriever(
            self.llm, 
            self.retriever, 
            prompt_search_query
        ) # Khi người dùng đặt câu hỏi tiếp theo như "Còn về vấn đề kia thì sao?" hoặc "Giải thích chi tiết hơn về điều đó", hệ thống cần hiểu "vấn đề kia" hoặc "điều đó" đề cập đến gì trong lịch sử đối thoại
        

        # Định nghĩa prompt cuối cùng để kết hợp tài liệu
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", f"{self.prompt} Bạn có quyền truy cập vào một số ngữ cảnh từ cơ sở kiến thức của chúng tôi: {{context}}."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        # Tạo chuỗi kết hợp tài liệu
        combine_docs_chain = create_stuff_documents_chain(
            self.llm, 
            final_prompt, 
            document_variable_name="context"
        )
        
        # Tạo chuỗi truy xuất toàn diện
        self.qa_chain = create_retrieval_chain(
            history_aware_retriever, 
            combine_docs_chain
        )
    
    def answer(self, question):
        """
        Trả lời câu hỏi của người dùng dựa trên lịch sử đoạn chat và cơ sở kiến thức.

        Args:
            question (str): Câu hỏi của User.

        Returns:
            str: Câu trả lời của hệ thống từ câu hỏi của User.
        """
        # Thêm câu hỏi hiện tại vào lịch sử
        self.history.append(("user", question))
        # Gọi qa_chain với câu hỏi và lịch sử hiện tại
        result = self.qa_chain.invoke({"input": question, "chat_history": self.history})
        # Lấy câu trả lời
        answer = result['answer']
        # Thêm câu trả lời vào lịch sử
        self.history.append(("assistant", answer))
        return answer

    def start_conversation(self):
        """
        Bắt đầu cuộc trò chuyện với AI Health Care Assistant
        """
        print("Bắt đầu cuộc trò chuyện (nhập 'exit' để thoát):")
        while True:
            question = input("Câu hỏi: ")
            if question == "exit":
                print(f"Kết thúc trò chuyện.")
                break
            answer = self.answer(question)
            print(f"Trả lời: {answer}\n")