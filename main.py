from modules.Embedding import Embedding
from modules.VectorDB import VectorDB
from modules.Prompt import Prompt
from modules.LLM import LLM
from modules.LLMChain import LLMChain

from utils.query_retriever import re_phrase_retriever, multiple_query_retriever, retriever_chain, \
                            contextual_compression_retriever, ensemble_retriever
from utils.helper_func import pretty_print_docs

from configs.setup import embedding_path,k_nearest_similarity, save_local_path

# Set logging for the queries
import logging
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)

# INIT RAG MODULES
## LLM
llm = LLM.from_openai(model = "Hermes-3-Llama-3.2-3B.Q4_K_M", base_url = "http://localhost:1234/v1", api_key="llm-studio-key")
# llm = LLM.from_local_transformers(model_path = "models/Hermes-3-Llama-3.2-3B.Q4_K_M.gguf", model_type = "llama", max_tokens = 512)
## EMBEDDING
embedding = Embedding(embedding_path = embedding_path)
# VECTOR DB
base_retriever = VectorDB(embedding = embedding).create_db_from_texts("dataset/source-1").as_retriever(search_kwargs={"k": k_nearest_similarity})
base_retriever_2 = VectorDB(embedding = embedding).create_db_from_texts("dataset/source-2").as_retriever(search_kwargs={"k": k_nearest_similarity})

# Kết hợp retriever của nhiều nguồn -> diễn đạt lại câu hỏi -> sinh ra thêm câu hỏi để có nhiều góc độ -> nén docs nếu quá nhiều để đỡ ảnh hưởng context
e_retriever = ensemble_retriever([base_retriever, base_retriever_2], weights=[1.0, 1.0])

# retriever = re_phrase_retriever(base_retriever, llm)
# retriever = multiple_query_retriever(base_retriever, llm)
chain_of_retriever = retriever_chain(e_retriever, llm, [re_phrase_retriever, multiple_query_retriever])

retriever = contextual_compression_retriever(chain_of_retriever, 
                                             filter_type = "rerank",
                                             llm = llm)

# INFERENCE CHAT
from scripts.Chat import Chat
prompt = "Bạn là một trợ lý hữu ích trong lĩnh vực y tế, Nếu câu trả lời nằm ngoài phạm vi y tế và nội dung được cho, hãy trả lời không biết, không được tạo ra câu trả lời khác."
assistant = Chat(llm, retriever, prompt)

# Ví dụ sử dụng
question1 = "đau đầu là gì"
answer1 = assistant.answer(question1)
print(f"Câu hỏi: {question1}\nTrả lời: {answer1}\n")

question2 = "làm sao để trị"
answer2 = assistant.answer(question2)
print(f"Câu hỏi: {question2}\nTrả lời: {answer2}\n")

question3 = "có lưu ý nào khác không"
answer3 = assistant.answer(question3)
print(f"Câu hỏi: {question3}\nTrả lời: {answer3}\n")

# answer log
# INFO:langchain.retrievers.re_phraser:Re-phrased question: Để truy xuất vectorstore chứa thông tin về nguyên nhân gây đau đầu, vui lòng cung cấp các truy vấn sau:

# 1. Vector chứa thông tin về căng thẳng và căng cơ làm đau đầu.
# 2. Vector chứa thông tin về migrain, một dạng headache đặc trưng bởi cơn đau mạnh mẽ thường ở một bên đầu.
# 3. Vector chứa thông tin về tension headache, nguyên nhân do căng cơ cơ thể, often caused by stress or eye strain.
# 4. Vector chứa thông tin về cluster headache, một dạng headache hiếm gặp có thể gây cơn đau dữ dội quanh hoặc sau mắt và có thể kéo dài vài giờ.
# 5. Vector chứa thông tin về sinus headache, nguyên nhân là do viêm sín, làm áp lực lên đầu.
# 6. Vector chứa thông tin về headache exertion (exercise-induced), xảy ra sau khi thực hiện運動 như vận động hoặc hoạt động căng thẳng.
# 7. Vector chứa thông tin về hormonal changes, sự biến đổi hormone estrogen và progesterone trong chu kỳ kinh nguyệt của một số phụ nữ có thể gây headache.
# 8. Vector chứa thông tin về tác dụng phụ của thuốc, một số loại thuốc như thuốc giảm đau có thể gây headache cho một số cá nhân.
# 9. Vector chứa thông tin về tai nạn đầu óc, nếu gặp phải tai nạn đầu óc thì có trường hợp rất hiếm gặp lại gây ra chứng headache mãn tính.
# 10. Vector chứa thông tin về các yếu tố khác như mất nước, huyết áp cao, thiếu ngủ, một số thức ăn hoặc allergen là một số yếu tố khác có thể là trigger cho headaches.

