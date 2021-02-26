class ValidateResponseMixin:
    def _is_response_ok(self):
        raise NotImplementedError()

    def _get_error(self):
        raise NotImplementedError()

    def validate(self, raise_exception=True):
        if self._is_response_ok():
            return
        error = self._get_error()
        if raise_exception:
            raise error
        return error
