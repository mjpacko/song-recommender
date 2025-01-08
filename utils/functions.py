def scrape_billboard_hot_100():
    url = "https://www.billboard.com/charts/hot-100/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    song_titles = []
    artists = []
    positions = []

    # Find all list items containing chart entries
    chart_items = soup.select('ul.o-chart-results-list-row')

    for item in chart_items:
        # Extract position
        position = item.select_one('span.c-label.a-font-primary-bold-l').text.strip()
    
        # Extract title
        title = item.select_one('h3#title-of-a-story').text.strip()
    
        # Extract artist - it's usually in the span following the title
        artist = item.select_one('span.c-label.a-no-trucate').text.strip()
    
        positions.append(position)
        song_titles.append(title)
        artists.append(artist)

    # Create a DataFrame
    hot100_df = pd.DataFrame({
        'Position': positions,
        'Song Title': song_titles,
        'Artist': artists
    })
    return hot100_df