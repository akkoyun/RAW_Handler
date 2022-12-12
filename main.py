# Import Libraries
from config import Database, Schema, Models, log_functions
from kafka import KafkaConsumer, KafkaProducer
from json import dumps
import json

# Create DB Models
Database.Base.metadata.create_all(bind=Database.DB_Engine)

# Kafka Consumer
Kafka_RAW_Consumer = KafkaConsumer('RAW', bootstrap_servers="165.227.154.147:9092", group_id="Data_Consumer", auto_offset_reset='earliest', enable_auto_commit=False)

# Defne Kafka Producers
Kafka_Producer = KafkaProducer(value_serializer=lambda m: dumps(m).encode('utf-8'), bootstrap_servers="165.227.154.147:9092")

def Handle_RAW_Topic():

	try:

		for Message in Kafka_RAW_Consumer:

			# handle Message.
			Kafka_Message = Schema.IoT_Data_Pack_Model(**json.loads(Message.value.decode()))

			# Handle Headers
			Command = Message.headers[0][1].decode('ASCII')
			Device_ID = Message.headers[1][1].decode('ASCII')
			Device_Time = Message.headers[2][1].decode('ASCII')
			Device_IP = Message.headers[3][1].decode('ASCII')

			# Print LOG
			log_functions.Log_Kafka_Header(Command, Device_ID, Device_IP, Device_Time, Message.topic, Message.partition, Message.offset)

			# Create Add Record Command
			New_Buffer_Post = Models.Incoming_Buffer(
				Buffer_Device_ID = Device_ID, 
				Buffer_Client_IP = Device_IP, 
				Buffer_Command = Command, 
				Buffer_Data = str(Kafka_Message))

			# Add and Refresh DataBase
			db = Database.SessionLocal()
			db.add(New_Buffer_Post)
			db.commit()
			db.refresh(New_Buffer_Post)

			# Print LOG
			print("Message recorded to Buffer DB with Buffer_ID : ", New_Buffer_Post.Buffer_ID)

			# Database Query
			IoT_Module_Query = db.query(Models.Module.Device_ID.like(Device_ID)).first()

			# Module Table Update
			if IoT_Module_Query == None:

				# Create Add Record Command
				New_Module_Post = Models.Module(
					Device_ID = Device_ID, 
					Device_Development = True, 
					Module_Name = "B100xx")
	
				db.add(New_Module_Post)
				db.commit()
				db.refresh(New_Module_Post)

				# Print LOG
				print("New module added with Module_ID : ", New_Module_Post.Buffer_ID)

			# Log
			print("Module exits on DB")
			print("................................................................................")

			# Close Database
			db.close()

			# Commit Message
			Kafka_RAW_Consumer.commit()

			# Set headers
			Kafka_Parser_Headers = [
				('Command', bytes(Command, 'utf-8')), 
				('ID', bytes(Device_ID, 'utf-8')), 
				('Device_Time', bytes(Device_Time, 'utf-8')), 
				('IP', bytes(Device_IP, 'utf-8'))]


			# Send Parsed Message to Queue
			Kafka_Producer.send("Device.Version", value=Kafka_Message.Device.Info.dict(exclude={'ID', 'Temperature', 'Humidity'}), headers=Kafka_Parser_Headers)
			Kafka_Producer.send("Device.IMU", value=Kafka_Message.Device.Info.dict(exclude={'ID', 'Hardware', 'Firmware'}), headers=Kafka_Parser_Headers)
			Kafka_Producer.send("Device.IoT_Module", value=Kafka_Message.Device.IoT.GSM.Module.dict(), headers=Kafka_Parser_Headers)


			# Send Parsed Message to Queue
#			Kafka_Producer.send("Device.Info", value=Kafka_Message.Device.Info.dict(exclude={'ID'}), headers=Kafka_Parser_Headers)
#			Kafka_Producer.send("Device.Power", value=Kafka_Message.Device.Power.dict(), headers=Kafka_Parser_Headers)
#			Kafka_Producer.send("Device.IoT", value=Kafka_Message.Device.IoT.dict(), headers=Kafka_Parser_Headers)
#			Kafka_Producer.send("Device.Payload", value=Kafka_Message.Payload.dict(exclude={'TimeStamp'}), headers=Kafka_Parser_Headers)

			print("Message parsed and sended to queue...")
			print("--------------------------------------------------------------------------------")


	finally:
		
		print("Error Accured !!")


# Handle All Message in Topic
Handle_RAW_Topic()
