import pandas as pd
import os
import streamlit as st
from ai_search import ai_search_component
import requests
import random

# ============ Your existing functions ============

# 🗺️ Geocoding using OpenCage Geocoder
def geocode_location(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {'q': place_name, 'key': '8e8875148f2f42e791dd420015550342', 'limit': 1}
    try:
        resp = requests.get(url, params=params, timeout=10).json()
        if resp.get('results'):
            geo = resp['results'][0]['geometry']
            return geo['lat'], geo['lng']
    except:
        pass
    return None, None

# Updated Nearby places via Overpass API
def get_nearby_places(lat, lon, query, label, radius=2000):
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node[{query}](around:{radius},{lat},{lon});
      way[{query}](around:{radius},{lat},{lon});
      relation[{query}](around:{radius},{lat},{lon});
    );
    out center;
    """
    try:
        response = requests.post(url, data={"data": query}, timeout=15)
        data = response.json()
        places = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name")
            if name:
                places.append(name)
        return places[:10] if places else [f"No {label} found"]
    except Exception as e:
        return [f"Error fetching {label}: {e}"]

def avg_housing_cost(place):
    avg_rent_2bed = random.randint(1500, 3500)
    avg_price_2bed = random.randint(250000, 750000)
    return {
        'avg_rent_2bed': f"${avg_rent_2bed:,}",
        'avg_price_2bed': f"${avg_price_2bed:,}"
    }

def crime_rate(place):
    return random.choice(['Low', 'Medium', 'High'])

def commute_score(place):
    score = random.randint(1, 10)
    mode = random.choice(["car", "train", "bus", "bike", "walk"])
    return score, mode

def walkability_score(lat, lon):
    return random.randint(1, 100)

def diversity_index(place):
    return round(random.uniform(0.3, 0.9), 2)

def pet_score(green_count, walk_score):
    return round((green_count * 10 + walk_score) / 2)

def parking_score(lat, lon):
    parks = get_nearby_places(lat, lon, 'amenity=parking', 'parking')
    return len(parks)

def get_all_metrics(place, lat, lon):
    housing = avg_housing_cost(place)
    crime = crime_rate(place)
    schools = get_nearby_places(lat, lon, 'amenity=school', 'schools') + get_nearby_places(lat, lon, 'amenity=college', 'colleges')
    schools_with_ratings = [f"{school} (Rating: {random.randint(1,10)}/10)" for school in schools]
    commute_sc, commute_type = commute_score(place)
    parks = get_nearby_places(lat, lon, 'leisure=park', 'parks')
    walk_sc = walkability_score(lat, lon)
    gyms = get_nearby_places(lat, lon, 'leisure=fitness_centre', 'gyms')
    shopping = get_nearby_places(lat, lon, 'shop', 'shopping')
    hospitals = get_nearby_places(lat, lon, 'amenity=hospital', 'hospitals')
    parking_ct = parking_score(lat, lon)
    div_ix = diversity_index(place)
    pet_sc = pet_score(walk_sc, len(parks))

    return {
        "Average Rent (2 bed)": housing['avg_rent_2bed'],
        "Average Sale Price (2 bed)": housing['avg_price_2bed'],
        "Crime Rate": crime,
        "Schools Nearby": schools_with_ratings,
        "Commute Score": commute_sc,
        "Transit Type": commute_type,
        "Green Space (parks count)": len(parks),
        "Walkability Score": walk_sc,
        "Gyms Nearby": gyms,
        "Shopping Nearby": shopping,
        "Hospitals Nearby": hospitals,
        "Parking Score (count)": parking_ct,
        "Diversity Index": div_ix,
        "PET Score": pet_sc
    }

# ============ Streamlit UI Setup ============

st.set_page_config(page_title="Neighborhood Insights", layout="centered")
st.title("Where to live next?")

mode = st.radio("Mode:", ("Compare Two Places", "Single Place"))
place1 = st.text_input("Place 1 (City, State)", "Cambridge, MA")
place2 = st.text_input("Place 2 (City, State)", "Somerville, MA") if mode == "Compare Two Places" else None
# ... Your entire original code unchanged above ...

if st.button("Show Insights"):
    lat1, lon1 = geocode_location(place1)
    lat2, lon2 = (None, None)
    if mode == "Compare Two Places":
        lat2, lon2 = geocode_location(place2)

    if lat1 is None:
        st.error(f"Couldn't locate {place1}")
        st.stop()
    if mode == "Compare Two Places" and lat2 is None:
        st.error(f"Couldn't locate {place2}")
        st.stop()

    locs = [{'lat': lat1,'lon':lon1,'place':place1}]
    if mode == "Compare Two Places":
        locs.append({'lat':lat2,'lon':lon2,'place':place2})
    st.map(pd.DataFrame(locs))

    data1 = get_all_metrics(place1, lat1, lon1)
    data2 = get_all_metrics(place2, lat2, lon2) if mode=="Compare Two Places" else None

    if mode=="Compare Two Places":
        col1, col2 = st.columns(2)
        for col, place, data in [(col1, place1, data1), (col2, place2, data2)]:
            with col:
                st.subheader(place)
                for k,v in data.items():
                    if isinstance(v, list):
                        st.markdown(f"**{k}:**")
                        for item in v:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{k}:** {v}")
    else:
        st.subheader(place1)
        for k,v in data1.items():
            if isinstance(v, list):
                st.markdown(f"**{k}:**")
                for item in v:
                    st.markdown(f"- {item}")
            else:
                st.markdown(f"**{k}:** {v}")

    # ======= Add AI search bar below results =======
    st.markdown("---")
    st.header("🤖 Ask me anything about these neighborhoods")

    user_input = st.text_input("Your Question", key="ai_question_input")
    if st.button("Get Answer", key="ai_answer_button"):
        if user_input.strip():
            API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
            HF_TOKEN = os.getenv("HF_TOKEN")  # Your Hugging Face token
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}"
            }
            payload = {"inputs": user_input}
            with st.spinner("Thinking..."):
                response = requests.post(API_URL, headers=headers, json=payload)
                try:
                    result = response.json()
                    if isinstance(result, list) and "generated_text" in result[0]:
                        st.markdown(f"**Answer:** {result[0]['generated_text']}")
                    elif "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.warning("Unexpected response format.")
                except Exception as e:
                    st.error(f"Error parsing response: {e}")
        else:
            st.warning("Please enter a question.")
