import requests
import json

query = '''
query ($username: String, $type: MediaType) {
  MediaListCollection(userName: $username, type: $type) {
	lists {
	  entries {
		status
		score(format: POINT_10)
		progress
		progressVolumes
		repeat
		priority
		notes
		startedAt { year, month, day }
		completedAt { year, month, day }
		media {
		  idMal
		  title { romaji }
		  episodes
		  chapters
		  volumes
		  siteUrl
		}
	  }
	}
  }
}
'''

variables = {
	'username': 'ynot254',
	'type': 'ANIME'
}

url = 'https://graphql.anilist.co'

def main():
	print('''
	┏━━ AniList to MAL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
	┃ An export tool for Anilist to import to MyAnimeList.          ┃
	┃ Enter your username, and this will generate an XML file       ┃
	┃ to import here: https://myanimelist.net/import.php            ┃
	┃ Made by Nathan Wentworth (https://nathanwentworth.co)         ┃
	┃ Modified by Antony Nyagah (https://tonynyagah.github.io)      ┃
	┃ Report any problems here: https://twitter.com/NyagahTony      ┃
	┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
''')
	getUserData()

def getUserData():
	variables['username'] = input("→ Anilist username: ")

	if variables['username'] == '':
		print('Please enter a valid username!')
		getUserData()
	else:
		getAnilistData()

# Make the HTTP Api request
def getAnilistData():
	response = requests.post(url, json={'query': query, 'variables': variables})
	jsonData = response.json()
	listEntries = jsonData['data']['MediaListCollection']['lists']
	# prettified results for easy reading
	readableData = json.dumps(listEntries, indent=2, sort_keys=True) 
	# print(readableData)
	printAnilistData(listEntries)
	convertAnilistData(listEntries)

def printAnilistData(data):

	listLength = len(data); # 5 because from current to planning

	print('↓ Exported List ↓')
	for x in range(0, listLength):
		print('\n##### ' + data[x]['entries'][x]['status'] + ' #####')
		entryLength = len(data[x]['entries'])
		for e in range(0, entryLength):
			print(' - ' + data[x]['entries'][e]['media']['title']['romaji'])
	print('\n✔︎ Successfully exported!')
	print('\nGo to https://myanimelist.net/import.php and select "MyAnimeList Import" under import type.\n')

def convertAnilistData(data):

	plan_to_watch = len(data[0]['entries'])
	completed = len(data[1]['entries'])
	dropped = len(data[2]['entries'])
	on_hold = len(data[3]['entries'])
	watching = len(data[4]['entries'])
	total = plan_to_watch + completed + dropped + on_hold + watching
	
	output = '''
	<?xml version="1.0" encoding="UTF-8" ?>
			<!--
			 Created by XML Export feature at MyAnimeList.net
			 Programmed by Xinil
			 Last updated 5/27/2008
			-->

			<myanimelist>

	'''

	userInfo = '            <myinfo>\n'
	userInfo += '                    <user_id>4381285</user_id>\n'
	userInfo += '                    <user_name>' + variables['username'] + '</user_name>\n'
	userInfo += '                    <user_export_type>1</user_export_type>\n'
	userInfo += '                    <user_total_anime>' + str(total) + '</user_total_anime>\n'
	userInfo += '                    <user_total_watching>' + str(watching) + '</user_total_watching>\n'
	userInfo += '                    <user_total_completed>' + str(completed) + '</user_total_completed>\n'
	userInfo += '                    <user_total_onhold>'+ str(on_hold) +'</user_total_onhold>\n'
	userInfo += '                    <user_total_dropped>' + str(dropped) + '</user_total_dropped>\n'
	userInfo += '                    <user_total_plantowatch>' +str(plan_to_watch) + '</user_total_plantowatch>\n'
	userInfo += '                </myinfo>\n\n'

	mediaInfo = ''

	lastLine = '            </myanimelist>'
	
	for n in range(0, len(data)):
		for i in range(0, len(data[n]['entries'])):

			yearStarted = data[n]['entries'][i]['startedAt']['year']
			monthStarted = data[n]['entries'][i]['startedAt']['month']
			dayStarted = data[n]['entries'][i]['startedAt']['day']
			yearCompleted = data[n]['entries'][i]['completedAt']['year']
			monthCompleted = data[n]['entries'][i]['completedAt']['month']
			dayCompleted = data[n]['entries'][i]['completedAt']['day']

			if yearStarted == None:
				yearStarted = '0000'
			if yearCompleted == None:
				yearCompleted = '0000'
			if monthStarted == None:
				monthStarted = '00'
			if monthCompleted == None:
				monthCompleted = '00'
			if dayStarted == None:
				dayStarted = '00'
			if dayCompleted == None:
				dayCompleted = '00'

			mediaInfo += '				    <anime>\n'
			mediaInfo += '					    <series_animedb_id>' + str(data[n]['entries'][i]['media']['idMal']) + '</series_animedb_id>\n'
			mediaInfo += '                        <series_title><![CDATA[' + str(data[n]['entries'][i]['media']['title']['romaji']) + ']]></series_title>\n'
			# mediaInfo += '					    <series_type></series_type>\n'
			mediaInfo += '                        <series_episodes>' + str(data[n]['entries'][i]['media']['episodes']) +'</series_episodes>\n'
			mediaInfo += '					    <my_id>0</my_id>\n'
			mediaInfo += '					    <my_watched_episodes>' + str(data[n]['entries'][i]['progress']) + '</my_watched_episodes>\n'
			mediaInfo += '						<my_start_date>' + str(yearStarted) + '-' + str(monthStarted) + '-' + str(dayStarted) + '</my_start_date>\n'
			mediaInfo += '						<my_finish_date>' + str(yearCompleted) + '-' + str(monthCompleted) + '-' + str(dayCompleted) + '</my_finish_date>\n'
			mediaInfo += '				    </anime>\n\n'
	
	
	results = output + userInfo + mediaInfo + lastLine
	print(results)
	print("Anime count: %d" % total)

main()