# Cảm ơn bạn đã cung cấp câu hỏi và hy vọng chúng tôi có thể giúp tìm kiếm vectorstore phù hợp.
# INFO:langchain.retrievers.multi_query:Generated queries: ['1. Vector chứa thông tin về căng thẳng, stress và sự cố gắng làm tăng nguy cơ đau đầu.', '2. Vector chứa thông tin về migrain, một dạng headache đặc trưng bởi cơn đau mạnh mẽ thường ở một bên đầu và kéo dài từ vài giờ đến một ngày.', '3. Vector chứa thông tin về tension headache, nguyên nhân do căng cơ cơ thể, often caused by stress hoặc eye strain và có thể gây đau đầu sau khi xem màn hình máy tính.', '4. Vector chứa thông tin về cluster headache, một dạng headache hiếm gặp có thể gây cơn đau dữ dội quanh hoặc sau mắt và kéo dài vài giờ.', '5. Vector chứa thông tin về sinus headache, nguyên nhân là do viêm sín, làm áp lực lên đầu và thường xảy ra khi chịu áp lực từ khí quản bị tắc nghẽn hoặc cảm lạnh.', '6. Vector chứa thông tin về headache exertion (exercise-induced), xảy ra sau khi thực hiện vận động như vận động hoặc hoạt động căng thẳng và có thể gây đau đầu do sự thay đổi hormone khi tập luyện.', '7. Vector chứa thông tin về hormonal changes, sự biến đổi hormone estrogen và progesterone trong chu kỳ kinh nguyệt của một số phụ nữ có thể gây headache và có liên quan đến các vấn đề kinh nguyệt.', '8. Vector chứa thông tin về tác dụng phụ của thuốc, một số loại thuốc như thuốc giảm đau có thể gây headache cho một số cá nhân và cần phải biết về khả năng gây ra cảm giác đau đầu.', '9. Vector chứa thông tin về tai nạn đầu óc, nếu gặp phải tai nạn đầu óc thì có trường hợp rất hiếm gặp lại gây ra chứng headache mãn tính và là một yếu tố nguy cơ đáng kể cho các vấn đề về đầu óc.', '10. Vector chứa thông tin về các yếu tố khác như mất nước, huyết áp cao, thiếu ngủ, một số thức ăn hoặc allergen là một số yếu tố khác có thể là trigger cho headaches và cần phải biết cách quản lý chúng.']
# Câu hỏi: đau đầu là gì
# Trả lời: Đau đầu là một rối loạn thần kinh gây cảm giác đau nhói ở phần đầu. Đây thường là một sự đau dữ dội ở một bên hoặc cả hai bên của đầu và có thể làm ảnh hưởng đến khả năng sống của người bệnh. Đau nửa đầu có thể xuất hiện một cách đột ngột, làm giảm khả năng tập trung và làm ảnh hưởng đến chất lượng cuộc sống của người bệnh.

# Đau nửa đầu thường được phân loại thành "đau nhói" và "đau dữ dội". Đau nhói là cảm giác đau nhạy cảm ở phần nào đó của đầu, thường kèm theo hiện tượng co thắt cơ. Còn đau dữ dội là một cảm giác đau lớn hơn nhiều, có thể làm rung động toàn bộ đầu.

