import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Text, BigInteger, Column, DateTime
from datetime import datetime
load_dotenv()

DATABASE_URL = os.getenv('database_url')
class Base(DeclarativeBase):
    pass
    
class UserLog(Base):
    __tablename__ = 'logs'  # имя таблицы в базе данных

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # уникальный идентификатор
    user_id = Column(BigInteger, nullable=False)  # ID пользователя
    command_request = Column(String(255), nullable=False)  # команда, отправленная пользователем
    timestamp = Column(DateTime, default=datetime.now)  # дата и время запроса
    response = Column(Text, nullable=False)  # ответ бота

    def __repr__(self):
        return f"<Log(id={self.id}, user_id={self.user_id}, command='{self.command_request}', timestamp='{self.timestamp}', response='{self.response}')>"

class UserSettings(Base):
    __tablename__ = 'user_settings'  # имя таблицы в базе данных

    user_id = Column(BigInteger, primary_key=True)  # уникальный ID пользователя
    fixed_city = Column(String(100), nullable=True)  # выбранный город

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, city='{self.fixed_city}')>"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)