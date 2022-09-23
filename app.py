from flask import Flask, render_template, request, redirect, url_for
from neo4j import GraphDatabase, basic_auth
import json

# Open Config File
configfile = open("config.json")
config = json.load(configfile)


# DB setup
# Graph DB Connection
graph_user = config['neo4j_settings']['user']
graph_password = config['neo4j_settings']['password']
graph_url = config['neo4j_settings']['url']
driver = GraphDatabase.driver(graph_url, auth=basic_auth(graph_user, graph_password))

# Flask setup
app = Flask(__name__)

@app.route('/')
def index():
	keys = request.args.get("keys", default="")
	keys = keys.lower()
	splitedkeys = keys.split()
	if keys == "":
		return render_template("index.html")
	else:
		if splitedkeys[0] == "meet":
			data = []
			# Query Interaction
			with driver.session() as session:
				GetInteractionUser = session.run("match (a:Users {NIK:$NIK})-[r1]->(b:Interactions)<-[r2]-(c) return a,b,c",NIK=int(splitedkeys[1]))

				for i in GetInteractionUser:
					# GET LABEL OF NODE
					node_data = i.data()
					d = node_data['b']
					if list(i.values()[2].labels)[0] == "Places":
						d["Visit"] = node_data['c']
					else:
						d["Interaction"] = node_data['c']
					data.append(d)
			driver.close()
			dictdata = {"user":splitedkeys[1], "data":data}
			return render_template("index.html", data=dictdata, type=4)
		elif splitedkeys[0] == "jumlah":
			with driver.session() as session:
				GetJumlahUser = session.run("match (a:Users) return count(a) as jumlah_user")
				data = GetJumlahUser.data()[0]['jumlah_user']
			return render_template("index.html", data=data, type=1)
		elif splitedkeys[0] == "user":
			if len(splitedkeys)==1:
				with driver.session() as session:
					GetUsers = session.run("match (n:Users) return n as users")
					data = []
					for i in GetUsers.data():
						data.append(i['users'])
				return render_template('index.html', data=data , type=5)
			else:
				if splitedkeys[1] == "status":
					with driver.session() as session:
						GetJumlahStatusUserStatus = session.run("match (n:Users) return n.Status as status, count(*) as jumlah_status")
						labels = []
						datas = []
						data = {}
						for i in GetJumlahStatusUserStatus.data():
							labels.append(str(i['status']))
							datas.append(i["jumlah_status"])
							if i['status'] == "Negatif":
								data['Negatif'] = i['jumlah_status']
							else:
								data['Positif'] = i['jumlah_status']
						data['labels'] = labels
						data['datas'] = datas
					return render_template("index.html", data=data, type=2)
				elif splitedkeys[1] == "gender":
					with driver.session() as session:
						GetJumlahGenderUser = session.run("match (n:Users) return n.Gender as gender, count(*) as jumlah_gender")
						labels = []
						datas = []
						data = {}
						for i in GetJumlahGenderUser.data():
							labels.append(str(i['gender']))
							datas.append(i["jumlah_gender"])
							if i['gender'] == "Perempuan":
								data['Perempuan'] = i['jumlah_gender']
							else:
								data['Laki-Laki'] = i['jumlah_gender']
						data['labels'] = labels
						data['datas'] = datas
					return render_template("index.html", data=data, type=3)
				else:
					return "unknown command"
		else:
			return "unknown command"

if __name__ == '__main__':
	app.run(debug=True)