# Đau nửa đầu có thể xuất hiện một cách đột ngột và không rõ nguyên nhân, hoặc nó có thể báo hiệu sự xuất hiện của các dấu hiệu báo trước gọi là "aura". Aura thường bao gồm các triệu chứng khác như cảm giác buồn nôn, nhạy cảm với ánh sáng và âm thanh, và đôi khi có biểu hiện thần kinh (như cảm giác có vật gì đó ở đầu hoặc cảm giác bị ướt). Tuy nhiên, không phải lúc nào cũng có dấu hiệu báo trước cho một đợt đau nửa đầu dữ dội.

# Nguồn gốc của đau nửa đầu là chưa rõ, nhưng nó được cho là liên quan đến nhiều yếu tố khác nhau, bao gồm di truyền, căng thẳng, thay đổi hormone, thiếu ngủ hoặc kích thích từ thực phẩm và đồ uống như rượu và caffeine.

# INFO:langchain.retrievers.re_phraser:Re-phrased question: Tìm hiểu về cách điều trị và ngăn ngừa đau nửa đầu.
# INFO:langchain.retrievers.multi_query:Generated queries: ['1. So sánh các phương pháp điều trị đau nửa đầu phổ biến, bao gồm liệu pháp thuốc, thể thao và điều dưỡng.', '2. Phân tích các yếu tố nguy cơ và rủi ro liên quan đến đau nửa đầu và cách ngăn ngừa chúng.', '3. Tìm hiểu về sự phát triển của đau nửa đầu ở mỗi bên và các nguyên nhân có thể gây ra nó.', '4. So sánh hiệu quả của liệu pháp thuốc, trị liệu tâm lý và chăm sóc sức khỏe cơ thể đối với đau nửa đầu.', '5. Phân tích tác động của stress và căng thẳng lên khả năng mắc phải đau nửa đầu và cách giảm thiểu chúng.']
# Câu hỏi: làm sao để trị
# Trả lời: Để điều trị đau nửa đầu, bạn có thể áp dụng một số cách thức sau đây:

# 1. Thuốc giảm đau: Bạn có thể sử dụng thuốc giảm đau không kê đơn (như ibuprofen) hoặc thuốc giảm đau đặc hiệu (triptans) theo chỉ dẫn của bác sĩ để kiểm soát triệu chứng.

# 2. Ngủ đủ giờ: Thay đổi lối sống và ngủ đủ giấc, từ 7-9 giờ mỗi đêm có thể giúp giảm bớt căng thẳng và mệt mỏi.

# 3. Chế độ ăn uống khoa học: Có một số thực phẩm đã được chứng minh là có thể kích hoạt các cơn đau nửa đầu, như caffeine trong cà phê hoặc trà, và tyramine trong các loại thịt đông và một số thực phẩm khác. Bạn cần tìm cách tránh xa chúng.

# 4. Chuyển đổi lối sống: Một số người bị đau nửa đầu có thể cải thiện triệu chứng của họ bằng việc thay đổi các yếu tố gây căng thẳng trong cuộc sống, như giảm áp lực làm việc hoặc học cách đối phó với căng thẳng bằng phương pháp phát triển cá nhân.

# 5. Thuốc trị liệu: Bác sĩ có thể kê toa thuốc chống stress và thuốc giảm căng thẳng cho bạn để hỗ trợ điều trị.

# 6. Massage và thực thi các bài tập thư giãn: Một số nghiên cứu chỉ ra rằng massage đầu và thực thi các bài tập thư giãn có thể giúp cải thiện triệu chứng đau nửa đầu.

# 7. Thuốc đặc trị: Bác sĩ cũng có thể kê toa thuốc đặc trị (triptans) cho bạn nếu các loại thuốc giảm đau không đủ hiệu quả.

# Lưu ý, nếu cảm thấy các triệu chứng của cơn đau nửa đầu của bạn trở nên tồi tệ hơn hoặc kéo dài quá lâu, hoặc nếu bạn bắt đầu gặp vấn đề với sự ổn định của tâm trạng và khả năng sống thường ngày, hãy liên hệ với bác sĩ để kiểm tra lại.

