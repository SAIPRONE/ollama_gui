import torch

def check_gpu_memory():
    if torch.cuda.is_available():
        total_memory = torch.cuda.get_device_properties(0).total_memory
        reserved_memory = torch.cuda.memory_reserved(0)
        allocated_memory = torch.cuda.memory_allocated(0)
        free_memory = total_memory - reserved_memory - allocated_memory
        
        print(f"Total GPU memory: {total_memory / (1024 ** 3):.2f} GB")
        print(f"Reserved GPU memory: {reserved_memory / (1024 ** 3):.2f} GB")
        print(f"Allocated GPU memory: {allocated_memory / (1024 ** 3):.2f} GB")
        print(f"Free GPU memory: {free_memory / (1024 ** 3):.2f} GB")
        
        return free_memory
    else:
        print("CUDA is not available.")
        return None

free_memory = check_gpu_memory()

if free_memory is not None and free_memory < 6 * 1024 * 1024 * 1024:  # Assuming 20GB needed
    print("Insufficient GPU memory to load the model.")
else:
    print("Sufficient GPU memory available.")
