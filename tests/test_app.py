# test_app.py
import settings
from main import run  # Assuming your original code is in app.py


def test_run_prints_discord_api_secret(capfd):
    # Mock the DISCORD_API_SECRET attribute in settings
    settings.DISCORD_API_SECRET = "mock_secret"

    # Call the function
    run()

    # Capture the output
    out, err = capfd.readouterr()

    # Verify the function prints the expected output
    assert out.strip() == "mock_secret", "run() should print the DISCORD_API_SECRET value"
