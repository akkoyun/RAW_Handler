# Import Libraries
from datetime import datetime
from Setup import Database, Schema, Models
from Setup.Config import APP_Settings
from kafka import KafkaConsumer, KafkaProducer
import logging, coloredlogs
import json
from json import dumps

# Set Log Options
Service_Logger = logging.getLogger(__name__)
logging.basicConfig(filename='Log/Service.LOG', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set Log Colored
coloredlogs.install(level='DEBUG', logger=Service_Logger)

# Create DB Models
Database.Base.metadata.create_all(bind=Database.DB_Engine)

# Kafka Consumer
Kafka_Consumer = KafkaConsumer('RAW', bootstrap_servers=f"{APP_Settings.POSTOFFICE_KAFKA_HOSTNAME}:{APP_Settings.POSTOFFICE_KAFKA_PORT}", group_id="Data_Consumer", auto_offset_reset='earliest', enable_auto_commit=False)

# Defne Kafka Producers
Kafka_Producer = KafkaProducer(value_serializer=lambda m: dumps(m).encode('utf-8'), bootstrap_servers=f"{APP_Settings.POSTOFFICE_KAFKA_HOSTNAME}:{APP_Settings.POSTOFFICE_KAFKA_PORT}")

def RAW_Handler():

	try:

		for Message in Kafka_Consumer:
	
			# handle Message.
			Kafka_Message = Schema.IoT_Data_Pack_Model(**json.loads(Message.value.decode()))
			
			class Headers:
				Command = Message.headers[0][1].decode('ASCII')
				Device_ID = Message.headers[1][1].decode('ASCII')
				Device_Time = Message.headers[2][1].decode('ASCII')
				Device_IP = Message.headers[3][1].decode('ASCII')
				Size = Message.headers[4][1].decode('ASCII')

			# Create Add Record Command
			New_Buffer = Models.Incoming_Buffer(
				Buffer_Device_ID = Headers.Device_ID, 
				Buffer_Client_IP = Headers.Device_IP, 
				Buffer_Command = Headers.Command, 
				Buffer_Data = str(Kafka_Message))

			# Define DB
			DB_Buffer = Database.SessionLocal()

			# Add and Refresh DataBase
			DB_Buffer.add(New_Buffer)
			DB_Buffer.commit()
			DB_Buffer.refresh(New_Buffer)

			# Close Database
			DB_Buffer.close()

			# Commit Message
			Kafka_Consumer.commit()

			# ------------------------------------------

			# Set headers
			Kafka_Parser_Headers = [
				('Command', bytes(Headers.Command, 'utf-8')), 
				('Device_ID', bytes(Headers.Device_ID, 'utf-8')), 
				('Device_Time', bytes(Headers.Device_Time, 'utf-8')), 
				('Device_IP', bytes(Headers.Device_IP, 'utf-8')),
				('Size', bytes(Headers.Size, 'utf-8')),
				('Buffer_ID', bytes(str(New_Buffer.Buffer_ID), 'utf-8'))]





			# Send Message to Queue
			Kafka_Producer.send("Device", value=Kafka_Message.Device.dict(), headers=Kafka_Parser_Headers)

			# Send PowerStat Payload to Queue
			if Kafka_Message.Payload.PowerStat is not None:
				Kafka_Producer.send("PowerStat.Payload", value=Kafka_Message.Payload.PowerStat.dict(), headers=Kafka_Parser_Headers)

			# Send WeatherStat Payload to Queue
			if Kafka_Message.Payload.WeatherStat is not None:
				Kafka_Producer.send("WeatherStat.Payload", value=Kafka_Message.Payload.WeatherStat.dict(), headers=Kafka_Parser_Headers)






#			Kafka_Producer.send("RAW.Discord", value=Kafka_Message.dict(), headers=Kafka_Parser_Headers)

			# Print Log
			Service_Logger.debug(f"RAW Data processed and sended to parsers. ['{Headers.Device_ID}'] - ['{Headers.Command}'] at ['{Headers.Device_Time}']")

	finally:
		
		print("Error Accured !!")


# Handle All Message in Topic
RAW_Handler()

