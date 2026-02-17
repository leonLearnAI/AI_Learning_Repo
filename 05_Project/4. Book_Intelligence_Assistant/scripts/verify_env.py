
from src.core.settings import settings

print(settings.postgres_host)
print(settings.postgres_port)
print(settings.postgres_db)
print(settings.postgres_user)
print(settings.postgres_password)
print(settings.default_top_k)
print(settings.default_spoiler_model)

# import os, sys
# from pathlib import Path

# print("CWD:", os.getcwd())
# print("FILE:", Path(__file__).resolve())
# print("sys.path[0]:", sys.path[0])
# print("sys.path first 5:")
# for p in sys.path[:5]:
#     print("  ", p)

# root = Path(__file__).resolve().parent.parent
# print("Project root guess:", root)
# print("Has src dir?:", (root / "src").exists())
# print("Has src/__init__.py?:", (root / "src" / "__init__.py").exists())
