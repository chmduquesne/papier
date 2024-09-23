import papier.extractor


def test_extractors() -> None:
    @papier.extractor
    def foo() -> None:
        pass
