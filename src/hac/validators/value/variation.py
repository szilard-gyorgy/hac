class variation(object):
    @staticmethod
    def filter_invalid(old, new, tolerance):
        if abs(old - new) / new * 100 < tolerance:
            return new
        return False
