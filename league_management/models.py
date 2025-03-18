from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    
    points = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)  # Total goals scored
    goals_against = models.IntegerField(default=0)  # Total goals conceded
    goal_difference = models.IntegerField(default=0)
    
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_standings(self):
        """Recalculates and updates team standings."""
        self.goal_difference = self.goals_for - self.goals_against
        self.save()

class Fixture(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')
    stadium = models.CharField(max_length=255, default="Main Stadium")
    match_date = models.DateTimeField()
    kickoff_time = models.TimeField(default="08:00:00")
    played = models.BooleanField(default=False)
    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date} {self.kickoff_time} at {self.stadium}"

    def clean(self):
        """Ensure that a team cannot play against itself."""
        if self.home_team == self.away_team:
            raise ValidationError("A team cannot play against itself.")

    def save(self, *args, **kwargs):
        """Update standings when a match is marked as played or edited."""
        if self.pk:
            previous_fixture = Fixture.objects.get(pk=self.pk)
            already_played = previous_fixture.played
        else:
            already_played = False  # New fixture

        super().save(*args, **kwargs)

        if not already_played and self.played:
            self.update_team_standings()
        elif already_played and self.played:  # If the fixture was already played but got updated
            self.recalculate_team_standings(previous_fixture)

    def update_team_standings(self):
        """Updates team standings when a match is played."""
        if not self.played or self.home_score is None or self.away_score is None:
            return  

        home_team, away_team = self.home_team, self.away_team

        # Update goals
        home_team.goals_for += self.home_score
        home_team.goals_against += self.away_score
        away_team.goals_for += self.away_score
        away_team.goals_against += self.home_score

        # Update matches played
        home_team.matches_played += 1
        away_team.matches_played += 1

        # Update points
        if self.home_score > self.away_score:
            home_team.points += 3
            home_team.wins += 1
            away_team.losses += 1
        elif self.home_score < self.away_score:
            away_team.points += 3
            away_team.wins += 1
            home_team.losses += 1
        else:
            home_team.points += 1
            away_team.points += 1
            home_team.draws += 1
            away_team.draws += 1

        # Save changes
        home_team.update_standings()
        away_team.update_standings()

    def recalculate_team_standings(self, previous_fixture):
        """Undo previous match results and apply new results if scores were edited."""
        home_team, away_team = self.home_team, self.away_team

        # Revert previous match stats
        home_team.goals_for -= previous_fixture.home_score
        home_team.goals_against -= previous_fixture.away_score
        away_team.goals_for -= previous_fixture.away_score
        away_team.goals_against -= previous_fixture.home_score

        home_team.matches_played -= 1
        away_team.matches_played -= 1

        # Reset points
        if previous_fixture.home_score > previous_fixture.away_score:
            home_team.points -= 3
            home_team.wins -= 1
            away_team.losses -= 1
        elif previous_fixture.home_score < previous_fixture.away_score:
            away_team.points -= 3
            away_team.wins -= 1
            home_team.losses -= 1
        else:
            home_team.points -= 1
            away_team.points -= 1
            home_team.draws -= 1
            away_team.draws -= 1

        # Apply new results
        self.update_team_standings()

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class MatchEvent(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name="events")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event_type = models.CharField(
        max_length=20,
        choices=[("goal", "Goal"), ("assist", "Assist"), ("yellow_card", "Yellow Card"), ("red_card", "Red Card")]
    )
    timestamp = models.TimeField()

    def __str__(self):
        return f"{self.player.name} - {self.event_type} in {self.fixture}"

    def save(self, *args, **kwargs):
        """Automatically update player stats when an event is created."""
        super().save(*args, **kwargs)

        if self.event_type == "goal":
            self.player.goals += 1
        elif self.event_type == "assist":
            self.player.assists += 1
        self.player.save()

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="news_images/", blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
