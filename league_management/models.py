from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    points = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)  # Total goals scored
    goals_against = models.IntegerField(default=0)  # Total goals conceded
    goals_scored = models.IntegerField(default=0)  # Used for ranking ties
    goals_scored_against = models.IntegerField(default=0)  # Used for ranking ties
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
    match_date = models.DateField()
    played = models.BooleanField(default=False)
    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date}"

    def save(self, *args, **kwargs):
        """Automatically update team standings when results are added."""
        super().save(*args, **kwargs)
        if self.played:
            self.update_team_standings()

    def update_team_standings(self):
        """Updates team standings based on match results."""
        if self.played and self.home_score is not None and self.away_score is not None:
            home_team = self.home_team
            away_team = self.away_team

            # Update total goals
            home_team.goals_for += self.home_score
            home_team.goals_against += self.away_score
            away_team.goals_for += self.away_score
            away_team.goals_against += self.home_score

            # Update goals for tie-breaking criteria
            home_team.goals_scored += self.home_score
            away_team.goals_scored += self.away_score

            home_team.goals_scored_against += self.away_score
            away_team.goals_scored_against += self.home_score

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