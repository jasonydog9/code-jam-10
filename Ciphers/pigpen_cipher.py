import PIL


class Pigpen:
    """
    Summary

    Pigpen class has image, cipher_text, and a solution
    """

    UPDATE = 0
    SOLVED = 1

    def __init__(
        self,
        image: PIL.Image,
        cipher_text: PIL.Image,
        solution: str,
    ):
        if type(image) is not PIL.PngImagePlugin.PngImageFile:
            raise (
                TypeError(
                    "Expected type "
                    + str(PIL.PngImagePlugin.PngImageFile)
                    + ", got type "
                    + str(type(image))
                    + " instead."
                )
            )
        self.image = (image,)
        self.cipher_text = cipher_text
        self.solution = solution
        self.event = []

    def check_solved(self, input_text):
        """
        Summary

        If the input user puts is equal to the solution of the cipher then it
        is solved
        """
        if input_text == self.solution:
            self.solved()

    def solved(self):
        """Cipher is solved"""
        self.event.append(Pigpen.SOLVED)
