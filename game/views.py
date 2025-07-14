from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
from .models import GameSession, GameRoll


# Symbol configuration
SYMBOLS = {
    'cherry': {'letter': 'C', 'reward': 10},
    'lemon': {'letter': 'L', 'reward': 20},
    'orange': {'letter': 'O', 'reward': 30},
    'watermelon': {'letter': 'W', 'reward': 40},
}

SYMBOL_NAMES = list(SYMBOLS.keys())


def index(request):
    """Main game page."""
    return render(request, 'game/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """Create a new game session."""
    session = GameSession.objects.create()
    return JsonResponse({
        'session_id': str(session.session_id),
        'credits': session.credits,
        'account_credits': session.account_credits
    })


@csrf_exempt
@require_http_methods(["POST"])
def roll_slots(request):
    """Handle slot machine roll with server-side cheating logic."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(GameSession, session_id=session_id, is_active=True)
        
        if not session.can_play():
            return JsonResponse({'error': 'Not enough credits'}, status=400)
        
        # Deduct credit for playing
        credits_before = session.credits
        session.deduct_credit()
        
        # Generate initial roll
        symbols = generate_roll()
        is_winning = check_winning_combination(symbols)
        credits_won = 0
        was_rerolled = False
        
        if is_winning:
            credits_won = SYMBOLS[symbols[0]]['reward']
            
            # Server-side cheating logic
            should_reroll = should_server_cheat(session.credits, credits_won)
            
            if should_reroll:
                # Re-roll to prevent winning
                symbols = generate_losing_roll()
                is_winning = False
                credits_won = 0
                was_rerolled = True
        
        # Update session credits
        if is_winning:
            session.add_credits(credits_won)
        
        # Record the roll
        roll = GameRoll.objects.create(
            session=session,
            symbols=symbols,
            credits_before=credits_before,
            credits_after=session.credits,
            credits_won=credits_won,
            was_winning_roll=is_winning,
            was_rerolled=was_rerolled
        )
        
        return JsonResponse({
            'symbols': symbols,
            'symbols_display': [SYMBOLS[symbol]['letter'] for symbol in symbols],
            'is_winning': is_winning,
            'credits_won': credits_won,
            'total_credits': session.credits,
            'was_rerolled': was_rerolled  # For debugging/testing
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cash_out(request):
    """Handle cash out functionality."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(GameSession, session_id=session_id, is_active=True)
        
        total_account_credits = session.cash_out()
        
        return JsonResponse({
            'success': True,
            'total_account_credits': total_account_credits,
            'message': f'Successfully cashed out {session.credits + total_account_credits} credits!'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_session_status(request, session_id):
    """Get current session status."""
    try:
        session = get_object_or_404(GameSession, session_id=session_id)
        return JsonResponse({
            'session_id': str(session.session_id),
            'credits': session.credits,
            'account_credits': session.account_credits,
            'is_active': session.is_active,
            'can_play': session.can_play()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper functions
def generate_roll():
    """Generate a random combination of 3 symbols."""
    return [random.choice(SYMBOL_NAMES) for _ in range(3)]


def generate_losing_roll():
    """Generate a guaranteed losing combination."""
    # Ensure at least one symbol is different
    symbols = [random.choice(SYMBOL_NAMES) for _ in range(3)]
    
    # If by chance it's a winning combination, make it losing
    if len(set(symbols)) == 1:
        # Change the last symbol to something different
        available_symbols = [s for s in SYMBOL_NAMES if s != symbols[0]]
        symbols[2] = random.choice(available_symbols)
    
    return symbols


def check_winning_combination(symbols):
    """Check if all three symbols are the same."""
    return len(set(symbols)) == 1


def should_server_cheat(current_credits, potential_win_credits):
    """
    Determine if server should cheat based on current credits.
    
    - Less than 40 credits: No cheating (0% chance)
    - 40-60 credits: 30% chance to re-roll winning combinations
    - Above 60 credits: 60% chance to re-roll winning combinations
    """
    future_credits = current_credits + potential_win_credits
    
    if future_credits < 40:
        return False
    elif 40 <= future_credits <= 60:
        return random.random() < 0.3  # 30% chance
    else:  # future_credits > 60
        return random.random() < 0.6  # 60% chance
