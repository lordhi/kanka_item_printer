import requests
import time
import re
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('API_KEY')
campaignId = os.getenv('CAMPAIGN_ID')
organisationId = os.getenv('ORGANISATION_ID')
attunementTagId = os.getenv('ATTUNEMENT_TAG_ID')

printTagId = 262897

def getCleanItemsForActiveMembers():
	items = getItemsForActiveMembers()

	return [stripItem(item) for item in items]

def removeTag(item, tagId=printTagId):
	newTags = item['tags']
	newTags.remove(tagId)

	full_url = 'https://kanka.io/api/1.0/' + getCampaignPreamble() + '/items/' + str(item['id'])
	r = requests.patch(full_url, headers = getHeaders(), data={'tags' : newTags})


def getReprintItems():
	itemEntities = getRequest(getCampaignPreamble() + '/entities?tags=' + str(printTagId))['data']
	items = [getItem(entity['child_id']) for entity in itemEntities]

	return [stripItem(item) for item in items]

def stripItem(item):
	item = item['data']

	cleanedItem = {
		'id': item['id'],
		'name': item['name'],
		'description': cleanupEntry(item['entry'])
	}

	typeThings = []
	if item['type']:
		typeThings.append(item['type'])
	if item['price']:
		typeThings.append(item['price'])

	cleanedItem['type'] = ','.join(typeThings) if len(typeThings) > 0 else ''
	if attunementTagId in item['tags']:
		cleanedItem['type'] += '<i>(Requires attunement)</i>'

	if 'posts' in item and len(item['posts']) > 0:
		post = sorted(item['posts'], key=lambda x: x['updated_at'])[0]
		if 'entry' in post:
			cleanedItem['description'] = cleanupEntry(post['entry'])
		if 'name' in post:
			cleanedItem['name'] = post['name']

	return cleanedItem

def cleanupEntry(entry):
	return entry.replace('\n', ' ').strip()

def getEntity(entityId):
	return getRequest(getCampaignPreamble() + '/entities/' + str(entityId) + '/?related')

def getEntityIdsForActiveMembers():
	characters = getCharactersForActiveMembers()['data']

	return [character['entity_id'] for character in characters]

def getItem(itemId):
	return getRequest(getCampaignPreamble() + '/items/' + str(itemId) + '?related=1')

def getItemsForActiveMembers():
	items = []

	chars = getCharactersForActiveMembers()
	for char in chars:
		inv = getInventory(char['data']['entity_id'])
		meta = inv['meta']
		itemsToAdd = inv['data']

		items += list(filter(hasItemId, itemsToAdd))

	items = [getItem(item['item_id']) for item in items]

	return items

def hasItemId(item):
	return 'item_id' in item and item['item_id'] != None

def getCharactersForActiveMembers():
	members = getActiveMembers()

	return [getCharacter(member['character_id']) for member in members]

def getInventory(entityId):
	return getRequest(getCampaignPreamble() + '/entities/' + str(entityId) + '/inventory')

def getCharacter(charId):
	return getRequest(getCampaignPreamble() + '/characters/' + str(charId))

def getActiveMembers():
	all_members = getOrganisationMembers()['data']
	active_members = filter(lambda x: x['status_id'] == 0, all_members)

	return list(active_members)

def getOrganisationMembers():
	return getRequest(getCampaignPreamble() + '/organisations/' + str(organisationId) + '/organisation_members')

def getOrganisations():
	return getRequest(getCampaignPreamble() + '/organisations')

def getCampaigns():
	return getRequest('campaigns')

def getHeaders():
	return {
		'Authorization': 'Bearer ' + token,
    	'Content-type': 'application/json'
	}

def getRequest(target_url):
	full_url = 'https://kanka.io/api/1.0/' + target_url
	r = requests.get(full_url, headers = getHeaders())

	if r.status_code == 429:
		print('RATE LIMITED! Sleeping...')
		time.sleep(60)
		return getRequest(target_url)
	
	return r.json()

def getCampaignPreamble():
	return 'campaigns/' + str(campaignId)