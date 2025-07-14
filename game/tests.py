from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch
from .models import GameSession, GameRoll
from .views import should_server_cheat, check_winning_combination, generate_roll, generate_losing_roll


class GameSessionModelTest(TestCase):
    """Test the GameSession model functionality."""
    
    def setUp(self):
        self.session = GameSession.objects.create()
    
    def test_session_creation(self):
        """Test that a new session is created with correct defaults."""
        self.assertEqual(self.session.credits, 10)
        self.assertEqual(self.session.account_credits, 0)
        self.assertTrue(self.session.is_active)
        self.assertTrue(self.session.can_play())
    
    def test_deduct_credit(self):
        """Test credit deduction functionality."""
        initial_credits = self.session.credits
        result = self.session.deduct_credit()
        
        self.assertTrue(result)
        self.assertEqual(self.session.credits, initial_credits - 1)
    
    def test_deduct_credit_insufficient_funds(self):
        """Test that deduction fails when insufficient credits."""
        self.session.credits = 0
        self.session.save()
        
        result = self.session.deduct_credit()
        self.assertFalse(result)
        self.assertEqual(self.session.credits, 0)
    
    def test_add_credits(self):
        """Test adding credits to session."""
        initial_credits = self.session.credits
        self.session.add_credits(20)
        
        self.assertEqual(self.session.credits, initial_credits + 20)
    
    def test_cash_out(self):
        """Test cash out functionality."""
        self.session.credits = 25
        self.session.save()
        
        total_account_credits = self.session.cash_out()
        
        self.assertEqual(total_account_credits, 25)
        self.assertEqual(self.session.credits, 0)
        self.assertEqual(self.session.account_credits, 25)
        self.assertFalse(self.session.is_active)


class GameLogicTest(TestCase):
    """Test game logic functions."""
    
    def test_check_winning_combination_true(self):
        """Test winning combination detection."""
        winning_symbols = ['cherry', 'cherry', 'cherry']
        self.assertTrue(check_winning_combination(winning_symbols))
    
    def test_check_winning_combination_false(self):
        """Test losing combination detection."""
        losing_symbols = ['cherry', 'lemon', 'cherry']
        self.assertFalse(check_winning_combination(losing_symbols))
    
    def test_generate_roll(self):
        """Test roll generation returns valid symbols."""
        symbols = generate_roll()
        valid_symbols = ['cherry', 'lemon', 'orange', 'watermelon']
        
        self.assertEqual(len(symbols), 3)
        for symbol in symbols:
            self.assertIn(symbol, valid_symbols)
    
    def test_generate_losing_roll(self):
        """Test that generate_losing_roll never produces winning combinations."""
        for _ in range(100):  # Test multiple times due to randomness
            symbols = generate_losing_roll()
            self.assertFalse(check_winning_combination(symbols))
    
    def test_should_server_cheat_low_credits(self):
        """Test no cheating when credits are low."""
        # Test with credits that would result in less than 40 total
        result = should_server_cheat(30, 5)  # 35 total
        self.assertFalse(result)
    
    @patch('random.random')
    def test_should_server_cheat_medium_credits(self, mock_random):
        """Test 30% cheating chance for medium credits."""
        # Test when random returns 0.2 (less than 0.3)
        mock_random.return_value = 0.2
        result = should_server_cheat(35, 10)  # 45 total (40-60 range)
        self.assertTrue(result)
        
        # Test when random returns 0.4 (greater than 0.3)
        mock_random.return_value = 0.4
        result = should_server_cheat(35, 10)  # 45 total
        self.assertFalse(result)
    
    @patch('random.random')
    def test_should_server_cheat_high_credits(self, mock_random):
        """Test 60% cheating chance for high credits."""
        # Test when random returns 0.5 (less than 0.6)
        mock_random.return_value = 0.5
        result = should_server_cheat(55, 10)  # 65 total (>60)
        self.assertTrue(result)
        
        # Test when random returns 0.7 (greater than 0.6)
        mock_random.return_value = 0.7
        result = should_server_cheat(55, 10)  # 65 total
        self.assertFalse(result)


class GameViewsTest(TestCase):
    """Test game views and API endpoints."""
    
    def setUp(self):
        self.client = Client()
    
    def test_index_view(self):
        """Test that the main game page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las Vegas Slots')
    
    def test_create_session_api(self):
        """Test session creation API."""
        response = self.client.post('/api/create-session/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('session_id', data)
        self.assertEqual(data['credits'], 10)
        self.assertEqual(data['account_credits'], 0)
    
    def test_roll_slots_api(self):
        """Test slot rolling API."""
        # Create a session first
        session = GameSession.objects.create()
        
        response = self.client.post('/api/roll/', 
            data=json.dumps({'session_id': str(session.session_id)}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('symbols', data)
        self.assertIn('symbols_display', data)
        self.assertIn('is_winning', data)
        self.assertIn('total_credits', data)
        self.assertEqual(len(data['symbols']), 3)
        self.assertEqual(len(data['symbols_display']), 3)
    
    def test_roll_slots_insufficient_credits(self):
        """Test rolling with insufficient credits."""
        session = GameSession.objects.create(credits=0)
        
        response = self.client.post('/api/roll/',
            data=json.dumps({'session_id': str(session.session_id)}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_cash_out_api(self):
        """Test cash out API."""
        session = GameSession.objects.create(credits=25)
        
        response = self.client.post('/api/cash-out/',
            data=json.dumps({'session_id': str(session.session_id)}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['total_account_credits'], 25)
        
        # Verify session state
        session.refresh_from_db()
        self.assertEqual(session.credits, 0)
        self.assertFalse(session.is_active)
    
    def test_get_session_status_api(self):
        """Test session status API."""
        session = GameSession.objects.create()
        
        response = self.client.get(f'/api/session/{session.session_id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['credits'], 10)
        self.assertTrue(data['is_active'])
        self.assertTrue(data['can_play'])


class GameRollModelTest(TestCase):
    """Test the GameRoll model functionality."""
    
    def setUp(self):
        self.session = GameSession.objects.create()
    
    def test_roll_creation(self):
        """Test that game rolls are created correctly."""
        roll = GameRoll.objects.create(
            session=self.session,
            symbols=['cherry', 'cherry', 'cherry'],
            credits_before=10,
            credits_after=20,
            credits_won=10,
            was_winning_roll=True,
            was_rerolled=False
        )
        
        self.assertEqual(roll.session, self.session)
        self.assertEqual(roll.symbols, ['cherry', 'cherry', 'cherry'])
        self.assertTrue(roll.was_winning_roll)
        self.assertFalse(roll.was_rerolled)


class IntegrationTest(TestCase):
    """Test complete game flow integration."""
    
    def test_complete_game_flow(self):
        """Test a complete game session from start to cash out."""
        client = Client()
        
        # Create session
        response = client.post('/api/create-session/')
        session_data = json.loads(response.content)
        session_id = session_data['session_id']
        
        # Play a few rounds
        for _ in range(3):
            response = client.post('/api/roll/',
                data=json.dumps({'session_id': session_id}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Check session status
        response = client.get(f'/api/session/{session_id}/')
        self.assertEqual(response.status_code, 200)
        
        # Cash out
        response = client.post('/api/cash-out/',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify session is closed
        session = GameSession.objects.get(session_id=session_id)
        self.assertFalse(session.is_active)
        self.assertEqual(session.credits, 0)
