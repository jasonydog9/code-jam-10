import PIL.Image


class Pigpen:
    """
    Summary

    Pigpen class has image, cipher_text, and a solution
    """

    UPDATE = 0
    SOLVED = 1

    def __init__(
        self,
        image: PIL.Image.Image,
        cipher_text: PIL.Image.Image,
        solution: str,
    ):
        self.image = (image,)
        self.cipher_text = cipher_text
        self.solution = solution
        self.event: list[int] = []

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
