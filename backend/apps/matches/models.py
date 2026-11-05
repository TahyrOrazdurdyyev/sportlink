"""
Match result models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User
from apps.bookings.models import Booking
from apps.tournaments.models import Tournament


class MatchResult(Document):
    """Match result/score model for MongoDB"""
    
    MATCH_TYPE_CHOICES = [
        ('booking', 'Court Booking Match'),
        ('tournament', 'Tournament Match'),
        ('friendly', 'Friendly Match'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Match reference
    booking = fields.ReferenceField(Booking, reverse_delete_rule=2)  # NULLIFY
    tournament = fields.ReferenceField(Tournament, reverse_delete_rule=2)  # NULLIFY
    match_type = fields.StringField(choices=MATCH_TYPE_CHOICES, required=True)
    
    # Match ID (for tournament bracket system)
    match_id = fields.StringField()  # Custom match identifier
    
    # Players/Teams
    players = fields.ListField(fields.ReferenceField(User))  # All players involved
    team_1_players = fields.ListField(fields.ReferenceField(User))
    team_2_players = fields.ListField(fields.ReferenceField(User))
    
    # Score data (flexible JSON structure)
    score_data = fields.DictField(default=dict)
    # Example structure:
    # {
    #   "sets": [
    #     {"team_1": 6, "team_2": 4},
    #     {"team_1": 6, "team_2": 3}
    #   ],
    #   "games": {
    #     "set_1": [{"team_1": 1, "team_2": 0}, ...],
    #     "set_2": [...]
    #   },
    #   "winner": "team_1",
    #   "match_duration_minutes": 90
    # }
    
    # Winner
    winning_team = fields.StringField(choices=['team_1', 'team_2', 'draw'])
    winner_players = fields.ListField(fields.ReferenceField(User))
    
    # Match details
    duration_minutes = fields.IntField(min_value=0)
    completed = fields.BooleanField(default=False)
    
    # Recording info
    recorded_by = fields.ReferenceField(User, required=True, reverse_delete_rule=2)  # NULLIFY
    verified = fields.BooleanField(default=False)
    verified_by = fields.ReferenceField(User, reverse_delete_rule=2)  # NULLIFY
    
    # Additional info
    notes = fields.StringField(max_length=1000)
    video_url = fields.URLField()  # Link to match video
    photos = fields.ListField(fields.URLField())  # Match photos
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    match_date = fields.DateTimeField()  # Actual match date/time
    
    meta = {
        'collection': 'match_results',
        'indexes': [
            'booking',
            'tournament',
            'match_type',
            'recorded_by',
            'verified',
            'completed',
            'match_date',
            'created_at',
            'players',  # For player statistics
            'winner_players',  # For winner statistics
        ]
    }
    
    def __str__(self):
        return f"Match {self.id} - {self.get_match_summary()}"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def get_match_summary(self):
        """Get a brief match summary"""
        if self.team_1_players and self.team_2_players:
            team_1_names = [p.first_name for p in self.team_1_players if p.first_name]
            team_2_names = [p.first_name for p in self.team_2_players if p.first_name]
            
            team_1_str = " & ".join(team_1_names[:2])  # Show max 2 names
            team_2_str = " & ".join(team_2_names[:2])
            
            return f"{team_1_str} vs {team_2_str}"
        
        return f"Match {self.match_id or ''}"
    
    def get_score_summary(self):
        """Get a brief score summary"""
        if not self.score_data or 'sets' not in self.score_data:
            return ""
        
        sets = self.score_data['sets']
        score_parts = []
        
        for set_score in sets:
            team_1_score = set_score.get('team_1', 0)
            team_2_score = set_score.get('team_2', 0)
            score_parts.append(f"{team_1_score}-{team_2_score}")
        
        return ", ".join(score_parts)
    
    def calculate_winner(self):
        """Automatically calculate winner from score data"""
        if not self.score_data or 'sets' not in self.score_data:
            return None
        
        sets = self.score_data['sets']
        team_1_sets = 0
        team_2_sets = 0
        
        for set_score in sets:
            team_1_score = set_score.get('team_1', 0)
            team_2_score = set_score.get('team_2', 0)
            
            if team_1_score > team_2_score:
                team_1_sets += 1
            elif team_2_score > team_1_score:
                team_2_sets += 1
        
        if team_1_sets > team_2_sets:
            self.winning_team = 'team_1'
            self.winner_players = list(self.team_1_players)
        elif team_2_sets > team_1_sets:
            self.winning_team = 'team_2'
            self.winner_players = list(self.team_2_players)
        else:
            self.winning_team = 'draw'
            self.winner_players = []
        
        return self.winning_team
    
    def mark_completed(self):
        """Mark match as completed"""
        self.completed = True
        if not self.match_date:
            self.match_date = datetime.utcnow()
        self.calculate_winner()
        self.save()
    
    def verify(self, verified_by_user):
        """Verify the match result"""
        self.verified = True
        self.verified_by = verified_by_user
        self.save()
