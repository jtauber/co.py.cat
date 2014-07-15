from slipnet import slipnet
from workspace import workspace
from workspaceStructure import WorkspaceStructure
from formulas import *


class Rule(WorkspaceStructure):
    def __init__(self, facet, descriptor, category, relation):
        WorkspaceStructure.__init__(self)
        self.facet = facet
        self.descriptor = descriptor
        self.category = category
        self.relation = relation

    def __str__(self):
        if not self.facet:
            return 'Empty rule'
        return 'replace %s of %s %s by %s' % (self.facet.name, self.descriptor.name, self.category.name, self.relation.name)

    def update_external_strength(self):
        self.external_strength = self.internal_strength

    def update_internal_strength(self):
        if not (self.descriptor and self.relation):
            self.internal_strength = 0.0
            return
        averageDepth = (self.descriptor.conceptualDepth + self.relation.conceptualDepth) / 2.0
        averageDepth **= 1.1
        # see if the object corresponds to an object
        # if so, see if the descriptor is present (modulo slippages) in the
        # corresponding object
        changedObjects = [o for o in workspace.initial.objects if o.changed]
        changed = changedObjects[0]
        sharedDescriptorTerm = 0.0
        if changed and changed.correspondence:
            targetObject = changed.correspondence.objectFromTarget
            slippages = workspace.slippages()
            slipnode = self.descriptor.applySlippages(slippages)
            if not targetObject.hasDescription(slipnode):
                self.internal_strength = 0.0
                return
            sharedDescriptorTerm = 100.0
        sharedDescriptorWeight = ((100.0 - self.descriptor.conceptualDepth) / 10.0) ** 1.4
        depthDifference = 100.0 - abs(self.descriptor.conceptualDepth - self.relation.conceptualDepth)
        weights = ((depthDifference, 12), (averageDepth, 18), (sharedDescriptorTerm, sharedDescriptorWeight))
        self.internal_strength = weightedAverage(weights)
        if self.internal_strength > 100.0:
            self.internal_strength = 100.0

    def ruleEqual(self, other):
        if not other:
            return False
        if self.relation != other.relation:
            return False
        if self.facet != other.facet:
            return False
        if self.category != other.category:
            return False
        if self.descriptor != other.descriptor:
            return False
        return True

    def activateRuleDescriptions(self):
        if self.relation:
            self.relation.buffer = 100.0
        if self.facet:
            self.facet.buffer = 100.0
        if self.category:
            self.category.buffer = 100.0
        if self.descriptor:
            self.descriptor.buffer = 100.0

    def incompatibleRuleCorrespondence(self, correspondence):
        if not correspondence:
            return False
        # find changed object
        changeds = [o for o in workspace.initial.objects if o.changed]
        if not changeds:
            return False
        changed = changeds[0]
        if correspondence.objectFromInitial != changed:
            return False
        # it is incompatible if the rule descriptor is not in the mapping list
        if len([m for m in correspondence.conceptMappings if m.initialDescriptor == self.descriptor]):
            return False
        return True

    def __changeString(self, string):
        # applies the changes to self string ie. successor
        if self.facet == slipnet.length:
            if self.relation == slipnet.predecessor:
                return string[0:-1]
            if self.relation == slipnet.successor:
                return string + string[0:1]
            return string
        # apply character changes
        if self.relation == slipnet.predecessor:
            if 'a' in string:
                return None
            return ''.join([chr(ord(c) - 1) for c in string])
        elif self.relation == slipnet.successor:
            if 'z' in string:
                return None
            return ''.join([chr(ord(c) + 1) for c in string])
        else:
            return self.relation.name.lower()

    def buildTranslatedRule(self):
        slippages = workspace.slippages()
        self.category = self.category.applySlippages(slippages)
        self.facet = self.facet.applySlippages(slippages)
        self.descriptor = self.descriptor.applySlippages(slippages)
        self.relation = self.relation.applySlippages(slippages)
        # generate the final string
        self.finalAnswer = workspace.targetString
        changeds = [
            o for o in workspace.target.objects
            if o.hasDescription(self.descriptor) and
            o.hasDescription(self.category)
        ]
        changed = changeds and changeds[0] or None
        logging.debug('changed object = %s' % changed)
        if changed:
            left = changed.leftStringPosition
            startString = ''
            if left > 1:
                startString = self.finalAnswer[0: left - 1]
            right = changed.rightStringPosition
            middleString = self.__changeString(self.finalAnswer[left - 1: right])
            if not middleString:
                return False
            endString = ''
            if right < len(self.finalAnswer):
                endString = self.finalAnswer[right:]
            self.finalAnswer = startString + middleString + endString
        return True
