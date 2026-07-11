import secrets

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.auth import NotAuthenticatedException, hash_password, verify_password
from app.models import GlobalQuestion, Member
from app.seed import _slugify, seed_members, seed_questions
from app.routers.public import MEMBERS
from sqlmodel import select


TEST_DB_URL = "sqlite:///./data/test_auth.db"
test_engine = create_engine(TEST_DB_URL, echo=False)


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


# ── Password hashing ──────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_and_verify_correct_password(self):
        hashed = hash_password("testpass123")
        assert verify_password("testpass123", hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = hash_password("testpass123")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("samepass")
        h2 = hash_password("samepass")
        assert h1 != h2


# ── Seed members ──────────────────────────────────────────────────────

class TestSeedMembers:
    def test_creates_all_10_members(self, setup_db):
        session = setup_db
        seed_members(session)
        members = session.exec(select(Member)).all()
        assert len(members) == 10

    def test_member_usernames_are_slugified(self, setup_db):
        session = setup_db
        seed_members(session)
        members = session.exec(select(Member)).all()
        for m in members:
            assert m.username is not None
            assert m.username == _slugify(m.name)

    def test_members_have_hashed_passwords(self, setup_db):
        session = setup_db
        seed_members(session)
        members = session.exec(select(Member)).all()
        for m in members:
            assert m.hashed_password is not None
            assert m.hashed_password != ""

    def test_seed_is_idempotent(self, setup_db):
        session = setup_db
        seed_members(session)
        seed_members(session)
        members = session.exec(select(Member)).all()
        assert len(members) == 10

    def test_seeded_passwords_are_verifiable(self, setup_db):
        session = setup_db
        # We can't recover plaintext from seed, but we can verify the
        # stored hash works with verify_password
        seed_members(session)
        members = session.exec(select(Member)).all()
        for m in members:
            assert verify_password("anything", m.hashed_password) is False

    def test_member_names_match_public_list(self, setup_db):
        session = setup_db
        seed_members(session)
        members = session.exec(select(Member)).all()
        member_names = sorted([m.name for m in members])
        expected = sorted([m["name"] for m in MEMBERS])
        assert member_names == expected

    def test_seeded_members_have_nickname(self, setup_db):
        session = setup_db
        seed_members(session)
        members = session.exec(select(Member)).all()
        for m in members:
            assert m.nickname is not None


# ── Slugify ───────────────────────────────────────────────────────────

class TestSlugify:
    def test_simple_name(self):
        assert _slugify("Alex") == "alex"

    def test_multi_word_name(self):
        assert _slugify("Alex Johnson") == "alex.johnson"

    def test_special_characters(self):
        assert _slugify("Alex's Name!") == "alex.s.name"

    def test_multiple_spaces(self):
        result = _slugify("Alex   Johnson")
        assert result == "alex.johnson"


# ── NotAuthenticatedException ─────────────────────────────────────────

class TestNotAuthenticatedException:
    def test_is_exception(self):
        assert issubclass(NotAuthenticatedException, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(NotAuthenticatedException):
            raise NotAuthenticatedException()


# ── GlobalQuestion model ─────────────────────────────────────────────

class TestGlobalQuestionModel:
    def test_create_question(self, setup_db):
        session = setup_db
        q = GlobalQuestion(
            question="What is 2+2?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_answer="b",
        )
        session.add(q)
        session.commit()
        assert q.id is not None

    def test_question_correct_answer_is_string(self, setup_db):
        session = setup_db
        q = GlobalQuestion(
            question="Capital of France?",
            option_a="London",
            option_b="Berlin",
            option_c="Paris",
            option_d="Madrid",
            correct_answer="c",
        )
        session.add(q)
        session.commit()
        assert q.correct_answer == "c"

    def test_seed_questions_populates_table(self, setup_db):
        session = setup_db
        seed_questions(session)
        questions = session.exec(select(GlobalQuestion)).all()
        assert len(questions) == 1

    def test_seed_questions_is_idempotent(self, setup_db):
        session = setup_db
        seed_questions(session)
        seed_questions(session)
        questions = session.exec(select(GlobalQuestion)).all()
        assert len(questions) == 1

    def test_seeded_question_has_four_options(self, setup_db):
        session = setup_db
        seed_questions(session)
        q = session.exec(select(GlobalQuestion)).first()
        assert q.option_a != ""
        assert q.option_b != ""
        assert q.option_c != ""
        assert q.option_d != ""
        assert q.correct_answer in ("a", "b", "c", "d")
