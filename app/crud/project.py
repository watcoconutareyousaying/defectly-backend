from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, project: ProjectCreate, owner_id: int):
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=owner_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int):
    return db.query(Project).filter((Project.id == project_id) & (Project.is_deleted == False)).first()


def get_projects(db: Session, owner_id: int):
    return db.query(Project).filter((Project.owner_id == owner_id) & (Project.is_deleted == False)).all()


def update_project(db: Session, project: Project, updates: ProjectUpdate):
    if updates.name is not None:
        project.name = updates.name
    if updates.description is not None:
        project.description = updates.description

    db.commit()
    db.refresh(project)
    return project


def soft_delete_project(db: Session, project: Project):
    project.soft_delete()
    db.commit()
    return project


def permanently_delete_project(db: Session, project: Project):
    db.delete(project)
    db.commit()


def permanently_delete_expired_projects(db: Session):
    expired_projects = db.query(Project).filter(
        Project.is_deleted == True).all()  # type: ignore
    for project in expired_projects:
        if project.is_expired():
            db.delete(project)
    db.commit()
