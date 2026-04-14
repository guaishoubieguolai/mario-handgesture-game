import torch
print(torch.version.cuda)   # CUDA 版本
print(torch.backends.cudnn.version())  # cuDNN 版本
print(torch.cuda.is_available())  # GPU 是否可用