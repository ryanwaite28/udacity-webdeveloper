import datetime, os, sys, random, string

# --- Code --- #

options = [
    {
        'answer': 'Stevie Wonder',
        'hintONE': 'i am blind.',
        'hintTWO': 'i am a musician.',
        'hintTHREE': 'i was born in 1950.'
    },
    {
        'answer': 'Denzel Washington',
        'hintONE': 'i am an actor, born in 1954.',
        'hintTWO': 'i have 4 children.',
        'hintTHREE': 'i received three Golden Globe awards, a Tony Award, and two Academy Awards.'
    },
    {
        'answer': 'Whitney Houston',
        'hintONE': 'i am a singer.',
        'hintTWO': 'i passed away in 2012.',
        'hintTHREE': 'i am from newark, new jersey.'
    },
    {
        'answer': 'Serena Williams',
        'hintONE': 'i am a professional tennis player.',
        'hintTWO': 'i was born in 1981.',
        'hintTHREE': 'i am ranked no. 1.'
    },
    {
        'answer': 'Barack Obama',
        'hintONE': 'i was born 1961.',
        'hintTWO': 'i have 2 children.',
        'hintTHREE': 'i am involved with politics.'
    },
    {
        'answer': 'Ernest Wilson',
        'hintONE': 'i was born 1971.',
        'hintTWO': 'i am from chicago.',
        'hintTHREE': 'i am a music producer.'
    },
    {
        'answer': 'Dave Chappelle',
        'hintONE': 'i am a comedian.',
        'hintTWO': 'i was born 1973.',
        'hintTHREE': 'i have 3 children.'
    },
    {
        'answer': 'Tupac Shakur',
        'hintONE': 'i died in 1996.',
        'hintTWO': 'i was a rapper.',
        'hintTHREE': 'i was born in New York.'
    },
    {
        'answer': 'Spike Lee',
        'hintONE': 'i am a film producer.',
        'hintTWO': 'i was born in 1957',
        'hintTHREE': 'i have produced over 35 films since 1983.'
    },
    {
        'answer': 'Taraji Henson',
        'hintONE': 'I am an actress',
        'hintTWO': 'I have 1 child',
        'hintTHREE': 'i played a part in the tv series called Empire'
    },
    {
        'answer': 'Will Smith',
        'hintONE': 'I am an actor',
        'hintTWO': 'i have 3 kids',
        'hintTHREE': 'i starred in the tv series call Fresh Prince Of Bel-Air'
    },
    {
        'answer': 'Michael Jordan',
        'hintONE': 'i was an NBA player',
        'hintTWO': 'i have a famous shoe-line',
        'hintTHREE': 'i was born in 1963'
    },
    {
        'answer': 'Michael Jackson',
        'hintONE': 'i was born in 1958',
        'hintTWO': 'i was called the king of pop',
        'hintTHREE': 'i was a famous singer and dancer'
    },
    {
        'answer': 'Quincy Jones',
        'hintONE': 'i was born in 1933',
        'hintTWO': 'i have worked with people such as Michael Jackson and Bob Russell',
        'hintTHREE': 'i am a record procuder, arranger and composer'
    },
    {
        'answer': 'Jimi Hendrix',
        'hintONE': 'i was born in 1942',
        'hintTWO': 'i died at 27',
        'hintTHREE': 'i was a rock guitarist, singer, and songwriter'
    },
    {
        'answer': 'Kanye West',
        'hintONE': 'i was born in 1977',
        'hintTWO': 'i am a recording artist, songwriter, record producer, fashion designer, and entrepreneur',
        'hintTHREE': 'i got married in 2014'
    },

    #
    {
        'answer': 'You',
        'hintONE': 'i am currently looking at a screen.',
        'hintTWO': 'i am not dead',
        'hintTHREE': 'i am a person'
    },
]

# ---

def selectRandomChoice():
    return random.choice(options)

# ---