# INFO:langchain.retrievers.re_phraser:Re-phrased question: Tôi rất cảm kích vì sự quan tâm của bạn đến việc tìm hiểu về đau nửa đầu và cách điều trị nó. Bạn có thể hỏi về nguyên nhân chính phổ biến nhất dẫn đến đau nửa đầu, các phương pháp điều trị hiệu quả hoặc thậm chí là việc sử dụng thuốc để giảm bớt cơn đau. Miễn là vấn đề liên quan đến đau nửa đầu, tôi sẵn sàng cung cấp thông tin hữu ích và trả lời câu hỏi của bạn một cách chuyên nghiệp và lịch sự nhất.
# INFO:langchain.retrievers.multi_query:Generated queries: ['1. Tôi có thể hỏi về nguyên nhân chính phổ biến nhất dẫn đến đau nửa đầu? Bác sĩ cho biết các phương pháp điều trị hiệu quả nào cho đau nửa đầu? Còn có cách nào để sử dụng thuốc giảm cơn đau mà không gây phụ thuộc hay tác hại không mong muốn không?', '2. Rất cảm ơn bạn đã quan tâm đến cách ngăn ngừa và điều trị đau nửa đầu. Bạn biết ai là những người dễ mắc phải đau nửa đầu hơn thế nào? Có các liệu pháp thay đổi hành vi giúp giảm bớt cơn đau không?', '3. Tôi rất quan tâm đến việc tìm hiểu về nguyên nhân phổ biến của đau nửa đầu và các phương pháp điều trị hiệu quả như thế nào. Còn có cách nào để sử dụng thuốc giảm đau mà không gây phụ thuộc hay tác hại không mong muốn?', '4. Rất cảm ơn bạn đã quan tâm đến vấn đề đau nửa đầu. Ai là những người dễ mắc phải đau nửa đầu hơn? Có các liệu pháp thay đổi hành vi giúp giảm bớt cơn đau không?', '5. Bạn biết ai là những người dễ mắc phải đau nửa đầu hơn thế nào? Rất mong muốn được nghe về các phương pháp điều trị hiệu quả cho đau nửa đầu cũng như việc sử dụng thuốc giảm đau mà không gây phụ thuộc hay tác hại không mong muốn.', '6. Tôi rất quan tâm đến việc ngăn ngừa và điều trị đau nửa đầu. Ai là những người dễ mắc phải đau nửa đầu hơn? Còn có cách nào để sử dụng thuốc giảm đau mà không gây phụ thuộc hay tác hại không mong muốn?', '7. Rất cảm ơn bạn đã quan tâm đến cách ngăn ngừa và điều trị đau nửa đầu. Có các phương pháp điều trị hiệu quả cho đau nửa đầu không? Ai là những người dễ mắc phải đau nửa đầu hơn?', '8. Tôi rất quan tâm đến việc tìm hiểu về nguyên nhân phổ biến của đau nửa đầu và các phương pháp điều trị hiệu quả như thế nào. Còn có cách nào để sử dụng thuốc giảm đau mà không gây phụ thuộc hay tác hại không mong muốn? Ai là những người dễ mắc phải đau nửa đầu hơn?', '9. Rất cảm ơn bạn đã quan tâm đến vấn đề đau nửa đầu. Có các liệu pháp thay đổi hành vi giúp giảm bớt cơn đau không? Bạn biết ai là những người dễ mắc phải đau nửa đầu hơn và có các phương pháp điều trị hiệu quả cho đau nửa đầu không?', '10. Tôi rất mong muốn được nghe về nguyên nhân chính phổ biến nhất dẫn đến đau nửa đầu, các phương pháp điều trị hiệu quả và việc sử dụng thuốc giảm đau mà không gây phụ thuộc hay tác hại không mong muốn. Ai là những người dễ mắc phải đau nửa đầu hơn và có các liệu pháp thay đổi hành vi giúp giảm bớt cơn đau không?']
# Câu hỏi: có lưu ý nào khác không
# Trả lời: Có, đây là một số lưu ý khác mà bạn có thể áp dụng:

# 1. Tăng cường chế độ ăn uống lành mạnh: Đảm bảo cung cấp cho cơ thể đủ vitamin và chất dinh dưỡng cần thiết để hỗ trợ hệ thần kinh.

