from django.shortcuts import render
from .models import Fixture, Team
from datetime import date 

def home(request):
    """Homepage displaying fixtures, results, and standings."""
    from datetime import date
    today = date.today()

    # Retrieve teams ordered by standings criteria
    standings = Team.objects.all().order_by(
        '-points',  # Highest points first
        '-goal_difference',  # Highest GD
        'goals_scored_against',  # Fewest goals conceded first
        '-goals_scored'  # Most goals scored next
    )

    # Assign position numbers
    for index, team in enumerate(standings, start=1):
        team.pos = index  # Assign position

    # Fetch recent matches and upcoming fixtures
    recent_matches = Fixture.objects.filter(played=True).order_by('-match_date')[:5]
    upcoming_fixtures = Fixture.objects.filter(played=False, match_date__gte=today).order_by('match_date')

    context = {
        'recent_matches': recent_matches,
        'standings': standings,
        'fixtures': upcoming_fixtures
    }
    return render(request, 'league_management/home.html', context)

