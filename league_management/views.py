from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from operator import attrgetter
from itertools import groupby
from .models import Fixture, Team, Player, MatchEvent, News
from datetime import date, datetime
from django.utils.timezone import localtime, localdate

def get_standings():
    """Returns ordered team standings with position numbers."""
    standings = Team.objects.all().order_by(
        '-points', '-goal_difference', '-goals_for', 'goals_against', 'name'
    )
    for index, team in enumerate(standings, start=1):
        team.pos = index  # Assign position
    return standings

def get_top_scorers():
    """Returns a list of top scorers based on goals scored and assists."""
    return Player.objects.annotate(
        total_goals=Sum("goals"),
        total_assists=Sum("assists")
    ).order_by("-total_goals", "-total_assists")[:10]  # Limit to top 10 scorers

def home(request):
    """Homepage displaying fixtures, results, standings, and news."""
    today = localdate()
    teams = Team.objects.all().order_by("name")

    # Fetch standings and top scorers
    standings = get_standings()
    top_scorers = get_top_scorers()

    # Fetch recent matches (last 5 played matches)
    recent_matches = Fixture.objects.filter(played=True).order_by('-match_date')[:5]

    # Get the next match day (first unplayed fixture)
    next_matchday = Fixture.objects.filter(played=False, match_date__gte=today).order_by('match_date').first()
    
    # Fetch fixtures for the next match day
    upcoming_fixtures = []
    stadium_name = "Stima club"  # Default stadium name

    if next_matchday:
        match_date = localtime(next_matchday.match_date).date()
        upcoming_fixtures = list(Fixture.objects.filter(
            played=False,
            match_date__date=match_date  # Get all fixtures on this day
        ).order_by('match_date'))

        if upcoming_fixtures:
            stadium_name = upcoming_fixtures[0].stadium

    # Fetch latest 3 news articles
    latest_news = News.objects.order_by('-created_at')[:3]

    # Select the main news article
    main_news = latest_news[0] if latest_news else None
    side_news = latest_news[1:3] if len(latest_news) > 1 else []

    # Group fixtures by match date
    grouped_fixtures = {
        match_date: list(fixtures)
        for match_date, fixtures in groupby(upcoming_fixtures, key=attrgetter('match_date'))
    }

    context = {
        
        'recent_matches': recent_matches,
        'standings': standings,
        'grouped_fixtures': grouped_fixtures,
        'upcoming_fixtures': upcoming_fixtures,
        'stadium_name': stadium_name,
        'teams': teams,
        'top_scorers': top_scorers,
        'main_news': main_news,
        'side_news': side_news,
    }

    return render(request, 'league_management/home.html', context)

def league_tables(request):
    """Displays league tables and top scorers."""
    standings = get_standings()
    top_scorers = get_top_scorers()
    teams = Team.objects.all().order_by("name")

    context = {
        "standings": standings,
        "top_scorers": top_scorers,
        "teams": teams,
    }
    return render(request, "league_management/tables.html", context)

def fixtures_page(request):
    """Display fixtures grouped by match day."""
    today = date.today()
    
    # Fetch all fixtures from today onward, sorted by match date
    fixtures = Fixture.objects.filter(match_date__gte=today).order_by("match_date")
    
    # Group fixtures by match day
    fixture_groups = {}
    for fixture in fixtures:
        match_day = fixture.match_date.strftime("%A %d %B %Y") if fixture.match_date else "Date Not Set"
        fixture_groups.setdefault(match_day, []).append(fixture)

    context = {
        "fixture_groups": fixture_groups,
        "teams": Team.objects.all().order_by("name"),
    }
    return render(request, "league_management/fixtures.html", context)

def results_page(request):
    """Display match results grouped by match day."""
    teams = Team.objects.all().order_by("name")

    # Fetch played matches sorted by match_date
    results = Fixture.objects.filter(played=True).order_by("-match_date")

    # Group results by match day
    result_groups = {}
    for match in results:
        match_month = match.match_date.strftime("%B %Y")  # Example: "March 2025"
        result_groups.setdefault(match_month, []).append(match)

    context = {
        "result_groups": result_groups,
        "teams": teams,
    }
    return render(request, "league_management/results.html", context)

def teams_list(request):
    """Display all teams in a grid format."""
    teams = Team.objects.all().order_by("name")
    context = {"teams": teams}
    return render(request, "league_management/teams.html", context)

def news_page(request):
    """Display all news articles."""
    news_articles = News.objects.all().order_by('-created_at')
    teams = Team.objects.all().order_by("name")

    context = {
        "news_articles": news_articles,
        "teams": teams,
    }
    return render(request, "league_management/news.html", context)

def news_detail(request, news_id):
    """Display details of a single news article."""
    article = get_object_or_404(News, id=news_id)
    return render(request, "league_management/news_detail.html", {"article": article})
