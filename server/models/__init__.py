# CREATE DATABASE django_nlp
# DEFAULT CHARACTER SET utf8
# DEFAULT COLLATE utf8_unicode_ci;

from .document import Document
from .entity import Entity
from .relation import Relation
from .user import User
from .collection import Collection
from .entity_category import EntityCategory
from .entity_property import EntityProperty
from .relation_category import RelationCategory
from .relation_property import RelationProperty
from .entity_as_argument import EntityAsArgument
from .relation_as_argument import RelationAsArgument
from .argument_role import ArgumentRole
from .document_property import DocumentProperty