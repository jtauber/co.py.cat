import formulas


class WorkspaceStructure(object):
    def __init__(self):
        self.string = None
        self.internal_strength = 0.0
        self.external_strength = 0.0
        self.total_strength = 0.0

    def update_strength(self):
        self.update_internal_strength()
        self.update_external_strength()
        self.update_total_strength()

    def update_total_strength(self):
        """Recalculate the total strength based on internal and external strengths"""
        weights = ((self.internal_strength, self.internal_strength), (self.external_strength, 100 - self.internal_strength))
        strength = formulas.weightedAverage(weights)
        self.total_strength = strength

    def total_weakness(self):
        """The total weakness is derived from total strength"""
        return 100 - self.total_strength ** 0.95
