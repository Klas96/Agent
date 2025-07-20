from utils.user_db import get_tokens

if __name__ == "__main__":
    email = "klas0holmgren@gmail.com"
    tokens = get_tokens(email)
    print(f"Token balance for {email}: {tokens}") 