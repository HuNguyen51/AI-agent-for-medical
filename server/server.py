# app.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import torch
import time
import uuid
import os
from contextlib import asynccontextmanager
from transformers import pipeline

from base_model import *

# --Khởi tạo server, load các mô hình cục bộ--

# Hệ thống xác thực đơn giản
security = HTTPBearer()
API_KEYS = {os.environ.get("API_KEY", "sk-default-key"), "key"}

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="API key không hợp lệ"
        )
    return credentials.credentials

# Lưu trữ models
models = {}

device = "cuda" if torch.cuda.is_available() else "cpu"
device = "mps" if torch.mps.is_available() else device

# Cấu hình mô hình mặc định
# //TODO: 1. DEFAULT_MODEL_CONFIG -> List[DEFAULT_MODEL_CONFIG], 2. lưu và tải cấu hình từ yaml file
DEFAULT_MODEL_CONFIG = {
        # required paramerters
        "task": "image-text-to-text",
        "model_id": "google/gemma-3-4b-it", 
        "device": device,
        # optional paramerters
        "max_length": 2048,
        "temperature": 0.7,
        "torch_dtype":"auto",
        "low_cpu_mem_usage":True,
    }

class ModelConfig:
    def __init__(self, task, model_id, device=None, **kwargs):
        self.task = task
        self.model_id = model_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.kwargs = kwargs

        self.generator = None
        
    def load(self):
        if self.model is None:
            print(f"Đang tải mô hình {self.model_id}...")
            self.generator = pipeline(
                # required paramerters
                task=self.task,
                model=self.model_id,
                device=self.device,
                # optional paramerters
                **self.kwargs
            )
            print(f"Đã tải mô hình {self.model_id} thành công")

# Load mô hình mặc định
def initialize_models():
    """
    Tải mô hình mặc định và lưu trữ trong bộ nhớ.
    
    Trả về một dictionary chứa mô hình mặc định.
    """
    default_config = ModelConfig(**DEFAULT_MODEL_CONFIG)
    default_config.load()

    models[DEFAULT_MODEL_CONFIG["model_id"]] = default_config
    return models


# Định nghĩa lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code chạy khi startup
    print("Ứng dụng đang khởi động...")
    initialize_models()
    # Ví dụ: Kết nối database, khởi tạo resource
    yield
    # Code chạy khi shutdown
    print("Ứng dụng đang tắt...")
    # Ví dụ: Đóng kết nối database, giải phóng resource

# Khởi tạo FastAPI
app = FastAPI(title="LLM API Server", 
              description="API server tương thích OpenAI cho mô hình ngôn ngữ lớn (HuggingFace)",
              lifespan=lifespan)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --API endpoints--

@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(api_key: str = Depends(verify_api_key)):
    data = []
    for model_id in models:
        data.append(ModelData(
            id=model_id,
            created=int(time.time()),
            owned_by="self-hosted"
        ))
    
    return ModelsResponse(data=data)

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest, api_key: str = Depends(verify_api_key)):
    model_id = request.model
    
    # Kiểm tra xem model có được hỗ trợ không
    if model_id not in models:
        if model_id not in [DEFAULT_MODEL_CONFIG["model_id"]]: #//TODO: kiểm tra model_id tồn tại trong list[DEFAULT_MODEL_CONFIG]
            raise HTTPException(status_code=404, detail=f"Model {model_id} không được tìm thấy.")
        else:
            # Tải model nếu chưa có
            config = ModelConfig(model_id=model_id)
            config.load()
            models[model_id] = config
    
    model_config = models[model_id]
    
    # Xử lý tin nhắn
    prompt = ""
    for msg in request.messages:
        role = msg.role
        content = msg.content
        
        if role == "system":
            prompt += f"System: {content}\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    
    prompt += "Assistant: "
    
    # Tạo phản hồi từ mô hình
    start_time = time.time()
    generation_config = {
        "max_new_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "do_sample": True if request.temperature > 0 else False,
    }
    
    if request.stop is not None:
        generation_config["stop_sequences"] = request.stop if isinstance(request.stop, list) else [request.stop]
    
    # Sử dụng pipeline để sinh văn bản
    outputs = model_config.generator(
        prompt, 
        **generation_config
    )
    
    # Xử lý kết quả
    generated_text = outputs[0]["generated_text"]
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):]
    
    # Tính toán số token
    input_tokens = len(model_config.tokenizer.encode(prompt))
    output_tokens = len(model_config.tokenizer.encode(generated_text))
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4()}",
        created=int(time.time()),
        model=model_id,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=Message(role="assistant", content=generated_text),
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
    )

@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest, api_key: str = Depends(verify_api_key)):
    model_id = request.model
    
    # Kiểm tra xem model có được hỗ trợ không
    if model_id not in models:
        if model_id not in [DEFAULT_MODEL_CONFIG["model_id"]]: #//TODO: kiểm tra model_id tồn tại trong list[DEFAULT_MODEL_CONFIG]
            raise HTTPException(status_code=404, detail=f"Model {model_id} không được tìm thấy.")
        else:
            # Tải model nếu chưa có
            config = ModelConfig(model_id=model_id)
            config.load()
            models[model_id] = config
    
    model_config = models[model_id]
    
    # Xử lý prompt
    prompt = request.prompt
    if isinstance(prompt, list):
        prompt = prompt[0]  # Chỉ lấy prompt đầu tiên nếu là danh sách
    
    # Tạo phản hồi từ mô hình
    generation_config = {
        "max_new_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "do_sample": True if request.temperature > 0 else False,
    }
    
    if request.stop is not None:
        generation_config["stop_sequences"] = request.stop if isinstance(request.stop, list) else [request.stop]
    
    # Sử dụng pipeline để sinh văn bản
    outputs = model_config.generator(
        prompt, 
        **generation_config
    )
    
    # Xử lý kết quả
    generated_text = outputs[0]["generated_text"]
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):]
    
    # Tính toán số token
    input_tokens = len(model_config.tokenizer.encode(prompt))
    output_tokens = len(model_config.tokenizer.encode(generated_text))
    
    return CompletionResponse(
        id=f"cmpl-{uuid.uuid4()}",
        created=int(time.time()),
        model=model_id,
        choices=[
            CompletionResponseChoice(
                index=0,
                text=generated_text,
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
    )

# Để chạy server: uvicorn app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)