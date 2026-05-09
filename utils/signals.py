import numpy as np


def generate_signal(prediction):

    """
    Convert predicted returns
    into trading signals
    """

    if prediction > 0.003:

        return 1

    elif prediction < -0.003:

        return -1

    else:

        return 0