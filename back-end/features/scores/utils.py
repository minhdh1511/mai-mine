def calculate_song_rank(song_score: float) -> str:
    """
    Takes the song_score (e.g., 100.50) and returns the rank (e.g., 'SSS+').
    """
    # TODO: Write your rank logic here!
    if(song_score >= 100.5):
        return 'SSS+'
    else:
        return 'skill issue lmao'


def calculate_rating(song_score: float, internal_difficulty: float) -> int:
    """
    Takes the score and internal difficulty and calculates the raw Maimai rating.
    """
    # TODO: Write your rating formula here!
    return 420