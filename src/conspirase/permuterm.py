import bisect

class PermutermIndex:
    def __init__(self, vocabulary):
        """Build two parallel lists: one with rotations and another with terms"""
        for term in vocabulary: 
            pairs_lst = []
            t = term +'$'
            for i in range(len(t)):
                rotation = t[i:] + t[:i]
                pairs_lst.append((rotation,term))
            pairs_lst.sort()
            self.rotations = [rotation for rotation, _ in pairs_lst] #all rotations are sorted alphabetically (not terms-wise alphabetically)
            self.terms = [term for _, term in pairs_lst] #the terms associated with the rotations, bound by the index [i]

    def _prefix_lookup(self,prefix):
        """Finds all terms with rotations starting with the prefix"""
        result = set() 
        start = bisect.bisect_left(self.rotations,prefix) #gives the position of the first rotation that is greater or equal to prefix  
        for i in range (start, len(self.rotations)):
            if not self.rotations[i].startswith(prefix):
                break
            result.add(self.terms[i])
        return result

    def lookup(self,pattern):
        """Build the right search key and hand it to _prefix_lookup function"""
        n = pattern.count("*")
        if pattern.split("*") == "":
            raise ValueError ("There must be at least one symbol besides wildcard")
        elif n == 0:
            prefix = pattern 
        elif n == 1:
            before,after = pattern.split("*")
            prefix = after + '$' + before 
        elif n == 2 and pattern.startswith("*") and pattern.endswith("*"):
            prefix = pattern[1:-1]
        else:
            raise ValueError ("Unsupported wildcard")
        return sorted(self._prefix_lookup(prefix))