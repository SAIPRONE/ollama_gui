import os
import torch
import psutil
from transformers import LlamaForCausalLM, LlamaTokenizer
from threading import Thread

class ModelManager:
    def __init__(self, app):
        self.app = app
        self.model = None
        self.tokenizer = None

    def check_memory(self):
        try:
            memory_info = psutil.virtual_memory()
            total_memory = memory_info.total / (1024 ** 3)  # GB
            available_memory = memory_info.available / (1024 ** 3)  # GB

            gpu_properties = torch.cuda.get_device_properties(0)
            total_gpu_memory = gpu_properties.total_memory / (1024 ** 3)  # GB
            reserved_gpu_memory = torch.cuda.memory_reserved(0) / (1024 ** 3)  # GB
            allocated_gpu_memory = torch.cuda.memory_allocated(0) / (1024 ** 3)  # GB
            free_gpu_memory = total_gpu_memory - reserved_gpu_memory - allocated_gpu_memory

            memory_status = (
                f"System Memory - Total: {total_memory:.2f} GB, Available: {available_memory:.2f} GB\n"
                f"GPU Memory - Total: {total_gpu_memory:.2f} GB, Free: {free_gpu_memory:.2f} GB"
            )
            self.app.update_status(memory_status)

            if available_memory < 20:
                raise MemoryError("Insufficient system memory to load the model.")
            if free_gpu_memory < 6:
                raise MemoryError("Insufficient GPU memory to load the model.")

        except MemoryError as e:
            self.app.update_status(f"Memory error: {e}")
        except Exception as e:
            self.app.update_status(f"Error checking memory: {e}")

    def load_model(self, model_path, tokenizer_path, ckpt_dir, max_seq_len=1024, max_batch_size=1):
        def load():
            try:
                self.check_memory()

                self.app.update_status("Loading tokenizer...")
                self.tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
                self.app.update_status("Tokenizer loaded successfully.")

                self.app.update_status("Loading model, please wait...")
                self.model = LlamaForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True,
                    device_map="auto"
                )
                self.app.update_status("Model loaded successfully.")
            except MemoryError as mem_err:
                self.app.update_status(f"Memory error: {mem_err}")
            except FileNotFoundError as fnf_error:
                self.app.update_status(f"File not found error: {fnf_error}")
            except Exception as e:
                self.app.update_status(f"Error loading model or tokenizer: {e}")
            finally:
                self.app.loading = False
                self.app.progress.stop()

        self.app.update_status("Loading model, please wait...")
        self.app.loading = True
        Thread(target=load).start()

    def generate_response(self, prompt):
        if self.model and self.tokenizer:
            try:
                inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
                outputs = self.model.generate(**inputs)
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                return response
            except Exception as e:
                return f"Error generating response: {e}"
        else:
            return "Model not loaded."

    def update_model(self):
        self.app.update_status("Updating model...")

    def train_model(self, train_data):
        self.app.update_status("Training model...")