# 2. Giữ sự cân bằng về căng thẳng và stress: Bao quanh bản thân cách làm việc và sinh hoạt bình yên, tránh xa các nguồn gây stress cao.

# 3. Ăn không kỳ vọng: Một số nghiên cứu cho thấy việc ăn không kỳ vọng có thể giúp giảm thiểu tác động của đau nửa đầu do căng thẳng.

# 4. Sử dụng phương tiện giải trí: Hãy dành thời gian cho bản thân những hoạt động giải trí và thư giãn, ví dụ như đọc sách, nghe nhạc hoặc đi bộ trong vườn.

# 5. Kết hợp các phương pháp điều trị: Bạn có thể kết hợp sử dụng thuốc giảm đau với việc áp dụng phương pháp phát triển cá nhân để kiểm soát căng thẳng và stress.

# 6. Giữ mình khỏi kích thích: Đảm bảo tránh xa thực phẩm và đồ uống có chứa caffeine, tyramine hoặc other substances that may trigger migraines.

# 7. Chế độ sinh hoạt khoa học: Có một số bằng chứng cho thấy việc ngủ đủ giấc có thể giúp giảm triệu chứng đau nửa đầu.

# Lưu ý rằng mỗi cá nhân có những cách điều trị khác nhau hiệu quả nhất, và việc áp dụng nhiều phương pháp có thể là một chiến lược an toàn để kiểm soát triệu chứng đau nửa đầu của bạn.

# INFERENCE LLM CHAIN

# PROMPT
# template =   \
# """<|im_start|>system
# Bạn là một trợ lý hữu ích trong lĩnh vực y tế. Sử dụng thông tin sau đây để trả lời câu hỏi
# ```{context}```. 
# Nếu câu trả lời nằm ngoài phạm vi y tế và nội dung bên trên, hãy trả lời không biết, không được tạo ra câu trả lời khác.
# <|im_end|>
# <|im_start|>user 
# {question}
# <|im_end|>
# <|im_start|>assistant
# """
# prompt = Prompt(template, ["context","question"])

# llm_chain = LLMChain(llm)

# question = "đau đầu do bệnh lý gì gây ra"
# llm_chain.infer(question, prompt, retriever)
# llm_chain.start_conversation()

# INFERENCE PIPELINE

# re-phrase `question` ----------
# Đau đầu có thể xuất phát từ nhiều nguyên nhân khác nhau. Có thể liên quan đến vấn đề về não, hệ thần kinh hoặc thậm chí tâm trạng. Để giúp tìm hiểu rõ hơn về nguyên nhân, tôi xin hỏi thêm một số câu hỏi sau:

# 1. Bạn có cảm nhận đau đầu đều đặn hay chỉ ở những lúc nhất định không?
# 2. Đau đầu thường xuất hiện cùng với các triệu chứng khác không?
# 3. Có thể kể tên cho chúng ta lần lượt từng cơn đau đầu của bạn để chúng tôi đánh giá chi tiết hơn.



# multi-query ----------
# ['1. Đau đầu có nguồn gốc từ một vấn đề thần kinh nhất định không?', 
#  '2. Bạn cảm nhận đau đầu gây áp lực, sưng hoặc tê tại nơi nào của đầu?', 
#  '3. Có liên quan đến việc giảm thị lực khi mở mắt hay không?', 
#  '4. Bác sĩ đã kiểm tra để tìm các mảng máu trong não chưa? ', 
#  '5. Bạn có sử dụng một số loại thực phẩm như ginkgo biloba hay fish oil không và cảm thấy đau đầu đã được cải thiện sau đó?'] 



# find 20 docs (10 for each base_retriever) ----------



# compress to 3 docs in the most relation ----------
# Document 1:

# Phân Loại và Phân Tích
# Các từ được chia thành bốn nhóm chính: triệu chứng, bệnh lý/tình trạng, tác nhân gây bệnh, và phương pháp điều trị. Mỗi nhóm được phân tích dựa trên thông tin từ các nguồn như Wikipedia, MedlinePlus, và các tổ chức y tế quốc tế.

