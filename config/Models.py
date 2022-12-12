from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .Database import Base

# Incoming Buffer Database Model
class Incoming_Buffer(Base):

	# Define Buffer Database
	__tablename__ = "Incoming_Buffer"

	# Define Colomns
	Buffer_ID = Column(Integer, primary_key=True, nullable=False)
	Buffer_Created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Buffer_Device_ID = Column(String, nullable=True)
	Buffer_Command = Column(String, nullable=True)
	Buffer_Client_IP = Column(String, nullable=True)
	Buffer_Data = Column(String, nullable=True)

# Incoming Buffer Database Model
class Module(Base):

	# Define Buffer Database
	__tablename__ = "Module"

	# Define Colomns
	Module_ID = Column(Integer, primary_key=True, nullable=False)
	Module_Create_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Device_ID = Column(String, nullable=True)
	Device_Development = Column(Boolean, server_default=True)
	Module_Name = Column(String, nullable=True)
