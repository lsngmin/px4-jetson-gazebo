class SingletonMixin:
    _instance = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise Exception(f"{self.__class__.__name__}는 싱글톤입니다! get_instance()로만 생성하세요.")
