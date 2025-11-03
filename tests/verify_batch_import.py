import importlib

try:
    mod = importlib.import_module('astro_engine.batch_processor')
    ok = 'process_single_calculation' in dir(mod) and callable(getattr(mod, 'process_single_calculation'))
    print(f"IMPORT_OK:{ok}")
except Exception as e:
    print(f"IMPORT_ERROR:{type(e).__name__}:{e}")
