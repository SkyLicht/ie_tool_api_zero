from core.auth.auth_utils import generate_16_uuid, generate_custom_id
from core.auth.security import get_password_hash, verify_password


# Example test: generate_16_uuid
def test_generate_16_uuid():
    # Call the function and get the result
    result = generate_16_uuid()

    # Check the length of the result
    assert len(result) == 16

    # Check if the result is a string
    assert isinstance(result, str)

    # Print the result
    print(result)

# Example test: generate_custom_id
def test_generate_custom_id():
    # Call the function and get the result
    result = generate_custom_id()

    # Check the length of the result
    assert len(result) == 15

    # Check if the result is a string
    assert isinstance(result, str)

    # Print the result
    print(result)


def test_get_password_hash():
    # Define the password
    password = "test_password"

    # Call the function and get the result
    result = get_password_hash(password)

    # Check if the result is a string
    assert isinstance(result, str)

    # Print the result
    print(result)

def test_verify_password():
    # Define the password
    password = "test_password"

    # Get the hash of the password
    hashed_password = get_password_hash(password)

    # Call the function and get the result
    result = verify_password(password, hashed_password)

    # Check the result
    assert result == True

    # Print the result
    print(result)