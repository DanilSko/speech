
class Pipeline:
    def __init__(self, *args):
        self.__steps = list(args)

    def apply_to(self, text):
        for step in self.__steps:
            text = step.annotate(text)
        return text

    def add_step(self, step):
        self.__steps.append(step)
