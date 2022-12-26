import os


def get_shot_context():
    """Gets the current shot context of the enb

    Returns:
        Context (string): "show/scene/shot"

    """
    # SHOW = os.getenv('SHOW')
    # SCENE = os.getenv('SCENE')
    # SHOT = os.getenv('SHOT')
    return '{}/{}/{}'.format(os.getenv('SHOW'), os.getenv('SCENE'), os.getenv('SHOT'))
