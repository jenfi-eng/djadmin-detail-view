import factory
import faker
from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from ..models import Company, Contact

fake = faker.Faker()


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company")
    address = factory.Faker("address")
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.Faker("email")
    website = factory.Faker("url")
    description = factory.Faker("text")
    is_active = True


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker("name")
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.Faker("email")
    is_active = True


class UserFactory(DjangoModelFactory):
    @post_generation
    def password(self, create: bool, extracted, **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)
        self.save()

    class Meta:
        model = get_user_model()
        django_get_or_create = ["email"]
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False
