import json


class JSONSerializable(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "toJSON"):
            return obj.toJSON()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return obj


class JSON():
    @staticmethod
    def stringify(obj: any) -> str:
        return json.dumps(obj, cls=JSONSerializable, ensure_ascii=False)

    @staticmethod
    def parse(jsonStr: str) -> any:
        return json.loads(jsonStr)
