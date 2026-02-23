import argparse

from finalproject_1_perfilova.core.usecases import register_user, login_user


def main():
    parser = argparse.ArgumentParser(prog="project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    p_reg = subparsers.add_parser("register")
    p_reg.add_argument("--username", required=True)
    p_reg.add_argument("--password", required=True)

    # login
    p_login = subparsers.add_parser("login")
    p_login.add_argument("--username", required=True)
    p_login.add_argument("--password", required=True)

    args = parser.parse_args()

    try:
        if args.command == "register":
            user = register_user(args.username, args.password)
            print(
                f"Пользователь '{user.username}' зарегистрирован (id={user.user_id})."
                f"Войдите: login --username {user.username} --password ****"
            )

        elif args.command == "login":
            user = login_user(args.username, args.password)
            print(f"Вы вошли как '{user.username}'")

    except Exception as e:
        print(str(e))