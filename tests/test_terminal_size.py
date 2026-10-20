from ascii_video.terminal.terminal_size import fit_to_terminal, get_terminal_size


def test_fit_to_terminal_caps_dimensions():
    width, height = fit_to_terminal(5000, 5000)
    assert width > 0
    assert height > 0


def test_get_terminal_size_returns_tuple():
    size = get_terminal_size()
    assert len(size) == 2
    assert size[0] > 0
    assert size[1] > 0