# Triệu Chứng
# Triệu chứng là những cảm giác chủ quan mà bệnh nhân trải nghiệm, thường là dấu hiệu của vấn đề sức khỏe tiềm ẩn. Dựa trên danh sách từ Wikipedia về triệu chứng y tế, các triệu chứng được liệt kê bao gồm:
# Metadata: {'id': 0, 'relevance_score': 0.9991718, 'source': 'dataset\\sick.txt'}
# ----------------------------------------------------------------------------------------------------
# Document 2:

# Nhiễm trùng (Infection): Xâm nhập cơ thể bởi vi sinh vật gây bệnh, gồm vi khuẩn, virus, nấm, ký sinh trùng. Điều trị tùy loại, như kháng sinh, kháng virus (NIH).

# Viêm khớp (Arthritis): Viêm khớp, gây đau, cứng khớp, gồm viêm xương khớp, viêm khớp dạng thấp. Điều trị bằng thuốc giảm đau, vật lý trị liệu, thuốc điều chỉnh bệnh (CDC).
# Metadata: {'id': 16, 'relevance_score': 0.999132, 'source': 'dataset\\sick.txt'}
# ----------------------------------------------------------------------------------------------------
# Document 3:

# Đau lưng (Back pain): Đau ở lưng, do căng cơ, thoát vị đĩa đệm, hoặc loãng xương. Điều trị bằng nghỉ ngơi, vật lý trị liệu, hoặc phẫu thuật nếu cần.  

# Bệnh Lý và Tình Trạng
# Cảm cúm (Influenza): Nhiễm virus đường hô hấp, triệu chứng gồm sốt, ho, đau họng, mệt mỏi. Điều trị bằng nghỉ ngơi, bù nước, thuốc kháng virus nếu cần. Phòng ngừa bằng vắc-xin hàng năm (CDC).
# Metadata: {'id': 8, 'relevance_score': 0.99911034, 'source': 'dataset\\sick.txt'}



# put docs to context and generate the answer ----------
# Đau đầu là triệu chứng của nhiều bệnh lý khác nhau. Một số nguyên nhân phổ biến có thể bao gồm:

# 1. Loãng xương (Osteoporosis): Loãng xương làm giảm độ cứng và độ chắc của xương, dễ bị tổn thương và phát triển nứt xương hoặc rạn xương. Đau đầu thường gây khó chịu, đau đớn, và có thể lan rộng đến đầu gối và lưng.

# 2. Tràn dịch giữa não (Hemorrhagic Meningitis): Tràn dịch này xảy ra khi máu tràn vào không gian quanh não, gây đau đầu dữ dội, chóng mặt, hôn mê hoặc tử vong nếu không được điều trị kịp thời.

# 3. Đau đầu do chấn thương (Headache from trauma): Có thể là tai nạn, va chạm, hoặc chấn thương khác làm căng cơ và dây thần kinh ở đầu.

# 4. Bệnh nhân Parkinson: Bệnh nhân Parkinson có thể bị đau đầu như một biến chứng của bệnh này.

# 5. Thể tích não tăng (Increased intracranial pressure): Có thể do các nguyên nhân như tê liệt, ung thư đầu hoặc một số bệnh lý khác gây ra sự kẹt của chất lỏng và khí trong không gian quanh não.

# 6. Loại bỏ độc tố trong não (Migraine): Đau đầu này thường bao gồm hai phần: một phần nhẹ nhàng, có thể xảy ra trước khi đau đầu chính, và một phần dữ dội hơn kéo dài từ vài giờ đến một ngày hoặc thậm chí nhiều ngày.

# 7. Migraine không điển hình: Một dạng migraine mà đau đầu không bắt nguồn từ một bên đầu.

# Để xác định nguyên nhân chính xác của đau đầu, bác sĩ thường tiến hành đánh giá bệnh nhân dựa trên lịch sử và triệu chứng của họ. Một số bài kiểm tra lâm sàng và chụp CT/MRI có thể giúp xác định vị trí và nguyên nhân của đau đầu.