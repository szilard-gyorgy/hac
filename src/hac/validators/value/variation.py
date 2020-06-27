class variation(object):
    @staticmethod
    def filter_invalid(old, new, tolerance):
        if not isinstance(old, (float,int)):
            return new

        if abs(float(old) - new) / new * 100 < tolerance:
            return new
        return False
