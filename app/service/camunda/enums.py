class RegimeTributario:
    NATIONAL_SIMPLE = "SIMPLES NACIONAL"

    @classmethod
    def get_by_name(cls, name: str):
        return getattr(cls, name.upper())
