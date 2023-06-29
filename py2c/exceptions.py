class SourceCodeException(Exception):
    def __init__(self, message, node):
        lineno = node.lineno if hasattr(node, 'lineno') else None
        col_offset = node.col_offset if hasattr(node, 'col_offset') else '-'
        name = node.__class__.__name__  # node.name if hasattr(node, 'name') else '-'
        message = f'{message}! Line: {lineno}/{col_offset} Name: {name}'
        super().__init__(message)


class InvalidAnnotationException(SourceCodeException):
    pass


class NoneIsNotAllowedException(SourceCodeException):
    pass


class LambdaIsNotAllowedHereException(SourceCodeException):
    pass


class TranslateAlgorythmException(Exception):
    pass