import logging

_LOGGER = logging.getLogger(__name__)

def get_wave_score(height, metric):
    return {
      "douglas_scale": get_douglas_scale(height, metric),
      "face_scale": get_face_scale(height, metric)
    }

def get_face_scale(height, metric):
    scores = [
        {
            "score": 1,
            "height_min_ft": 0,
            "height_max_ft": 1,
            "height_min_m": 0,
            "height_max_m": 0.30,
            "desc": "Ankle-shin"
        },
        {
            "score": 2,
            "height_min_ft": 1,
            "height_max_ft": 2,
            "height_min_m": 0.30,
            "height_max_m": 0.60,
            "desc": "Knee-thigh"
        },
        {
            "score": 3,
            "height_min_ft": 2,
            "height_max_ft": 3,
            "height_min_m": 0.60,
            "height_max_m": 0.91,
            "desc": "Waist-belly"
        },
        {
            "score": 4,
            "height_min_ft": 3,
            "height_max_ft": 4,
            "height_min_m": 0.91,
            "height_max_m": 1.21,
            "desc": "Chest-shoulder"
        },
        {
            "score": 5,
            "height_min_ft": 4,
            "height_max_ft": 5,
            "height_min_m": 1.21,
            "height_max_m": 1.52,
            "desc": "Head high"
        },
        {
            "score": 6,
            "height_min_ft": 5,
            "height_max_ft": 6,
            "height_min_m": 1.52,
            "height_max_m": 1.82,
            "desc": "1' overhead"
        },
        {
            "score": 8,
            "height_min_ft": 6,
            "height_max_ft": 8,
            "height_min_m": 1.82,
            "height_max_m": 2.43,
            "desc": "3' overhead"
        },
        {
            "score": 10,
            "height_min_ft": 8,
            "height_max_ft": 10,
            "height_min_m": 2.43,
            "height_max_m": 3.04,
            "desc": "3' overhead"
        },
        {
            "score": 12,
            "height_min_ft": 10,
            "height_max_ft": 12,
            "height_min_m": 3.04,
            "height_max_m": 3.65,
            "desc": "2x overhead"
        },
        {
            "score": 15,
            "height_min_ft": 12,
            "height_max_ft": 15,
            "height_min_m": 3.65,
            "height_max_m": 1,
            "desc": "3x overhead"
        },
        {
            "score": 20,
            "height_min_ft": 15,
            "height_max_ft": 100,
            "height_min_m": 4.57,
            "height_max_m": 100,
            "desc": "Stupid big"
        }
    ]
    for score in scores:
        if height > score["height_min_" + metric] and height < score["height_max_" + metric]:
            return {
                "score": score["score"],
                "description": score["desc"],
                "scale_name": "Face height scale"
            }

def get_douglas_scale(height, metric):
    scores = [
        {
            "score": 1,
            "height_min_ft": 0,
            "height_max_ft": 0.32,
            "height_min_m": 0,
            "height_max_m": 0.10,
            "desc": "Calm"
        },
        {
            "score": 2,
            "height_min_ft": 0.32,
            "height_max_ft": 1.64,
            "height_min_m": 0.10,
            "height_max_m": 0.50,
            "desc": "Smooth"
        },
        {
            "score": 3,
            "height_min_ft": 1.64,
            "height_max_ft": 4.10,
            "height_min_m": 0.5,
            "height_max_m": 1.25,
            "desc": "Slight"
        },
        {
            "score": 4,
            "height_min_ft": 4.10,
            "height_max_ft": 8.20,
            "height_min_m": 1.25,
            "height_max_m": 2.50,
            "desc": "Moderate"
        },
        {
            "score": 5,
            "height_min_ft": 8.20,
            "height_max_ft": 13.12,
            "height_min_m": 2.50,
            "height_max_m": 4.00,
            "desc": "Rough"
        },
        {
            "score": 6,
            "height_min_ft": 13.12,
            "height_max_ft": 19.68,
            "height_min_m": 4.00,
            "height_max_m": 6.00,
            "desc": "Very Rough"
        },
        {
            "score": 7,
            "height_min_ft": 19.68,
            "height_max_ft": 29.52,
            "height_min_m": 6.00,
            "height_max_m": 9.00,
            "desc": "High"
        },
        {
            "score": 8,
            "height_min_ft": 29.52,
            "height_max_ft": 45.93,
            "height_min_m": 9.00,
            "height_max_m": 14.00,
            "desc": "Very high"
        },
        {
            "score": 9,
            "height_min_ft": 45.93,
            "height_max_ft": 200.00,
            "height_min_m": 14.00,
            "height_max_m": 200.00,
            "desc": "Phenomenal"
        }
    ]
    for score in scores:
        if height > score["height_min_" + metric] and height < score["height_max_" + metric]:
            return {
                "score": score["score"],
                "description": score["desc"],
                "scale_name": "Douglas sea scale"
            }
