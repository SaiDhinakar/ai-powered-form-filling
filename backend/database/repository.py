from typing import List, Optional

from sqlalchemy.orm import Session

from .models import User, Entity, Template, ExtractedData


class UserRepository:
    """Repository for User model operations."""
    
    @staticmethod
    def create(db: Session, username: str, hashed_password: str) -> User:
        """Create a new user."""
        user = User(username=username, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Delete a user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False


class EntityRepository:
    """Repository for Entity model operations."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        name: str,
        entity_metadata: Optional[dict] = None,
        doc_path: Optional[str] = None
    ) -> Entity:
        """Create a new entity."""
        entity = Entity(
            user_id=user_id,
            name=name,
            entity_metadata=entity_metadata,
            doc_path=doc_path
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    @staticmethod
    def get_by_id(db: Session, entity_id: int) -> Optional[Entity]:
        """Get entity by ID."""
        return db.query(Entity).filter(Entity.id == entity_id).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Entity]:
        """Get all entities for a user."""
        return db.query(Entity).filter(Entity.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        entity_id: int,
        name: Optional[str] = None,
        entity_metadata: Optional[dict] = None,
        doc_path: Optional[str] = None
    ) -> Optional[Entity]:
        """Update an entity."""
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if entity:
            if name is not None:
                entity.name = name
            if entity_metadata is not None:
                entity.entity_metadata = entity_metadata
            if doc_path is not None:
                entity.doc_path = doc_path
            db.commit()
            db.refresh(entity)
        return entity
    
    @staticmethod
    def delete(db: Session, entity_id: int) -> bool:
        """Delete an entity by ID."""
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if entity:
            db.delete(entity)
            db.commit()
            return True
        return False


class TemplateRepository:
    """Repository for Template model operations."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        path: str,
        file_hash: str,
        lang: Optional[str] = None,
        word: Optional[str] = None
    ) -> Template:
        """Create a new template."""
        template = Template(
            user_id=user_id,
            path=path,
            file_hash=file_hash,
            lang=lang,
            word=word
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def get_by_id(db: Session, template_id: int) -> Optional[Template]:
        """Get template by ID."""
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def get_by_hash(db: Session, file_hash: str) -> Optional[Template]:
        """Get template by file hash."""
        return db.query(Template).filter(Template.file_hash == file_hash).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Template]:
        """Get all templates with pagination."""
        return db.query(Template).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, template_id: int) -> bool:
        """Delete a template by ID."""
        template = db.query(Template).filter(Template.id == template_id).first()
        if template:
            db.delete(template)
            db.commit()
            return True
        return False


class ExtractedDataRepository:
    """Repository for ExtractedData model operations."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        entity_id: int,
        file_hash: str,
        status: int = 0,
        extracted_toon_object: Optional[dict] = None
    ) -> ExtractedData:
        """Create a new extracted data record."""
        extracted_data = ExtractedData(
            user_id=user_id,
            entity_id=entity_id,
            file_hash=file_hash,
            status=status,
            extracted_toon_object=extracted_toon_object
        )
        db.add(extracted_data)
        db.commit()
        db.refresh(extracted_data)
        return extracted_data
    
    @staticmethod
    def get_by_id(db: Session, extracted_data_id: int) -> Optional[ExtractedData]:
        """Get extracted data by ID."""
        return db.query(ExtractedData).filter(ExtractedData.id == extracted_data_id).first()
    
    @staticmethod
    def get_by_entity(db: Session, entity_id: int) -> List[ExtractedData]:
        """Get all extracted data for an entity."""
        return db.query(ExtractedData).filter(ExtractedData.entity_id == entity_id).all()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ExtractedData]:
        """Get all extracted data for a user."""
        return db.query(ExtractedData).filter(ExtractedData.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_status(
        db: Session,
        extracted_data_id: int,
        status: int,
        extracted_toon_object: Optional[dict] = None
    ) -> Optional[ExtractedData]:
        """Update extracted data status and object."""
        extracted_data = db.query(ExtractedData).filter(ExtractedData.id == extracted_data_id).first()
        if extracted_data:
            extracted_data.status = status
            if extracted_toon_object is not None:
                extracted_data.extracted_toon_object = extracted_toon_object
            db.commit()
            db.refresh(extracted_data)
        return extracted_data
    
    @staticmethod
    def delete(db: Session, extracted_data_id: int) -> bool:
        """Delete an extracted data record by ID."""
        extracted_data = db.query(ExtractedData).filter(ExtractedData.id == extracted_data_id).first()
        if extracted_data:
            db.delete(extracted_data)
            db.commit()
            return True
        return False