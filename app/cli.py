"""CLI utility for managing member data and security questions.

Usage:
    python -m app.cli set-email <username> <email>
    python -m app.cli add-question
    python -m app.cli list-questions
"""
import sys

from sqlmodel import Session, select

from app.database import engine
from app.models import GlobalQuestion, Member


def set_email(username: str, email: str) -> None:
    with Session(engine) as session:
        member = session.exec(
            select(Member).where(Member.username == username)
        ).first()
        if member is None:
            print(f"Error: no member with username '{username}'")
            sys.exit(1)
        member.email = email
        session.add(member)
        session.commit()
        print(f"Set email for {member.name} ({member.username}) to {email}")


def add_question() -> None:
    print("Add a new security question\n")

    question = input("Question: ").strip()
    if not question:
        print("Error: question cannot be empty.")
        sys.exit(1)

    option_a = input("Option A: ").strip()
    option_b = input("Option B: ").strip()
    option_c = input("Option C: ").strip()
    option_d = input("Option D: ").strip()

    if not all([option_a, option_b, option_c, option_d]):
        print("Error: all four options are required.")
        sys.exit(1)

    correct = input("Correct answer (a/b/c/d): ").strip().lower()
    if correct not in ("a", "b", "c", "d"):
        print("Error: correct answer must be a, b, c, or d.")
        sys.exit(1)

    with Session(engine) as session:
        q = GlobalQuestion(
            question=question,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct,
        )
        session.add(q)
        session.commit()
        print(f"\nQuestion #{q.id} added successfully.")


def list_questions() -> None:
    with Session(engine) as session:
        questions = session.exec(select(GlobalQuestion)).all()
        if not questions:
            print("No questions found.")
            return
        for q in questions:
            print(f"\n#{q.id}  {q.question}")
            print(f"   a) {q.option_a}")
            print(f"   b) {q.option_b}")
            print(f"   c) {q.option_c}")
            print(f"   d) {q.option_d}")
            print(f"   Answer: {q.correct_answer}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    command = args[0]
    if command == "set-email":
        if len(args) != 3:
            print("Usage: python -m app.cli set-email <username> <email>")
            sys.exit(1)
        set_email(args[1], args[2])
    elif command == "add-question":
        add_question()
    elif command == "list-questions":
        list_questions()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
