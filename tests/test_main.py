from unittest.mock import patch

from main import main


def test_main_starts_user_interaction() -> None:
    with patch("main.user_interaction") as interaction:
        main()

    interaction.assert_called_once_with()
