import ctypes
import llama_cpp

# C 签名:
# void callback(int level, const char * message, void * user_data)
_LOG_CALLBACK_TYPE = ctypes.CFUNCTYPE(
    None,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_void_p,
)

# 保留模块级引用以防止被垃圾回收
_silent_callback_ref = None


def disable_llama_logging():
    """
    禁用所有原生 llama.cpp / ggml 日志记录（Metal、CUDA、CPU）。

    必须在创建任何 Llama 实例之前调用一次。
    """
    global _silent_callback_ref

    def _silent_log(level, message, user_data):
        return

    _silent_callback_ref = _LOG_CALLBACK_TYPE(_silent_log)
    llama_cpp.llama_log_set(_silent_callback_ref, None)
