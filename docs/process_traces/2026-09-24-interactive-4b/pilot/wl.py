import ctypes, json, os, sys, time
out = sys.argv[1]
libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
libc.pthread_self.restype = ctypes.c_void_p
libc.pthread_get_qos_class_np.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_int)]
qos = ctypes.c_uint(); rel = ctypes.c_int()
libc.pthread_get_qos_class_np(libc.pthread_self(), ctypes.byref(qos), ctypes.byref(rel))
res = {"pid": os.getpid(), "ppid": os.getppid(), "qos_class": hex(qos.value), "nice": os.getpriority(os.PRIO_PROCESS, 0)}
def cpu():
    t = time.perf_counter(); x = 0
    for i in range(20_000_000): x += i
    return time.perf_counter() - t
res["cpu_s"] = [round(cpu(), 3) for _ in range(3)]
import mlx.core as mx
a = mx.random.normal((4096, 4096), dtype=mx.float16); mx.eval(a)
def gpu():
    t = time.perf_counter()
    for _ in range(40): b = a @ a; mx.eval(b)
    return time.perf_counter() - t
gpu(); res["gpu_s"] = [round(gpu(), 3) for _ in range(3)]
from mlx_lm import load, generate
m, tok = load("mlx-community/Qwen2.5-0.5B-Instruct-4bit")
generate(m, tok, prompt="Hello", max_tokens=16)
def lm():
    t = time.perf_counter(); generate(m, tok, prompt="Write a long story about a lighthouse keeper.", max_tokens=200); return time.perf_counter() - t
res["lm200_s"] = [round(lm(), 3) for _ in range(3)]
json.dump(res, open(out, "w"))
