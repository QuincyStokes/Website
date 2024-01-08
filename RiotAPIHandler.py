from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/get_recent_games": {"origins": "*"}})
RIOT_API_KEY = "RGAPI-2ec2ac36-804a-4200-b116-ab7d45ec11eb"
RIOT_API_BASE_URL = "https://americas.api.riotgames.com"
os.environ["OPENAI_API_KEY"] = "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"
headers = {"X-Riot-Token": RIOT_API_KEY}


@app.route('/get_recent_games', methods=['POST'])
def get_recent_games():
    #get Username
    gameName = request.json["summonername"]
    tagLine = request.json["tagline"]

    puuid = get_puuid(gameName, tagLine)

    match_ids = get_match_IDs(puuid)
    #now we need to fetch more specific data with these match IDs

    grabbed_player_info = {"totalGameLength": 0, "totalKills": 0, "totalDeaths": 0, 
                           "totalAssists" : 0, "totalDetectorWards" : 0, "totalWards":0, "totalTimeSpentDead": 0}


    print(match_ids)
    print(type(match_ids))
    for match_id in match_ids: #match_ids confirmed to be a list
        player = get_correct_participant(puuid, match_id)
        print("PLAYER TYPE")
        print(type(player))
        grabbed_player_info["totalGameLength"] += player["timePlayed"]
        grabbed_player_info["totalKills"] += player["kills"]
        grabbed_player_info["totalDeaths"] += player["deaths"]
        grabbed_player_info["totalAssists"] += player["assists"]
        grabbed_player_info["totalDetectorWards"] += player["detectorWardsPlaced"]
        grabbed_player_info["totalWards"] += player["wardsPlaced"]
        grabbed_player_info["totalTimeSpentDead"] += player["totalTimeSpentDead"]


    return grabbed_player_info

        
def get_correct_participant(puuid, match_id):
    chosenParticipant = None  # Use None to indicate no participant found initially
    print("INSIDE GET_CORRECT_PARTICIPANT")
    try: 
        match_id_response = requests.get(f'{RIOT_API_BASE_URL}/lol/match/v5/matches/{match_id}', headers=headers)
        print("here too!", match_id_response.status_code)
        match_id_response.raise_for_status()
        print(match_id_response.status_code)
        if match_id_response.status_code == 200:
            match_id_json = match_id_response.json()
            print("MATCH_ID_JSON: ", type(match_id_json))
            match_id_participants = match_id_json["info"]["participants"]

            for participant in match_id_participants:
                if participant["puuid"] == puuid:
                    chosenParticipant = participant
                    break  # Stop the loop once a participant is found
                    
            print("CHOSEN PARTICIPANT: ", type(chosenParticipant))
            return chosenParticipant
        else:
            return jsonify({"error": str(match_id_response.text)})

    except Exception as e:
        return jsonify({'error': str(e)})


def get_puuid(gameName, tagLine):
    try:
            
        puuid_response = requests.get(f'{RIOT_API_BASE_URL}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}', headers=headers)
        puuid_response.raise_for_status()
        
        if puuid_response.status_code == 200:
            puuid_data = puuid_response.json()
            puuid = puuid_data['puuid']
            return puuid
        else:
            return jsonify({"error" : str(puuid_response.text)})


    except Exception as e:
        return jsonify({'error': str(e)})


def get_match_IDs(puuid):
    
    try:
        response = requests.get(f'{RIOT_API_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids', headers=headers)

        """
        if response.status_code == 400:
            formatted_response = f"response_status_code: {response.status_code}\n" \
                             f"response_headers: {dict(response.headers)}\n" \
                             f"response_content: {response.content.decode('utf-8')}"
            return formatted_response
        """
        if response.status_code == 200:
            #recent_20_games_data = response.json()
            match_ids = response.json()
            return match_ids

        else:
            return jsonify({"error" : str(response.text)})

        #insights = get_match_insights(recent_20_games_data)


        
    except Exception as e:
        return jsonify({'error': str(e)})
    

""" def get_match_insights(match_ids):
    prompt = f"Looking at these Match ID's: {match_ids}, How many of them are there?"

    response = openai.completions.create(
        model="text-davinci-002",
        prompt=prompt,
        #max_tokens=500
    )

    generated_text = response.choices[0].text
    return generated_text

"""

if __name__ == "__main__":
    print("Hello World!")
    app.run(debug=True)
