print("=== resolve_screen_name candidates ===")
import vkbottle_types.responses.utils as u
print([m for m in dir(u) if "Resolve" in m or "resolve" in m])

print("\n=== pick model ===")
for name in dir(u):
    if "ResolveScreenName" in name:
        cls = getattr(u, name)
        if hasattr(cls, "model_fields"):
            print(name, "->", list(cls.model_fields.keys()))

print("\n=== WallWallpostFull fields ===")
try:
    from vkbottle_types.objects import WallWallpostFull
    fields = list(WallWallpostFull.model_fields.keys())
    for f in ["id","text","from_id","signer_id","owner_id"]:
        print(f"  {f}: {f in fields}")
except Exception as e:
    print("ERR:", repr(e))

print("\n=== wall.get_comments response ===")
import vkbottle_types.responses.wall as w
print([m for m in dir(w) if "Comment" in m])
for name in dir(w):
    if "GetComments" in name:
        cls = getattr(w, name)
        if hasattr(cls, "model_fields"):
            print(name, "->", list(cls.model_fields.keys()))

print("\n=== check full model of get_comments ===")
try:
    from vkbottle_types.responses.wall import WallGetCommentsResponseModel
    print("fields:", list(WallGetCommentsResponseModel.model_fields.keys()))
except Exception as e:
    print("ERR:", repr(e))

print("\n=== VKAPIError location ===")
try:
    from vkbottle.exception_factory import VKAPIError
    print("VKAPIError OK:", VKAPIError)
except Exception as e:
    print("ERR:", repr(e))
try:
    from vkbottle import VKAPIError as E2
    print("vkbottle.VKAPIError OK:", E2)
except Exception as e:
    print("ERR2:", repr(e))