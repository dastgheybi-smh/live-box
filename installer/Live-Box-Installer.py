from colorama import Fore


print(Fore.LIGHTWHITE_EX + f"""Welcome to {Fore.LIGHTGREEN_EX}Live Box{Fore.LIGHTWHITE_EX}
A place to share your {Fore.LIGHTMAGENTA_EX}codes{Fore.LIGHTWHITE_EX}""")

endpoint = input(f"Enter the server {Fore.LIGHTBLACK_EX}Endpoint URL{Fore.CYAN}: ")
bucket = input(f"{Fore.LIGHTWHITE_EX}Enter the server {Fore.LIGHTBLUE_EX}Bucket Name{Fore.CYAN}: ")
secret = input(f"{Fore.LIGHTWHITE_EX}Enter the bucket {Fore.LIGHTRED_EX}Secret Key{Fore.CYAN}: ")
access = input(f"{Fore.LIGHTWHITE_EX}Enter the bucket {Fore.LIGHTYELLOW_EX}Access Key{Fore.CYAN}: ")

with open("../secret.py", "w") as f:
    f.write(
        f"""ENDPOINT = "{endpoint}"
NAME = "{bucket}"
SECRET = "{secret}"
ACCESS_TOKEN = "{access}" """
    )
