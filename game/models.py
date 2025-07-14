from django.db import models
import uuid
from django.utils import timezone


class GameSession(models.Model):
    """Model to track game sessions and player credits."""
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    credits = models.IntegerField(default=10)
    account_credits = models.IntegerField(default=0)  # Credits that have been cashed out
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Session {self.session_id} - Credits: {self.credits}"
    
    def can_play(self):
        """Check if player has enough credits to play."""
        return self.credits >= 1
    
    def deduct_credit(self):
        """Deduct one credit for playing."""
        if self.can_play():
            self.credits -= 1
            self.save()
            return True
        return False
    
    def add_credits(self, amount):
        """Add credits from winning."""
        self.credits += amount
        self.save()
    
    def cash_out(self):
        """Move credits to account and close session."""
        self.account_credits += self.credits
        self.credits = 0
        self.is_active = False
        self.save()
        return self.account_credits


class GameRoll(models.Model):
    """Model to track individual game rolls for auditing."""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    symbols = models.JSONField()  # Store the 3 symbols as JSON
    credits_before = models.IntegerField()
    credits_after = models.IntegerField()
    credits_won = models.IntegerField(default=0)
    was_winning_roll = models.BooleanField(default=False)
    was_rerolled = models.BooleanField(default=False)  # Track if server cheated
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Roll {self.id} - Session {self.session.session_id} - {self.symbols}"
