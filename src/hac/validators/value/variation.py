class variation(object):
    @staticmethod
    def filter_invalid(old, new, tolerance):
        #print("Old value: {} new value: {}".format(old, new))
        if not isinstance(old, (float, int)) and new:
            if abs(float(old) - new) / new * 100 < tolerance:
                return new
        return old
