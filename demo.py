# import tensorflow as tf

# # 检查 TensorFlow 是否能访问 GPU
# if tf.test.is_gpu_available():
#     print("TensorFlow is using GPU.")
# else:
#     print("TensorFlow is using CPU.")


import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("Built with CUDA:", tf.test.is_built_with_cuda())
print("Built with GPU support:", tf.test.is_built_with_gpu_support())