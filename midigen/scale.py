class Scale:
    # Interval steps
    MAJOR_INTERVALS = [2, 2, 1, 2, 2, 2, 1] # W W H W W W H
    MINOR_INTERVALS = [2, 1, 2, 2, 1, 2, 2] # W H W W H W W

    @staticmethod
    def major(root):
        return Scale._generate_scale(root, Scale.MAJOR_INTERVALS)

    @staticmethod
    def minor(root):
        return Scale._generate_scale(root, Scale.MINOR_INTERVALS)

    @staticmethod
    def _generate_scale(root, intervals):
        if not isinstance(root, int) or root < 0 or root > 127:
            raise ValueError("Root must be an integer between 0 and 127 inclusive")
        scale = [root]
        for interval in intervals:
            scale.append(scale[-1] + interval)
        return scale
